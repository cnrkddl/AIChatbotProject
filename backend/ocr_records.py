import os
import re
import pdfplumber
from pathlib import Path
from typing import Dict, List, Tuple

SYMPTOM_TEMPLATES = {
    "수면장애": "수면",
    "자가배뇨 못함": "자가배뇨",
    "대소변 조절 못함": "변조절",          
    "파킨슨 증상악화": "파킨슨 증상심해져",
    "변을 못봄": "변을 못봄"
}


CAUSE_TEMPLATES = {
    "산소 공급으로 안정화": "침상에서 소리를 계속 내면서",
    "도뇨관 삽입 및 관리로 해결": "foley catheter",
    "기저귀 착용과 주기적 교환으로 해결": "기저귀",
    "진료후 복용량 증량": "파킨슨 증상심해져",
    "좌약 넣어드림": "좌약 넣어드림"
}

EXCLUDE_REGEXES = [
    re.compile(r"욕창.*예방"), 
    re.compile(r"낙상방지")
]

SYMPTOM_REGEXES: Dict[str, re.Pattern] = {
    # 자가배뇨(공백·변형 허용)
    "자가배뇨": re.compile(r"자가\s*배뇨"),
    # 수면
    "수면": re.compile(r"수면"),
    # 욕창: 같은 줄/블록에 '예방'이 붙으면 EXCLUDE 단계에서 제거되므로 여기선 단순히 '욕창'만
    "욕창": re.compile(r"욕창"),
    # 대변/대소변/변조절 등 변형 모두 허용 -> 내부 라벨은 '변조절'로 통일
    "변조절": re.compile(r"(대\s*소\s*변\s*조절|대\s*변\s*조절|변\s*조절)"),
    # 변을 못봄 (을 생략한 '변 못봄'도 허용)
    "변을 못봄": re.compile(r"변(?:을)?\s*못봄"),
    # 파킨슨 증상 악화(폭넓게)
    "파킨슨 증상심해져": re.compile(r"파킨슨\s*증상.*(심해|악화)"),
}

def is_block_start(line: str) -> bool:
    if line.startswith("*") or line.startswith("-"):
        return True
    return any(p.search(line) for p in SYMPTOM_REGEXES.values())


# -----------------------------
# 템플릿 적용 함수
# -----------------------------

def apply_symptom_template(internal_label: str) -> str:

    for pretty, raw in SYMPTOM_TEMPLATES.items():

        if internal_label == raw or raw in internal_label:
            return pretty
    return internal_label

def apply_cause_template(cause_text: str) -> str:

    for pretty, raw in CAUSE_TEMPLATES.items():
        if raw in cause_text:
            return pretty
    return cause_text

# PDF 텍스트 추출
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    PDF에서 텍스트 추출 (pdfplumber)
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# 날짜별 파싱

def parse_by_date(text: str) -> Dict[str, List[Tuple[str, str]]]:

    records: Dict[str, List[Tuple[str, str]]] = {}
    current_date: str = None
    buffer: List[str] = []

    def flush_buffer():
        nonlocal buffer
        if buffer and current_date:
            block = " ".join(buffer)

            if any(rx.search(block) for rx in EXCLUDE_REGEXES):
                buffer = []
                return

            found_labels = set()
            for label, pat in SYMPTOM_REGEXES.items():
                if pat.search(block):
                    found_labels.add(label)

            if found_labels:

                existing_labels = {kw for kw, _ in records.get(current_date, [])}
                for label in found_labels - existing_labels:
                    records[current_date].append((label, block))
        buffer = []

    for raw_line in text.split("\n"):
        line = raw_line.strip()

        # 무시할 공통 머리말
        if (not line
            or "효림요양병원" in line
            or "Page No" in line
            or "Nurse Record" in line):
            continue

        # 날짜 라인
        m = re.match(r"#\s*(\d{4}-\d{2}-\d{2})", line)
        if m:
            flush_buffer()
            current_date = m.group(1)
            records.setdefault(current_date, [])
            continue

        # 블록 시작 판단
        if current_date and is_block_start(line):
            flush_buffer()
            buffer = [line]
        elif buffer:
            buffer.append(line)

    flush_buffer()
    return records

def compare_changes_with_text(records: Dict[str, List[Tuple[str, str]]]) -> str:
    output_lines: List[str] = []
    dates = sorted(records.keys())

    for i, date in enumerate(dates):
        output_lines.append(f"=== {date} ===")
        current_items = list(records[date])

        # 전일 대비 호전
        if i > 0:
            prev_date = dates[i - 1]
            prev_labels = {kw for kw, _ in records[prev_date]}
            curr_labels = {kw for kw, _ in records[date]}
            resolved = prev_labels - curr_labels
            for kw in sorted(resolved):
                current_items.append((kw, "호전됨"))

        # 출력 (템플릿 적용)
        for internal_label, cause_text in current_items:
            symptom_out = apply_symptom_template(internal_label)
            cause_out = "호전됨" if cause_text == "호전됨" else apply_cause_template(cause_text)
            output_lines.append(f"- 특이사항 : {symptom_out} / {cause_out}")

        output_lines.append("")  # 날짜 구분 빈 줄

    return "\n".join(output_lines)

#JSON 구조로 가공해주는 헬퍼
def build_nursing_notes_json(pdf_path):

    text = extract_text_from_pdf(pdf_path)
    records = parse_by_date(text)
    notes = []
    for date in sorted(records.keys()):
        items = [
            {
                "keyword": apply_symptom_template(kw),
                "detail": "호전됨" if cause == "호전됨" else apply_cause_template(cause)
            }
            for kw, cause in records[date]
        ]
        notes.append({"date": date, "items": items})
    return notes