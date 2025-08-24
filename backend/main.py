# backend/main.py
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import importlib
import json
import os
import traceback
import inspect
import uuid


# ===== 카카오 라우터 임포트 (패키지/단일파일 실행 모두 지원) =====
try:
    # 패키지 실행: uvicorn backend.main:app --reload
    from .auth_kakao import router as kakao_router  # type: ignore
except ImportError:
    # 디렉토리에서 직접 실행: (cd backend && uvicorn main:app --reload)
    from auth_kakao import router as kakao_router  # type: ignore

# ===== 프로젝트 내부 모듈 =====
try:
    from .chatbot_core import get_emotional_support_response  # type: ignore
    from .ocr_records import (  # type: ignore
        extract_text_from_pdf,
        parse_by_date,
        compare_changes_with_text,
        build_nursing_notes_json,
    )
    from .database import db_manager  # type: ignore
except ImportError:
    from chatbot_core import get_emotional_support_response
    from ocr_records import (
        extract_text_from_pdf,
        parse_by_date,
        compare_changes_with_text,
        build_nursing_notes_json,
    )
    from database import db_manager

# ==============================
# FastAPI App
# ==============================
app = FastAPI(title="AI Care Backend", version="1.0.2")

# ----- CORS -----
ALLOWED_ORIGINS = [
    "https://cnrkddl.github.io",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- 카카오 라우터 -----
app.include_router(kakao_router)

# ==============================
# 스키마
# ==============================
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # 없으면 "web"

class AnalyzePdfRequest(BaseModel):
    pdf_path: str

class ParseByDateRequest(BaseModel):
    text: str

class CompareChangesRequest(BaseModel):
    prev_text: str
    curr_text: str

class FeedbackRequest(BaseModel):
    rating: int
    comment: str
    timestamp: str

# ==============================
# 공용
# ==============================
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}

@app.get("/")
def root():
    front = os.getenv("FRONTEND_REDIRECT_URL", "http://localhost:3000/")
    return RedirectResponse(front)

# ==============================
# 챗봇
# ==============================
@app.post("/chat")
def chat(req: ChatRequest):
    """
    요청(JSON):
      { "message": "안녕", "session_id": "demo-session" }  # session_id는 선택
    응답(JSON):
      { "ok": true, "reply": "..." }
    """
    try:
        session_id = (req.session_id or "web").strip() or "web"
        reply_text = get_emotional_support_response(
            session_id=session_id,     # ✅ 이름 맞춤
            user_input=req.message     # ✅ 이름 맞춤
        )
        return {"ok": True, "reply": reply_text}
    except Exception as e:
        # 서버 콘솔에 스택트레이스 출력(디버그 도움)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"chat failed: {e}")

# ==============================
# PDF 분석/간호기록 파싱
# ==============================
@app.post("/analyze-pdf")
def analyze_pdf(req: AnalyzePdfRequest):
    try:
        text = extract_text_from_pdf(req.pdf_path)
        by_date = parse_by_date(text)
        notes_json = build_nursing_notes_json(req.pdf_path)
        return {"ok": True, "by_date": by_date, "notes": notes_json}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"analyze-pdf failed: {e}")

@app.post("/parse-by-date")
def parse_by_date_api(req: ParseByDateRequest):
    try:
        by_date = parse_by_date(req.text)
        return {"ok": True, "by_date": by_date}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"parse-by-date failed: {e}")

@app.post("/compare-changes")
def compare_changes_api(req: CompareChangesRequest):
    try:
        diff_text = compare_changes_with_text(req.prev_text, req.curr_text)
        return {"ok": True, "diff": diff_text}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"compare-changes failed: {e}")


# ==============================
# 환자ID → PDF 매핑 & 경로 헬퍼
# ==============================
PATIENT_PDFS: Dict[str, str] = {
    "25-0000032": "uploads/김x애-간호기록지.pdf",
    # 필요 시 계속 추가
    # "23-0000009": "uploads/장x규-간호기록지.pdf",
}

def _abs_path(rel_or_abs: str) -> str:
    """backend 기준 절대경로로 변환"""
    base = os.path.dirname(os.path.abspath(__file__))
    return rel_or_abs if os.path.isabs(rel_or_abs) else os.path.join(base, rel_or_abs)

