from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
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

app = FastAPI()

# =========================
# CORS 설정
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 리액트 앱의 URL. 필요시 추가/수정
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
    """
    서버에 저장된 PDF를 분석해 문장 형태 결과 반환
    """
    pdf_path = "uploads/김x애-간호기록지.pdf"  # 실제 파일 경로로 맞춰주세요
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"PDF not found: {pdf_path}")

    pdf_text = extract_text_from_pdf(pdf_path)
    parsed = parse_by_date(pdf_text)
    text_with_changes = compare_changes_with_text(parsed)
    return {"result": text_with_changes}

# =========================
# 3) PatientInfoPage용 API (JSON 구조)
#    - 환자별 PDF 매핑 + 기간/버전 확장 고려
# =========================

# 환자ID → 기간별 문서 목록 (from/to는 YYYY-MM-DD, to=None은 열린 구간)
PATIENT_PDFS = {
    "25-0000032": [  # 김x애
        {"from": "2025-08-01", "to": None, "path": "uploads/김x애-간호기록지.pdf"},
    ],
    "23-0000009": [  # 장x규
        {"from": "2025-08-10", "to": None, "path": "uploads/장x규-간호기록지.pdf"},
        # 새 버전 생기면 아래처럼 추가
        # {"from": "2025-09-01", "to": None, "path": "uploads/장x규-간호기록지_2.pdf"},
    ],
}

def _within(d: str, start: Optional[str], end: Optional[str]) -> bool:
    """
    d(YYYY-MM-DD)가 [start, end]에 포함되는가? end=None이면 열린 구간
    """
    dd = datetime.fromisoformat(d).date()
    s = datetime.fromisoformat(start).date() if start else date.min
    e = datetime.fromisoformat(end).date() if end else date.max
    return s <= dd <= e

def select_pdf_for_patient(patient_id: str, target_date: Optional[str]) -> Optional[str]:
    """
    환자ID와 (옵션) 기준일로 적절한 PDF 경로 반환
    - 기준일 없으면 최신(from 가장 최근) 문서를 선택
    - 기준일 있으면 그 날짜를 포함하는 기간 문서를 선택
    """
    entries = PATIENT_PDFS.get(patient_id, [])
    if not entries:
        return None

    # 기준일 없으면 최신(from 최신) 우선으로 존재하는 파일 반환
    if not target_date:
        entries_sorted = sorted(entries, key=lambda x: x.get("from") or "", reverse=True)
        for ent in entries_sorted:
            if os.path.exists(ent["path"]):
                return ent["path"]
        return None

    # 기준일 있는 경우 그 기간에 해당하는 문서를 선택
    for ent in entries:
        if _within(target_date, ent.get("from"), ent.get("to")) and os.path.exists(ent["path"]):
            return ent["path"]
    return None

# ====== 응답 스키마 ======
class NursingNoteItem(BaseModel):
    keyword: str
    detail: str

class NursingNote(BaseModel):
    date: str
    items: List[NursingNoteItem]

@app.get("/patients/{patient_id}/nursing-notes", response_model=List[NursingNote])
def get_nursing_notes(
    patient_id: str,
    target_date: Optional[str] = Query(
        None, description="YYYY-MM-DD (이 날짜가 포함되는 문서를 우선 선택)"
    ),
):
    """
    환자별 간호기록지(PDF)를 파싱해 날짜별 특이사항을 JSON 배열로 반환
      - target_date 미지정 시: 최신 문서 사용
      - target_date 지정 시: 해당 날짜가 포함되는 기간 문서 사용
    반환 형식:
      [
        {"date": "2025-08-12", "items": [{"keyword":"발열","detail":"38.0도..."}, ...]},
        ...
      ]
    """
    pdf_path = select_pdf_for_patient(patient_id, target_date)
    if not pdf_path:
        raise HTTPException(
            status_code=404,
            detail=f"No PDF found for patient {patient_id} (target_date={target_date})"
        )

    notes = build_nursing_notes_json(pdf_path)
    return notes
