# backend/kakao_oauth.py
import os
import requests
from urllib.parse import urlencode

KAKAO_AUTH_BASE = "https://kauth.kakao.com"
KAKAO_API_BASE = "https://kapi.kakao.com"

CLIENT_ID = os.getenv("KAKAO_CLIENT_ID", "").strip()
REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "").strip()
CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "").strip()


def build_authorize_url(scope: str = "profile_nickname,account_email") -> str:
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": scope,
    }
    return f"{KAKAO_AUTH_BASE}/oauth/authorize?{urlencode(params)}"


def exchange_token(code: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    if CLIENT_SECRET:
        data["client_secret"] = CLIENT_SECRET

    r = requests.post(f"{KAKAO_AUTH_BASE}/oauth/token", data=data, timeout=10)
    r.raise_for_status()
    return r.json()


def get_user_profile(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(f"{KAKAO_API_BASE}/v2/user/me", headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()