# ==============================
# 환자 간호기록 라우트
# ==============================
@app.get("/patients/{patient_id}/nursing-notes")
def get_nursing_notes(patient_id: str):
    rel_path = PATIENT_PDFS.get(patient_id)
    if not rel_path:
        raise HTTPException(status_code=404, detail=f"등록된 PDF가 없습니다: {patient_id}")

    full_path = _abs_path(rel_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"PDF 파일이 없습니다: {full_path}")

    # JSON 형태 간호기록
    notes_json = build_nursing_notes_json(full_path)
    # 날짜별 원문 파싱(옵션: 프론트에서 날짜 드롭다운/원문 하이라이트 등에 활용)
    text = extract_text_from_pdf(full_path)
    by_date = parse_by_date(text)

    return {
        "ok": True,
        "patient_id": patient_id,
        "resolved_path": full_path,
        "by_date": by_date,
        "notes": notes_json,
    }

# ==============================
# 피드백 저장
# ==============================
@app.post("/feedback")
def save_feedback(req: FeedbackRequest):
    """
    피드백 저장 API
    
    요청(JSON):
      {
        "rating": 5,
        "comment": "서비스가 매우 만족스럽습니다",
        "timestamp": "2024-01-01T12:00:00.000Z"
      }
    
    응답(JSON):
      {"ok": True, "message": "피드백이 저장되었습니다"}
    """
    try:
        # 피드백 데이터 검증
        if not (1 <= req.rating <= 5):
            raise HTTPException(status_code=400, detail="별점은 1-5 사이여야 합니다")
        
        if not req.comment.strip():
            raise HTTPException(status_code=400, detail="의견을 입력해주세요")
        
        # 현재 로그인한 사용자 이메일 가져오기 (쿠키에서)
        # 실제 구현에서는 인증된 사용자 정보를 사용해야 함
        user_email = "sample@sample.com"  # 임시로 하드코딩, 나중에 수정 필요
        
        # 데이터베이스에 피드백 저장
        feedback_id = db_manager.save_feedback(
            user_email=user_email,
            rating=req.rating,
            comment=req.comment.strip(),
            timestamp=req.timestamp
        )
        
        return {
            "ok": True, 
            "message": "피드백이 성공적으로 저장되었습니다",
            "feedback_id": feedback_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"피드백 저장 실패: {e}")

# ==============================
# 저장된 피드백 조회
# ==============================
@app.get("/feedback")
def get_feedback():
    """
    저장된 모든 피드백 조회
    
    응답(JSON):
      {
        "ok": True,
        "feedback": [
          {
            "id": 1,
            "user_email": "sample@sample.com",
            "rating": 5,
            "comment": "서비스가 매우 만족스럽습니다",
            "timestamp": "2024-01-01T12:00:00.000Z",
            "created_at": "2024-01-01T12:00:00.000Z"
          }
        ]
      }
    """
    try:
        feedback_data = db_manager.get_feedback()
        return {"ok": True, "feedback": feedback_data}
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"피드백 조회 실패: {e}")

# ==============================
# 사용자별 환자 목록 조회
# ==============================
@app.get("/my-patients")
def get_my_patients(request: Request):
    """
    로그인한 사용자의 환자 목록 조회
    
    응답(JSON):
      {
        "ok": True,
        "patients": [
          {
            "patient_id": "25-0000032",
            "patient_name": "김x애",
            "relationship": "딸",
            "birth_date": "1935-03-15",
            "room_number": "301",
            "admission_date": "2024-01-15"
          }
        ]
      }
    """
    try:
        # 현재 로그인한 사용자 이메일 가져오기 (쿠키에서)
        # 실제 구현에서는 인증된 사용자 정보를 사용해야 함
        user_email = "sample@sample.com"  # 임시로 하드코딩, 나중에 수정 필요
        
        patients = db_manager.get_user_patients(user_email)
        return {"ok": True, "patients": patients}
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"환자 목록 조회 실패: {e}")

# ==============================
# 사용자-환자 연결 추가
# ==============================
@app.post("/add-patient")
async def add_patient(request: Request):
    """
    사용자-환자 연결 추가
    
    요청(JSON):
      {
        "patient_id": "25-0000032",
        "patient_name": "김x애",
        "relationship": "딸"
      }
    """
    try:
        # 현재 로그인한 사용자 이메일 가져오기
        user_email = "sample@sample.com"  # 임시로 하드코딩
        
        # 요청 본문 파싱
        body = await request.json()
        patient_id = body.get("patient_id")
        patient_name = body.get("patient_name")
        relationship = body.get("relationship")
        
        if not patient_id or not patient_name:
            raise HTTPException(status_code=400, detail="환자 ID와 이름은 필수입니다")
        
        # 데이터베이스에 연결 추가
        success = db_manager.add_user_patient(
            user_email=user_email,
            patient_id=patient_id,
            patient_name=patient_name,
            relationship=relationship
        )
        
        if success:
            return {"ok": True, "message": "환자가 추가되었습니다"}
        else:
            return {"ok": False, "message": "이미 연결된 환자입니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"환자 추가 실패: {e}")