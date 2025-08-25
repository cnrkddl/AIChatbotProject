from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
import os
import traceback

# ===== 카카오 라우터 임포트 =====
try:
    from .auth_kakao import router as kakao_router
except ImportError:
    from auth_kakao import router as kakao_router

# ===== 내부 모듈 =====
try:
    from .chatbot_core import get_emotional_support_response
    from .ocr_records import (
        extract_text_from_pdf,
        parse_by_date,
        compare_changes_with_text,
        build_nursing_notes_json,
    )
    from .database import db_manager
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

ALLOWED_ORIGINS = ["https://cnrkddl.github.io"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kakao_router)

# ==============================
# 스키마
# ==============================
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

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
    try:
        session_id = (req.session_id or "web").strip() or "web"
        reply_text = get_emotional_support_response(
            session_id=session_id,
            user_input=req.message
        )
        return {"ok": True, "reply": reply_text}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"chat failed: {e}")

# ==============================
# PDF 분석
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
# 환자 기록
# ==============================
PATIENT_PDFS: Dict[str, str] = {
    "25-0000032": "uploads/김x애-간호기록지.pdf",
}

def _abs_path(rel_or_abs: str) -> str:
    base = os.path.dirname(os.path.abspath(__file__))
    return rel_or_abs if os.path.isabs(rel_or_abs) else os.path.join(base, rel_or_abs)

@app.get("/patients/{patient_id}/nursing-notes")
def get_nursing_notes(patient_id: str):
    rel_path = PATIENT_PDFS.get(patient_id)
    if not rel_path:
        raise HTTPException(status_code=404, detail=f"등록된 PDF가 없습니다: {patient_id}")

    full_path = _abs_path(rel_path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"PDF 파일이 없습니다: {full_path}")

    notes_json = build_nursing_notes_json(full_path)
    text = extract_text_from_pdf(full_path)
    by_date = parse_by_date(text)

    return {"ok": True, "patient_id": patient_id, "resolved_path": full_path, "by_date": by_date, "notes": notes_json}

# ==============================
# 피드백
# ==============================
@app.post("/feedback")
def save_feedback(req: FeedbackRequest, request: Request):
    try:
        user_email = request.cookies.get("k_email")
        if not user_email:
            raise HTTPException(status_code=401, detail="로그인이 필요합니다")

        feedback_id = db_manager.save_feedback(
            user_email=user_email,
            rating=req.rating,
            comment=req.comment.strip(),
            timestamp=req.timestamp
        )
        return {"ok": True, "feedback_id": feedback_id}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"피드백 저장 실패: {e}")

@app.get("/feedback")
def get_feedback():
    try:
        feedback_data = db_manager.get_feedback()
        return {"ok": True, "feedback": feedback_data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"피드백 조회 실패: {e}")

# ==============================
# 환자 관리
# ==============================
@app.get("/my-patients")
def get_my_patients(request: Request):
    try:
        user_email = "sample@sample.com"  # TODO: 쿠키 이메일로 교체
        patients = db_manager.get_user_patients(user_email)
        return {"ok": True, "patients": patients}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"환자 목록 조회 실패: {e}")

@app.post("/add-patient")
async def add_patient(request: Request):
    try:
        user_email = "sample@sample.com"  # TODO: 쿠키 이메일로 교체
        body = await request.json()
        patient_id = body.get("patient_id")
        patient_name = body.get("patient_name")
        relationship = body.get("relationship")
        if not patient_id or not patient_name:
            raise HTTPException(status_code=400, detail="환자 ID와 이름은 필수입니다")

        success = db_manager.add_user_patient(user_email, patient_id, patient_name, relationship)
        if success:
            return {"ok": True, "message": "환자가 추가되었습니다"}
        else:
            return {"ok": False, "message": "이미 연결된 환자입니다"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"환자 추가 실패: {e}")
