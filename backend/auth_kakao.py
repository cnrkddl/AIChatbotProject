# backend/auth_kakao.py
import os
from typing import Optional
from urllib.parse import quote, unquote

import requests
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

# =========================
# kakao_oauth 모듈 (동일 디렉토리에 존재 가정)
# - build_authorize_url(scope: str) -> str
# - exchange_token(code: str) -> dict
# - get_user_profile(access_token: str) -> dict
# =========================
try:
    from kakao_oauth import (
        build_authorize_url,
        exchange_token,
        get_user_profile,
    )
except ImportError:
    # 패키지 구조가 달라도 동일 이름으로 임포트 시도
    from kakao_oauth import (  # type: ignore
        build_authorize_url,
        exchange_token,
        get_user_profile,
    )

# =========================
# 환경 변수
# =========================
# 프론트엔드 배포 베이스 URL (GitHub Pages 등)
FRONTEND_BASE = os.getenv("FRONTEND_BASE", "http://localhost:3000").rstrip("/")
# Hash Router 사용 여부 (CRA의 HashRouter 사용 시 True)
USE_HASH_ROUTER = os.getenv("USE_HASH_ROUTER", "true").lower() == "true"

# 카카오 Admin 키(선택): access_token 없이 unlink가 필요할 때 사용
KAKAO_ADMIN_KEY = os.getenv("KAKAO_ADMIN_KEY", "").strip()

# 쿠키 정책(로컬/배포 전환 시 유용)
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN") or None  # 예: ".onrender.com" 또는 None
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() == "true"  # 배포면 True 권장
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "none").lower()  # "lax"|"strict"|"none"

# 기본 리다이렉트 경로 (?login=success 감지용)
DEFAULT_FRONT_PATH = "/?login=success"

# 카카오 API 베이스
KAKAO_API_BASE = "https://kapi.kakao.com"

# 라우터 (최종 경로는 /auth/kakao/...)
router = APIRouter(prefix="/auth/kakao", tags=["kakao"])


# =========================
# Helper: 프론트 URL 빌드 (HashRouter 대응)
# =========================
def _front_join(path: str) -> str:
    """
    FRONTEND_BASE + path 조합.
    Hash Router 사용 시 '/#/path' 형태로 조립.
    """
    if not path:
        path = "/"
    if USE_HASH_ROUTER:
        # 이미 /#/ 로 시작하지 않으면 강제로 붙여줌
        if path.startswith("/#/"):
            return f"{FRONTEND_BASE}{path}"
        # path가 '/'로 시작하도록 보정
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{FRONTEND_BASE}/#{path}"
    else:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{FRONTEND_BASE}{path}"


def _build_front_url(next_param: Optional[str]) -> str:
    """
    state/next 파라미터를 안전하게 프론트 URL로 변환.
    - 절대 URL이면 그대로 사용
    - '/'로 시작하면 프론트 베이스에 합치기
    - 비어있으면 기본 경로(?login=success)
    """
    if not next_param:
        return _front_join(DEFAULT_FRONT_PATH)

    decoded = unquote(next_param)
    if decoded.startswith(("http://", "https://")):
        return decoded
    if decoded.startswith("/"):
        return _front_join(decoded)
    return _front_join(f"/{decoded}")


def _append_query(url: str, key: str, value: str) -> str:
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{key}={quote(value, safe='')}"


# =========================
# Helper: 쿠키 set/del
# =========================
def set_cookie(resp, key, value, *, max_age=60 * 60 * 8, http_only=True):
    resp.set_cookie(
        key=key,
        value=value,
        max_age=max_age,
        httponly=http_only,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,  # "none"일 경우 secure=True 필요
        domain=COOKIE_DOMAIN,
        path="/",
    )


def del_cookie(resp, key: str):
    # FastAPI Response.delete_cookie 에서도 동일 파라미터 맞춰 삭제
    resp.delete_cookie(
        key=key,
        domain=COOKIE_DOMAIN,
        path="/",
        samesite=COOKIE_SAMESITE if COOKIE_SAMESITE in ("lax", "strict") else "none",
    )


# =========================
# 1) 로그인 시작
# =========================
@router.get("/login")
def login(scope: Optional[str] = "profile_nickname,account_email", next: Optional[str] = None):
    """
    카카오 인가 페이지로 리다이렉트.
    state 에 front로 돌아갈 next URL을 넣어 둔다.
    """
    authorize_base = build_authorize_url(scope=scope or "")
    next_url = _build_front_url(next)
    authorize_url = f"{authorize_base}&state={quote(next_url, safe='')}"
    return RedirectResponse(authorize_url, status_code=307)


