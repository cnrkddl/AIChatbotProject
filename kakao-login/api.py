# kakao-login/api.py
import os
import sys
import requests
from urllib.parse import urljoin, unquote
from pathlib import Path
from flask import Flask, redirect, request, session, jsonify
from flask_cors import CORS

# ---- .env 자동 로드 (있으면) ----
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
    # 루트/backend/.env도 있으면 함께 로드( override=False )
    be_env = (Path(__file__).resolve().parent / ".." / "backend" / ".env").resolve()
    if be_env.exists():
        load_dotenv(be_env, override=False)
except Exception as e:
    print("[WARN] dotenv load:", e, file=sys.stderr)

# ---- 환경변수 ----
CLIENT_ID = os.getenv("KAKAO_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "").strip()
BACKEND_BASE = os.getenv("BACKEND_BASE", "https://aichatbotproject.onrender.com").strip()
FRONTEND_BASE = os.getenv("FRONTEND_BASE", "https://cnrkddl.github.io").strip()
REDIRECT_URI = f"{BACKEND_BASE}/auth/kakao/callback"
FLASK_SECRET = os.getenv("FLASK_SECRET", os.urandom(24))
KAUTH_HOST = "https://kauth.kakao.com"
KAPI_HOST = "https://kapi.kakao.com"

print("=== Kakao OAuth Boot ===")
print("CLIENT_ID(prefix):", (CLIENT_ID[:6] + "..." if CLIENT_ID else "(EMPTY)"))
print("BACKEND_BASE:", BACKEND_BASE)
print("FRONTEND_BASE:", FRONTEND_BASE)
print("REDIRECT_URI:", REDIRECT_URI)
print("========================")

if not CLIENT_ID:
    raise RuntimeError("KAKAO_CLIENT_ID 가 비어 있습니다. kakao-login/.env 에 REST API 키를 설정하세요.")

app = Flask(__name__)
app.secret_key = FLASK_SECRET
CORS(app, supports_credentials=True)

def build_front_url(next_param: str) -> str:
    """
    next가 인코딩/비인코딩 어떤 형태로 와도,
    최종적으로 FRONTEND_BASE + 절대경로(/...) 형태의 URL을 만든다.
    """
    if not next_param:
        return urljoin(FRONTEND_BASE, "/login?login=success")

    # 1) 먼저 디코딩 시도 (예: %2Flogin%3Flogin%3Dsuccess -> /login?login=success)
    decoded = unquote(next_param)

    # 2) 절대 URL이면 그대로 사용
    if decoded.startswith("http://") or decoded.startswith("https://"):
        return decoded

    # 3) '/...' 로 시작하면 프론트 도메인에 그대로 붙임
    if decoded.startswith("/"):
        return f"{FRONTEND_BASE}{decoded}"

    # 4) 상대경로라면 앞에 '/'를 붙여서 처리
    return f"{FRONTEND_BASE}/{decoded}"


@app.route("/auth/kakao/login")      # ✅ /authorize -> /auth/kakao/login 로 변경
def authorize():
    next_raw = request.args.get("next", "/login?login=success")
    next_url = build_front_url(next_raw)
    session["next"] = next_url

    scope_param = request.args.get("scope", "")
    authorize_url = (
        f"{KAUTH_HOST}/oauth/authorize"
        f"?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    )
    if scope_param:
        authorize_url += f"&scope={scope_param}"
    return redirect(authorize_url)

@app.route("/auth/kakao/callback")   # ✅ /redirect -> /auth/kakao/callback 로 변경
def redirect_page():
    code = request.args.get("code", "")
    if not code:
        return "Missing code", 400

    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,   # ← authorize 때와 완전히 동일
        "code": code,
    }
    if CLIENT_SECRET:  # 콘솔에서 Client Secret '사용'일 때만 포함
        data["client_secret"] = CLIENT_SECRET

    # 디버깅 로그(401 원인 파악용)
    token_resp = requests.post(f"{KAUTH_HOST}/oauth/token",
                               data=data,
                               headers={"Content-Type": "application/x-www-form-urlencoded"},
                               timeout=10)
    print("Kakao token status:", token_resp.status_code)
    print("Kakao token body:", token_resp.text)

    if token_resp.status_code != 200:
        return f"Token error: {token_resp.text}", 400

    token_json = token_resp.json()
    session["access_token"] = token_json.get("access_token", "")

    next_url = session.pop("next", build_front_url("/login?login=success"))
    if ("login=success" not in next_url) and ("login%3Dsuccess" not in next_url):
        sep = "&" if ("?" in next_url) else "?"
        next_url = f"{next_url}{sep}login=success"

    print("[REDIRECT -> FRONT]", next_url)
    return redirect(next_url)

@app.route("/profile")
def profile():
    token = session.get("access_token", "")
    if not token:
        return jsonify({"error": "not_authenticated"}), 401
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{KAPI_HOST}/v2/user/me", headers=headers)
    return (resp.text, resp.status_code, resp.headers.items())

@app.route("/logout", methods=["POST", "GET"])
def logout():
    token = session.get("access_token", "")
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        requests.post(f"{KAPI_HOST}/v1/user/logout", headers=headers)
    session.pop("access_token", None)
    return jsonify({"ok": True})

@app.route("/unlink", methods=["POST", "GET"])
def unlink():
    token = session.get("access_token", "")
    if not token:
        return jsonify({"error": "not_authenticated"}), 401
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{KAPI_HOST}/v1/user/unlink", headers=headers)
    session.pop("access_token", None)
    try:
        body = resp.json()
    except Exception:
        body = {"raw": resp.text}
    return jsonify({"ok": True, "kakao": body})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
