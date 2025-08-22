# server.py
import os, sys
# 현재 레포 루트를 파이썬 모듈 경로에 추가 (Render 작업 디렉터리 보호)
sys.path.append(os.path.dirname(__file__))

# FastAPI 앱을 백엔드 모듈에서 가져옴
from backend.main import app  # noqa: F401
