import os
import re
import pdfplumber
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# 1. 특이사항 키워드
KEYWORDS = ["땀", "자가배뇨", "수면", "가래", "욕창"]

# YYYY-MM-DD 형태만
RE_YMD = re.compile(r"\b(20\d{2})[-./](\d{1,2})[-./](\d{1,2})\b")

# 2. PDF 텍스트 추출
def extract_text_from_pdf(pdf_path: str) -> str:
    """PDF에서 텍스트 추출"""
    text = ""

    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_pdf_path = os.path.join(base_dir, pdf_path)

    if not os.path.exists(full_pdf_path):
        raise FileNotFoundError(f"[extract_text_from_pdf] 파일이 없습니다: {full_pdf_path}")

    with pdfplumber.open(full_pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# 3. 날짜별 파싱 (YYYY-MM-DD 탐지 개선)
def parse_by_date(text: str) -> Dict[str, List[Tuple[str, str]]]:
    records: Dict[str, List[Tuple[str, str]]] = {}
    current_date: Optional[str] = None

    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue

        # 라인 전체가 날짜만 있는 경우뿐 아니라, 문장 중간에 날짜가 있어도 탐지
        m = RE_YMD.search(line)
        if m:
            y, mth, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            current_date = f"{y:04d}-{mth:02d}-{d:02d}"
            if current_date not in records:
                records[current_date] = []
            continue

        # 특이사항 라인 탐색 (*, -로 시작)
        if current_date and (line.startswith("*") or line.startswith("-")):
            for kw in KEYWORDS:
                if kw in line:
                    records[current_date].append((kw, line))
                    break

    return records


# 4. 호전 여부 포함 텍스트 출력
def compare_changes_with_text(records: Dict[str, List[Tuple[str, str]]]) -> str:
    output_lines = []
    dates = sorted(records.keys())

    for i, date in enumerate(dates):
        output_lines.append(f"=== {date} ===")
        current_items = list(records[date])  # (kw, cause)

        if i > 0:
            prev_date = dates[i - 1]
            prev_kw = {kw for kw, _ in records[prev_date]}
            curr_kw = {kw for kw, _ in records[date]}
            resolved = prev_kw - curr_kw
            for kw in resolved:
                current_items.append((kw, "호전됨"))

        for kw, cause in current_items:
            output_lines.append(f"- 특이사항 : {kw} / 원인 : {cause}")
        output_lines.append("")

    return "\n".join(output_lines)


# 5. JSON 구조로 반환
def build_nursing_notes_json(pdf_path: str):
    text = extract_text_from_pdf(pdf_path)
    records = parse_by_date(text)
    notes = []
    for date in sorted(records.keys()):
        items = [{"keyword": kw, "detail": cause} for kw, cause in records[date]]
        notes.append({"date": date, "items": items})
    return notes
