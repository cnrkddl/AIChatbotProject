from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import os

from chatbot_core import get_emotional_support_response
from ocr_records import (
    extract_text_from_pdf,
    parse_by_date,
    compare_changes_with_text,
    build_nursing_notes_json,
)

# ===== 카카오 OAuth 유틸
from kakao_oauth import (
    build_authorize_url,
    exchange_token,
    get_user_profile,
)

app = FastAPI()

# =========================
# CORS 설정
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 리액트 앱 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 1) 챗봇 API
# =========================
class UserInput(BaseModel):
    session_id: str
    user_input: str

@app.get("/")
def root():
    return {"message": "챗봇 API 정상 동작 중"}

@app.post("/chat")
def chat_endpoint(data: UserInput):
    reply = get_emotional_support_response(
        session_id=data.session_id,
        user_input=data.user_input
    )
    return {"response": reply}

# =========================
# 2) PDF 분석 API (문장형 결과)
# =========================
@app.get("/analyze-pdf")
def analyze_pdf():
    pdf_path = "uploads/김x애-간호기록지.pdf"
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"PDF not found: {pdf_path}")

    pdf_text = extract_text_from_pdf(pdf_path)
    parsed = parse_by_date(pdf_text)
    text_with_changes = compare_changes_with_text(parsed)
    return {"result": text_with_changes}

# =========================
# 3) PatientInfoPage용 API (JSON 구조)
# =========================

PATIENT_PDFS = {
    "25-0000032": [
        {"from": "2025-08-01", "to": None, "path": "uploads/김x애-간호기록지.pdf"},
    ],
    "23-0000009": [
        {"from": "2025-08-10", "to": None, "path": "uploads/장x규-간호기록지.pdf"},
    ],
}

def _within(d: str, start: Optional[str], end: Optional[str]) -> bool:
    dd = datetime.fromisoformat(d).date()
    s = datetime.fromisoformat(start).date() if start else date.min
    e = datetime.fromisoformat(end).date() if end else date.max
    return s <= dd <= e

def select_pdf_for_patient(patient_id: str, target_date: Optional[str]) -> Optional[str]:
    entries = PATIENT_PDFS.get(patient_id, [])
    if not entries:
        return None

    if not target_date:
        entries_sorted = sorted(entries, key=lambda x: x.get("from") or "", reverse=True)
        for ent in entries_sorted:
            if os.path.exists(ent["path"]):
                return ent["path"]
        return None

    for ent in entries:
        if _within(target_date, ent.get("from"), ent.get("to")) and os.path.exists(ent["path"]):
            return ent["path"]
    return None

class NursingNoteItem(BaseModel):
    keyword: str
    detail: str

class NursingNote(BaseModel):
    date: str
    items: List[NursingNoteItem]

@app.get("/patients/{patient_id}/nursing-notes", response_model=List[NursingNote])
def get_nursing_notes(
    patient_id: str,
    target_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
):
    pdf_path = select_pdf_for_patient(patient_id, target_date)
    if not pdf_path:
        raise HTTPException(
            status_code=404,
            detail=f"No PDF found for patient {patient_id} (target_date={target_date})"
        )

    notes = build_nursing_notes_json(pdf_path)
    return notes

# =========================
# 4) 카카오 로그인 API
# =========================

@app.get("/auth/kakao/login")
def kakao_login():
    url = build_authorize_url(scope="profile_nickname,account_email")
    return RedirectResponse(url)


@app.get("/auth/kakao/callback")
def kakao_callback(code: str):
    token_info = exchange_token(code)
    access_token = token_info.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="카카오 토큰 발급 실패")

    user_info = get_user_profile(access_token)

    # 프론트엔드 주소로 리다이렉트 (사용자 정보는 쿼리 파라미터로 일부만 전달)
    frontend_url = f"http://localhost:3000/login?login=success&nickname={user_info['properties']['nickname']}"
    return RedirectResponse(frontend_url)