# =========================
# 2) 카카오 콜백
# =========================
@router.get("/callback")
def callback(code: Optional[str] = None, state: Optional[str] = None):
    if not code:
        raise HTTPException(status_code=400, detail="missing authorization code")

    try:
        token_json = exchange_token(code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"token exchange error: {e}")

    access_token = token_json.get("access_token")
    refresh_token = token_json.get("refresh_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="no access_token from kakao")

    # 유저 프로필
    nickname = None
    email = None
    kakao_uid = None
    profile_image = None

    try:
        profile = get_user_profile(access_token) or {}
        kakao_uid = str(profile.get("id") or "")
        kakao_account = profile.get("kakao_account") or {}
        email = kakao_account.get("email") or None
        prof_obj = kakao_account.get("profile") or {}
        nickname = prof_obj.get("nickname") or None
        profile_image = prof_obj.get("profile_image_url") or None
    except Exception:
        # 프로필 조회 실패는 로그인 자체 실패가 아님
        pass

    # 프론트 이동 URL
    next_url = state or _build_front_url(DEFAULT_FRONT_PATH)

    # ?login=success 보장
    if ("login=success" not in next_url) and ("login%3Dsuccess" not in next_url):
        next_url = _append_query(next_url, "login", "success")

    # nickname / email 을 프론트로 넘기고 싶다면 쿼리로도 전달 가능(선택)
    if nickname and "nickname=" not in next_url:
        next_url = _append_query(next_url, "nickname", nickname)
    if email and "email=" not in next_url:
        next_url = _append_query(next_url, "email", email)

    # 쿠키 세팅
    resp = RedirectResponse(next_url, status_code=307)
    set_cookie(resp, "k_at", access_token, max_age=60 * 60 * 8, http_only=True)  # 8h
    if refresh_token:
        set_cookie(resp, "k_rt", refresh_token, max_age=60 * 60 * 24 * 30, http_only=True)
    if kakao_uid:
        set_cookie(resp, "k_uid", kakao_uid, max_age=60 * 60 * 24 * 30, http_only=True)
    if email:
        set_cookie(resp, "k_email", email, max_age=60 * 60 * 24 * 30, http_only=False)  # JS에서 읽어도 되면 http_only=False
    if profile_image:
        set_cookie(resp, "k_profile", profile_image, max_age=60 * 60 * 24 * 30, http_only=False)

    return resp


# =========================
# 3) 프로필/whoami
# =========================
@router.get("/profile")
def profile(request: Request):
    """
    원본 Kakao /v2/user/me 응답을 반환(디버그/개발용)
    """
    at = request.cookies.get("k_at")
    if not at:
        return JSONResponse({"error": "not_authenticated"}, status_code=401)
    r = requests.get(f"{KAKAO_API_BASE}/v2/user/me", headers={"Authorization": f"Bearer {at}"}, timeout=10)
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text}
    return JSONResponse(body, status_code=r.status_code)


@router.get("/whoami")
def whoami(request: Request):
    """
    프론트에서 쓰기 쉬운 축약 정보
    """
    at = request.cookies.get("k_at")
    if not at:
        return JSONResponse({"logged_in": False})

    r = requests.get(f"{KAKAO_API_BASE}/v2/user/me", headers={"Authorization": f"Bearer {at}"}, timeout=8)
    if r.status_code != 200:
        return JSONResponse({"logged_in": False, "error": r.text}, status_code=401)

    prof = r.json() or {}
    kakao_account = prof.get("kakao_account") or {}
    profile = kakao_account.get("profile") or {}

    return JSONResponse(
        {
            "logged_in": True,
            "id": prof.get("id"),
            "email": kakao_account.get("email"),
            "nickname": profile.get("nickname"),
            "profile_image": profile.get("profile_image_url"),
        }
    )


# =========================
# 4) 로그아웃
# =========================
def _clear_auth_cookies(resp):
    for k in ("k_at", "k_rt", "k_uid", "k_email", "k_profile"):
        del_cookie(resp, k)


@router.post("/logout")
def logout(request: Request):
    access_token = request.cookies.get("k_at")
    resp = JSONResponse({"ok": True})
    _clear_auth_cookies(resp)

    if not access_token:
        return resp

    try:
        r = requests.post(
            f"{KAKAO_API_BASE}/v1/user/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=8,
        )
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail=f"kakao logout failed: {r.text}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"kakao logout failed: {e}")

    return resp


# (개발 편의) GET도 허용 — 운영에서는 CSRF 이유로 비권장
@router.get("/logout")
def logout_get(request: Request):
    return logout(request)


# =========================
# 5) 연결 해제 (탈퇴)
# =========================
@router.post("/unlink")
def unlink(request: Request):
    access_token = request.cookies.get("k_at")
    kakao_uid = request.cookies.get("k_uid")

    resp = JSONResponse({"ok": True})
    _clear_auth_cookies(resp)

    try:
        if access_token:
            r = requests.post(
                f"{KAKAO_API_BASE}/v1/user/unlink",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=8,
            )
        elif KAKAO_ADMIN_KEY and kakao_uid:
            # Admin Key로 유저 ID 직접 해제
            r = requests.post(
                f"{KAKAO_API_BASE}/v1/user/unlink",
                headers={"Authorization": f"KakaoAK {KAKAO_ADMIN_KEY}"},
                data={"target_id_type": "user_id", "target_id": kakao_uid},
                timeout=8,
            )
        else:
            raise HTTPException(status_code=400, detail="no token or user id to unlink")

        if r.status_code != 200:
            raise HTTPException(status_code=502, detail=f"kakao unlink failed: {r.text}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"kakao unlink failed: {e}")

    return resp


# (개발 편의) GET도 허용 — 운영에서는 CSRF 이유로 비권장
@router.get("/unlink")
def unlink_get(request: Request):
    return unlink(request)
