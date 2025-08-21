# backend/kakao_oauth.py
import os
from urllib.parse import urljoin, unquote
import requests
from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse, JSONResponse

router = APIRouter()

# ---- 환경변수 ----
CLIENT_ID = os.getenv("KAKAO_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "").strip()   # 콘솔 '사용'일 때만 쓸 것
BACKEND_BASE = os.getenv("BACKEND_BASE", "https://aichatbotproject.onrender.com").strip()
FRONTEND_BASE = os.getenv("FRONTEND_BASE", "https://cnrkddl.github.io/AIChatbotProject").strip()
REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", f"{BACKEND_BASE}/auth/kakao/callback").strip()

KAUTH_HOST = "https://kauth.kakao.com"
KAPI_HOST = "https://kapi.kakao.com"

def build_front_url(next_param: str | None) -> str:
    """/login 같은 상대경로든, 인코딩된 값이든 안전하게 프론트 URL 만들어줌"""
    if not next_param:
        return urljoin(FRONTEND_BASE, "/login?login=success")

    decoded = unquote(next_param)

    if decoded.startswith("http://") or decoded.startswith("https://"):
        return decoded
    if decoded.startswith("/"):
        return f"{FRONTEND_BASE}{decoded}"
    return f"{FRONTEND_BASE}/{decoded}"

def exchange_code_for_token(code: str) -> dict:
    url = f"{KAUTH_HOST}/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,  # authorize 때와 완전히 동일해야 함
        "code": code,
    }
    # 콘솔에서 Client Secret 사용이 ON일 때만 포함
    if CLIENT_SECRET:
        data["client_secret"] = CLIENT_SECRET

    resp = requests.post(
        url, data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    # 디버깅용 로그(배포 중 문제 파악)
    print("Kakao token status:", resp.status_code)
    print("Kakao token body:", resp.text)

    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Token error: {resp.text}")
    return resp.json()

@router.get("/auth/kakao/login")
def kakao_login(request: Request, next: str | None = "/login?login=success"):
    if not CLIENT_ID:
        raise HTTPException(status_code=500, detail="KAKAO_CLIENT_ID not set")

    next_url = build_front_url(next)
    # 세션에 next 저장
    request.session["next"] = next_url

    authorize_url = (
        f"{KAUTH_HOST}/oauth/authorize"
        f"?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    )
    return RedirectResponse(authorize_url, status_code=302)

@router.get("/auth/kakao/callback")
def kakao_callback(request: Request, code: str | None = None, error: str | None = None):
    if error:
        # 카카오에서 에러가 넘어온 경우
        return JSONResponse({"error": error}, status_code=400)
    if not code:
        return JSONResponse({"error": "Missing code"}, status_code=400)

    token = exchange_code_for_token(code).get("access_token", "")

    # (선택) 토큰으로 사용자 정보 조회 원하면 아래 사용
    # user = requests.get(f"{KAPI_HOST}/v2/user/me",
    #                     headers={"Authorization": f"Bearer {token}"},
    #                     timeout=10).json()

    # next URL 불러오기 (없으면 기본값)
    next_url = request.session.pop("next", build_front_url("/login?login=success"))

    # 성공 표시 없으면 추가
    if ("login=success" not in next_url) and ("login%3Dsuccess" not in next_url):
        sep = "&" if ("?" in next_url) else "?"
        next_url = f"{next_url}{sep}login=success"

    print("[REDIRECT -> FRONT]", next_url)
    return RedirectResponse(next_url, status_code=302)
