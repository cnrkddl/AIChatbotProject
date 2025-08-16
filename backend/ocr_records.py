import os
import re
import pdfplumber

# 1. 특이사항 키워드
KEYWORDS = ["땀", "자가배뇨", "수면", "가래", "욕창"]

# 2. PDF 텍스트 추출
def extract_text_from_pdf(pdf_path):
    """PDF에서 텍스트 추출"""
    text = ""

    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_pdf_path = os.path.join(base_dir, pdf_path)

    with pdfplumber.open(full_pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# 3. 날짜별 파싱
def parse_by_date(text):
    """날짜별로 특이사항과 원인 추출"""
    records = {}
    current_date = None
    for line in text.split("\n"):
        # 날짜 찾기
        date_match = re.match(r"# (\d{4}-\d{2}-\d{2})", line.strip())
        if date_match:
            current_date = date_match.group(1)
            records[current_date] = []
            continue

        # 특이사항 라인 탐색 (*, -로 시작)
        if current_date and (line.strip().startswith("*") or line.strip().startswith("-")):
            for kw in KEYWORDS:
                if kw in line:
                    cause = line.strip()
                    records[current_date].append((kw, cause))
    return records

# 4. 호전 여부 포함 텍스트 출력
def compare_changes_with_text(records):
    """전날 대비 특이사항 호전 여부를 표시하고 텍스트로 변환"""
    output_lines = []
    dates = sorted(records.keys())

    for i, date in enumerate(dates):
        output_lines.append(f"=== {date} ===")
        current_items = list(records[date])  # (kw, cause)

        # 호전 여부 비교
        if i > 0:
            prev_date = dates[i-1]
            prev_kw = {kw for kw, _ in records[prev_date]}
            curr_kw = {kw for kw, _ in records[date]}
            resolved = prev_kw - curr_kw
            for kw in resolved:
                current_items.append((kw, "호전됨"))

        # 날짜별 항목 출력
        for kw, cause in current_items:
            output_lines.append(f"- 특이사항 : {kw} / 원인 : {cause}")
        output_lines.append("")  # 날짜 구분 빈줄

    return "\n".join(output_lines)

#JSON 구조로 가공해주는 헬퍼
def build_nursing_notes_json(pdf_path):
    """
    PDF -> {date, items:[{keyword, detail}]}[] 형태의 리스트로 반환
    """
    text = extract_text_from_pdf(pdf_path)            # 기존 함수 사용
    records = parse_by_date(text)                     # {date: [(kw, cause), ...]}
    notes = []
    for date in sorted(records.keys()):
        items = [{"keyword": kw, "detail": cause} for kw, cause in records[date]]
        notes.append({"date": date, "items": items})
    return notes