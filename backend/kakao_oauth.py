import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

KAKAO_AUTH_BASE = "https://kauth.kakao.com"
KAKAO_API_BASE  = "https://kapi.kakao.com"

KAKAO_REST_KEY = os.getenv("KAKAO_REST_KEY", "").strip()
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "").strip()

if not KAKAO_REST_KEY:
    raise RuntimeError("KAKAO_REST_KEY 가 .env에 설정되어 있지 않습니다.")
if not KAKAO_REDIRECT_URI:
    raise RuntimeError("KAKAO_REDIRECT_URI 가 .env에 설정되어 있지 않습니다.")

def build_authorize_url(state: Optional[str] = None, scope: Optional[str] = None) -> str:
    """
    카카오 인가(로그인) URL 생성
    """
    from urllib.parse import urlencode
    params = {
        "client_id": KAKAO_REST_KEY,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "response_type": "code",
    }
    if state:
        params["state"] = state
    if scope:
        params["scope"] = scope  # 예: "profile_nickname,account_email"
    return f"{KAKAO_AUTH_BASE}/oauth/authorize?{urlencode(params)}"

def exchange_token(code: str) -> Dict[str, Any]:
    """
    인가코드(code) → 액세스 토큰 교환
    """
    url = f"{KAKAO_AUTH_BASE}/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_REST_KEY,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "code": code,
    }
    r = requests.post(url, headers=headers, data=data, timeout=10)
    r.raise_for_status()
    return r.json()

def refresh_token(refresh_token: str) -> Dict[str, Any]:
    """
    리프레시 토큰으로 액세스 토큰 재발급
    """
    url = f"{KAKAO_AUTH_BASE}/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    data = {
        "grant_type": "refresh_token",
        "client_id": KAKAO_REST_KEY,
        "refresh_token": refresh_token,
    }
    r = requests.post(url, headers=headers, data=data, timeout=10)
    r.raise_for_status()
    return r.json()

def get_user_profile(access_token: str) -> Dict[str, Any]:
    """
    액세스 토큰으로 사용자 정보 조회
    """
    url = f"{KAKAO_API_BASE}/v2/user/me"
    headers = { "Authorization": f"Bearer {access_token}" }
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()
