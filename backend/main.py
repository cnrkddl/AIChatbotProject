# backend/main.py
import os
from datetime import datetime, date
from typing import List, Optional

import requests
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .auth_kakao import router as kakao_router
from .chatbot_core import get_emotional_support_response
from .ocr_records import (
    extract_text_from_pdf,
    parse_by_date,
    compare_changes_with_text,
    build_nursing_notes_json,
)

FRONTEND_ORIGIN = os.getenv("FRONT_ORIGIN", "https://cnrkddl.github.io")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN,             # 깃허브 페이지
        "http://localhost:3000",     # 로컬 개발
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,          # 쿠키 전송 허용
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kakao OAuth 라우터 부착 (/auth/kakao/login, /auth/kakao/callback, /logout, /unlink, /profile)
app.include_router(kakao_router)


@app.get("/")
def root():
    return {"message": "챗봇 API 정상 동작 중"}


class UserInput(BaseModel):
    session_id: str
    user_input: str


@app.post("/chat")
def chat_endpoint(data: UserInput):
    reply = get_emotional_support_response(
        session_id=data.session_id,
        user_input=data.user_input,
    )
    return {"response": reply}


@app.get("/analyze-pdf")
def analyze_pdf():
    pdf_path = "uploads/김x애-간호기록지.pdf"
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"PDF not found: {pdf_path}")
    pdf_text = extract_text_from_pdf(pdf_path)
    parsed = parse_by_date(pdf_text)
    text_with_changes = compare_changes_with_text(parsed)
    return {"result": text_with_changes}


PATIENT_PDFS = {
    "25-0000032": [{"from": "2025-08-01", "to": None, "path": "uploads/김x애-간호기록지.pdf"}],
    "23-0000009": [{"from": "2025-08-10", "to": None, "path": "uploads/장x규-간호기록지.pdf"}],
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
            detail=f"No PDF found for patient {patient_id} (target_date={target_date})",
        )
    notes = build_nursing_notes_json(pdf_path)
    return notes


@app.get("/auth/session")
def get_session(request: Request):
    token = request.cookies.get("kakao_access_token")
    if not token:
        return JSONResponse({"ok": False}, status_code=401)
    r = requests.get("https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {token}"}, timeout=10)
    if r.status_code != 200:
        return JSONResponse({"ok": False}, status_code=401)
    data = r.json()
    nickname = (data.get("kakao_account") or {}).get("profile", {}).get("nickname", "친구")
    return {"ok": True, "user": {"nickname": nickname}}
