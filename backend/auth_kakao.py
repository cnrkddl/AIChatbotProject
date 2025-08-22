# backend/auth_kakao.py
import os
from urllib.parse import quote, unquote
from typing import Optional

import requests
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse

# ── Kakao OAuth 헬퍼 (이미 프로젝트에 존재)
from .kakao_oauth import (
    build_authorize_url,   # 인가 URL
    exchange_token,        # code -> token
    get_user_profile,      # token -> profile
    KAPI_HOST,             # https://kapi.kakao.com
)

BACKEND_BASE = os.getenv("BACKEND_BASE", "https://aichatbotproject.onrender.com").strip()
FRONTEND_BASE = os.getenv("FRONTEND_BASE", "https://cnrkddl.github.io/AIChatbotProject").strip()

USE_HASH_ROUTER = True  # GitHub Pages(HashRouter)라서 /#/ 강제

router = APIRouter()


def _front_join(path: str) -> str:
    if not path:
        path = "/"
    if USE_HASH_ROUTER:
        return f"{FRONTEND_BASE}{path if path.startswith('/#/') else f'/#{path}'}"
    return f"{FRONTEND_BASE}{path}"


def _build_front_url(next_param: Optional[str]) -> str:
    if not next_param:
        return _front_join("/?login=success")
    decoded = unquote(next_param)
    if decoded.startswith(("http://", "https://")):
        return decoded
    if decoded.startswith("/"):
        return _front_join(decoded)
    return _front_join(f"/{decoded}")


@router.get("/auth/kakao/login")
async def kakao_login(
    scope: Optional[str] = "profile_nickname,account_email",
    next: Optional[str] = "/?login=success",
):
    next_url = _build_front_url(next)
    authorize_base = build_authorize_url(scope=scope or "")
    authorize_url = f"{authorize_base}&state={quote(next_url, safe='')}"
    return RedirectResponse(authorize_url, status_code=307)


@router.get("/auth/kakao/callback")
async def kakao_callback(code: Optional[str] = None, state: Optional[str] = None):
    if not code:
        return JSONResponse({"error": "missing_code"}, status_code=400)

    try:
        token_json = exchange_token(code)
    except Exception as e:
        return JSONResponse({"error": "token_error", "detail": str(e)}, status_code=400)

    access_token = token_json.get("access_token", "")

    nickname = None
    if access_token:
        try:
            profile = get_user_profile(access_token)
            kakao_account = profile.get("kakao_account") or {}
            profile_obj = kakao_account.get("profile") or {}
            nickname = profile_obj.get("nickname")
        except Exception:
            pass

    next_url = state or _build_front_url("/?login=success")
    if "login=success" not in next_url and "login%3Dsuccess" not in next_url:
        next_url += "&" if "?" in next_url else "?"
        next_url += "login=success"
    if nickname and "nickname=" not in next_url:
        next_url += "&" if "?" in next_url else "?"
        next_url += f"nickname={quote(nickname, safe='')}"

    resp = RedirectResponse(next_url, status_code=307)
    if access_token:
        resp.set_cookie(
            key="kakao_access_token",
            value=access_token,
            max_age=60 * 60 * 6,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
        )
    return resp


@router.get("/profile")
async def profile(request: Request):
    token = request.cookies.get("kakao_access_token")
    if not token:
        return JSONResponse({"error": "not_authenticated"}, status_code=401)
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{KAPI_HOST}/v2/user/me", headers=headers, timeout=10)
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text}
    return JSONResponse(body, status_code=r.status_code)


@router.get("/logout")
async def logout(request: Request):
    """
    카카오 로그아웃 호출 + 우리 측 쿠키 삭제.
    프론트에서는 호출 후 로컬 상태 초기화하고 '#/'로 보내면 끝.
    """
    token = request.cookies.get("kakao_access_token")
    if token:
        try:
            requests.post(
                f"{KAPI_HOST}/v1/user/logout",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
        except Exception:
            pass
    res = JSONResponse({"ok": True})
    res.delete_cookie("kakao_access_token", path="/")
    return res


@router.get("/unlink")
async def unlink(request: Request):
    """
    카카오 앱 연결 해제(회원탈퇴 성격).
    """
    token = request.cookies.get("kakao_access_token")
    if not token:
        return JSONResponse({"error": "not_authenticated"}, status_code=401)
    r = requests.post(
        f"{KAPI_HOST}/v1/user/unlink",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text}
    res = JSONResponse({"ok": r.status_code == 200, "kakao": body}, status_code=(200 if r.status_code == 200 else r.status_code))
    res.delete_cookie("kakao_access_token", path="/")
    return res
