# backend/kakao_oauth.py
import os
import requests
from urllib.parse import urlencode

# ---- 환경변수 ----
CLIENT_ID = os.getenv("KAKAO_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "").strip()  # 콘솔에서 '사용'일 때만 사용
BACKEND_BASE = os.getenv("BACKEND_BASE", "https://aichatbotproject.onrender.com").strip()
REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", f"{BACKEND_BASE}/auth/kakao/callback").strip()

KAUTH_HOST = "https://kauth.kakao.com"
KAPI_HOST = "https://kapi.kakao.com"

if not CLIENT_ID:
    raise RuntimeError("KAKAO_CLIENT_ID 가 설정되지 않았습니다.")

def build_authorize_url(scope: str = "") -> str:
    """카카오 authorize URL 생성 (main.py에서 /auth/kakao/login 에서 사용)"""
    base = f"{KAUTH_HOST}/oauth/authorize"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,  # 콜백과 정확히 일치해야 함
    }
    if scope:
        params["scope"] = scope
    return f"{base}?{urlencode(params)}"

def exchange_token(code: str) -> dict:
    """인가코드로 액세스 토큰 교환"""
    url = f"{KAUTH_HOST}/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,  # authorize 때 보낸 것과 완전히 동일
        "code": code,
    }
    # 콘솔에서 Client Secret '사용'이면 포함, 미사용이면 절대 넣지 말 것
    if CLIENT_SECRET:
        data["client_secret"] = CLIENT_SECRET

    resp = requests.post(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    # 디버깅용: 배포 실패시 원인 확인
    print("Kakao token status:", resp.status_code)
    print("Kakao token body:", resp.text)

    resp.raise_for_status()
    return resp.json()

def get_user_profile(access_token: str) -> dict:
    """토큰으로 사용자 정보 조회"""
    url = f"{KAPI_HOST}/v2/user/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers, timeout=10)
    # 디버깅용
    print("Kakao user status:", resp.status_code)
    print("Kakao user body:", resp.text)
    resp.raise_for_status()
    return resp.json()
