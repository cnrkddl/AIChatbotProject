# kakao-login/api.py
import os
import sys
import requests
from urllib.parse import urlencode, quote, unquote
from pathlib import Path
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS

# =========================
# .env 로드 (있으면)
# =========================
try:
    from dotenv import load_dotenv
    here = Path(__file__).resolve().parent
    load_dotenv(here / ".env")
    be_env = (here / ".." / "backend" / ".env").resolve()
    if be_env.exists():
        load_dotenv(be_env, override=False)
except Exception as e:
    print("[WARN] dotenv load:", e, file=sys.stderr)

# =========================
# 환경 변수 (배포용)
# =========================
# 카카오 REST API 키
CLIENT_ID = os.getenv("KAKAO_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "").strip()  # 선택

# 이 Flask 서비스의 퍼블릭 베이스 URL (예: https://kakao-bridge.onrender.com)
SERVICE_BASE = os.getenv("SERVICE_BASE", os.getenv("BACKEND_BASE", "http://localhost:8001")).strip().rstrip("/")

# 최종 프론트(사용자에게 보여줄) 베이스 URL (예: https://cnrkddl.github.io/AIChatbotProject)
FRONTEND_BASE = os.getenv("FRONTEND_BASE", "http://localhost:3000").strip().rstrip("/")

# HashRouter(CRA GitHub Pages) 사용 여부
USE_HASH_ROUTER = os.getenv("USE_HASH_ROUTER", "true").lower() == "true"

# Kakao OAuth 고정 호스트
KAUTH_HOST = "https://kauth.kakao.com"
KAPI_HOST = "https://kapi.kakao.com"

# 콜백 경로/URL — 카카오 개발자 콘솔 Redirect URI와 동일해야 함
REDIRECT_PATH = os.getenv("KAKAO_REDIRECT_PATH", "/redirect").strip()
REDIRECT_URI = f"{SERVICE_BASE}{REDIRECT_PATH}"

# 요청 시 허용할 오리진(CORS) — 쿠키/자격증명 없는 순수 리다이렉트 서버지만, 디버그용 API마다 필요할 수 있음
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()] or [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://cnrkddl.github.io",
    "https://cnrkddl.github.io/AIChatbotProject",
]

# 동의 항목 스코프 (필요 없는 건 제거 가능)
DEFAULT_SCOPE = os.getenv("KAKAO_SCOPE", "profile_nickname,account_email")

print("=== Kakao OAuth Boot (PROD) ===")
print("CLIENT_ID(prefix):", (CLIENT_ID[:6] + "..." if CLIENT_ID else "(EMPTY)"))
print("SERVICE_BASE:", SERVICE_BASE)
print("FRONTEND_BASE:", FRONTEND_BASE)
print("REDIRECT_URI:", REDIRECT_URI)
print("USE_HASH_ROUTER:", USE_HASH_ROUTER)
print("CORS_ORIGINS:", CORS_ORIGINS)
print("===============================")

if not CLIENT_ID:
    raise RuntimeError("KAKAO_CLIENT_ID 가 비어 있습니다. .env에 REST API 키를 설정하세요.")

# =========================
# Flask App (세션/서버쿠키 미사용)
# =========================
app = Flask(__name__)
CORS(app, supports_credentials=False, resources={r"/*": {"origins": CORS_ORIGINS}})

# =========================
# Helper
# =========================
def _front_join(path: str) -> str:
    """
    FRONTEND_BASE + path 조합.
    HashRouter 사용 시 '/#/<path>' 형태로.
    """
    if not path:
        path = "/"
    if USE_HASH_ROUTER:
        if path.startswith("/#/"):
            return f"{FRONTEND_BASE}{path}"
        if path.startswith("?"):
            path = "/" + path
        if not path.startswith("/"):
            path = "/" + path
        return f"{FRONTEND_BASE}/#{path}"  # ex) https://gh-pages/#/login?login=success
    else:
        if not path.startswith("/"):
            path = "/" + path
        return f"{FRONTEND_BASE}{path}"

def build_front_url(next_param: str | None) -> str:
    """
    next(인코딩/비인코딩 모두 허용)를 안전하게 최종 프론트 URL로 변환
    """
    if not next_param:
        return _front_join("/login?login=success")
    decoded = unquote(next_param)
    if decoded.startswith(("http://", "https://")):
        return decoded
    if decoded.startswith("/"):
        return _front_join(decoded)
    return _front_join("/" + decoded)

def append_query(url: str, key: str, value: str) -> str:
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{quote(key, safe='')}={quote(value, safe='')}"

def build_authorize_url(scope: str | None, state: str | None) -> str:
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
    }
    if scope:
        params["scope"] = scope
    if state:
        params["state"] = state  # ✅ next_url을 담아 세션 없이 왕복
    return f"{KAUTH_HOST}/oauth/authorize?{urlencode(params)}"

def exchange_token(code: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    if CLIENT_SECRET:
        data["client_secret"] = CLIENT_SECRET
    resp = requests.post(f"{KAUTH_HOST}/oauth/token", data=data, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"Token error: {resp.text}")
    return resp.json()

def fetch_profile(access_token: str) -> dict:
    r = requests.get(
        f"{KAPI_HOST}/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    try:
        return r.json()
    except Exception:
        return {"raw": r.text, "status": r.status_code}

# =========================
# Routes (배포용)
# =========================
@app.route("/authorize")
def authorize():
    """
    카카오 인가 페이지로 리다이렉트.
    - next: 로그인 성공 후 돌아갈 경로/URL (ex: /home)
    - scope: 기본 'profile_nickname,account_email'
    """
    next_raw = request.args.get("next", "/login?login=success")
    next_url = build_front_url(next_raw)
    scope = request.args.get("scope", DEFAULT_SCOPE)
    authorize_url = build_authorize_url(scope=scope, state=next_url)  # ✅ 세션 없이 state 사용
    return redirect(authorize_url, code=302)

@app.route(REDIRECT_PATH, methods=["GET"])
def redirect_page():
    """
    카카오 콜백. code + state(next_url).
    토큰 교환 → (선택) 프로필 조회 → next_url로 리다이렉트.
    """
    code = request.args.get("code")
    state = request.args.get("state")  # authorize에서 실어 보낸 next_url
    if not code:
        return "Missing code", 400

    try:
        token = exchange_token(code)
    except Exception as e:
        return f"Token error: {e}", 400

    access_token = token.get("access_token", "")
    next_url = state or build_front_url("/login?login=success")

    # ?login=success 보장
    if ("login=success" not in next_url) and ("login%3Dsuccess" not in next_url):
        next_url = append_query(next_url, "login", "success")

    # (선택) 닉네임/이메일을 쿼리로 추가 — 프론트에서 바로 표시하고 싶을 때만 유용
    try:
        if access_token:
            prof = fetch_profile(access_token)
            kakao_account = prof.get("kakao_account") or {}
            profile = kakao_account.get("profile") or {}
            nickname = profile.get("nickname")
            email = kakao_account.get("email")
            if nickname and "nickname=" not in next_url:
                next_url = append_query(next_url, "nickname", nickname)
            if email and "email=" not in next_url:
                next_url = append_query(next_url, "email", email)
    except Exception as e:
        # 프로필 실패는 로그인 실패 아님
        print("[WARN] profile fetch failed:", e, file=sys.stderr)

    print("[REDIRECT -> FRONT]", next_url)
    return redirect(next_url, code=302)

# (디버그용) 액세스 토큰을 헤더로 보내서 카카오 프로필 프록시 조회
@app.route("/profile")
def profile():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "send 'Authorization: Bearer <access_token>'"}), 400
    token = auth.split(" ", 1)[1]
    r = requests.get(f"{KAPI_HOST}/v2/user/me", headers={"Authorization": f"Bearer {token}"}, timeout=10)
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text}
    return jsonify(body), r.status_code

# (디버그용) 카카오 로그아웃 프록시
@app.route("/logout", methods=["POST", "GET"])
def logout():
    auth = request.headers.get("Authorization", "")
    token = auth.split(" ", 1)[1] if auth.startswith("Bearer ") else ""
    if token:
        try:
            requests.post(f"{KAPI_HOST}/v1/user/logout", headers={"Authorization": f"Bearer {token}"}, timeout=10)
        except Exception as e:
            print("[WARN] kakao logout error:", e, file=sys.stderr)
    return jsonify({"ok": True})

# (디버그용) 카카오 연결해제 프록시
@app.route("/unlink", methods=["POST", "GET"])
def unlink():
    auth = request.headers.get("Authorization", "")
    token = auth.split(" ", 1)[1] if auth.startswith("Bearer ") else ""
    if not token:
        return jsonify({"error": "not_authenticated"}), 401
    r = requests.post(f"{KAPI_HOST}/v1/user/unlink", headers={"Authorization": f"Bearer {token}"}, timeout=10)
    try:
        body = r.json()
    except Exception:
        body = {"raw": r.text}
    return jsonify({"ok": r.status_code == 200, "kakao": body}), r.status_code

# 헬스체크(배포 플랫폼용)
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service_base": SERVICE_BASE,
        "redirect_uri": REDIRECT_URI,
        "frontend_base": FRONTEND_BASE,
    })

# =========================
# Entrypoint
# =========================
if __name__ == "__main__":
    # 배포에서는 gunicorn 등 WSGI 서버 권장 (예: gunicorn -w 2 -b :8001 api:app)
    port = int(os.getenv("PORT", "8001"))
    app.run(host="0.0.0.0", port=port, debug=False)
