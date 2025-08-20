// src/pages/PatientInfoPage.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import Header from "../components/Header";
import PatientHistoryCard from "../components/PatientHistoryCard";

export default function PatientInfoPage() {
  const { patientId: routePatientId } = useParams();
  const [patientId, setPatientId] = useState(routePatientId || "25-0000032");

  // .env 우선, 없으면 8000 기본값
  const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

  const [notes, setNotes] = useState([]);        // 원본 전체
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedDate, setSelectedDate] = useState("");

  // 검색 상태 (히스토리 섹션에서 사용)
  const [query, setQuery] = useState("");         // 자유 검색(키워드/내용)
  const [debounced, setDebounced] = useState(""); // 간단 디바운스

  // ocr_records.py의 라벨을 반영한 키워드-색상 매핑
  const keywordColor = useMemo(
    () => ({
      발열: "#ef4444",         // 발열
      가래: "#06b6d4",         // 가래
      자가배뇨: "#8b5cf6",     // 자가배뇨 못함
      욕창: "#f59e0b",         // 욕창
      통증: "#f97316",         // 통증
      식사: "#22c55e",         // 식사
      "대소변 조절 못함": "#0ea5e9",   // 파랑
      "수면장애": "#f97316",         // 주황
      "자가배뇨 못함": "#8b5cf6",    // 보라
      "파킨슨 증상 악화": "#ef4444", // 빨강
      기타: "#64748b",               // 회색
    }),
    []
  );


  // 데이터 로드
  useEffect(() => {
    let ignore = false;
    async function fetchNotes() {
      setLoading(true);
      setError("");
      try {
        const res = await fetch(`${API_BASE}/patients/${patientId}/nursing-notes`);
        if (!res.ok) {
          const { detail } = await res.json().catch(() => ({ detail: res.statusText }));
          throw new Error(detail || `API Error ${res.status}`);
        }
        const data = await res.json();
        if (!ignore) {
          // 백엔드가 이미 템플릿 반영(키워드/원인 매핑, '호전됨' 포함)한 JSON을 내려줌
          setNotes(Array.isArray(data) ? data : []);
          if (Array.isArray(data) && data.length > 0) {
            setSelectedDate(data[data.length - 1].date); // 최신 날짜
          } else {
            setSelectedDate("");
          }
          setQuery(""); // 환자 변경 시 검색 초기화
        }
      } catch (e) {
        if (!ignore) setError(e.message || "불러오기에 실패했습니다.");
      } finally {
        if (!ignore) setLoading(false);
      }
    }
    fetchNotes();
    return () => {
      ignore = true;
    };
  }, [API_BASE, patientId]);

  // 검색 디바운스 (250ms)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(query.trim()), 250);
    return () => clearTimeout(t);
  }, [query]);

  // 필터링(검색어: 키워드/내용 모두 대상)
  const filteredNotes = useMemo(() => {
    const q = debounced.toLowerCase();
    if (!q) return notes;

    return notes
      .map((d) => {
        const items = (d.items || []).filter((it) => {
          const kw = (it.keyword || "기타").toLowerCase();
          const detail = (it.detail || "").toLowerCase();
          return kw.includes(q) || detail.includes(q);
        });
        return { ...d, items };
      })
      .filter((d) => (d.items || []).length > 0);
  }, [notes, debounced]);

  // 날짜 목록 / 선택 항목 (필터 결과 기준)
  const dates = useMemo(() => filteredNotes.map((n) => n.date), [filteredNotes]);

  const selectedItems = useMemo(() => {
    const day = filteredNotes.find((n) => n.date === selectedDate);
    return day?.items || [];
  }, [filteredNotes, selectedDate]);

  // 검색으로 인해 선택 날짜가 사라지면 자동 보정
  useEffect(() => {
    if (selectedDate && !dates.includes(selectedDate)) {
      setSelectedDate(dates[dates.length - 1] || "");
    }
  }, [dates, selectedDate]);

  // 키워드 요약(필터링된 결과 기준)
  const keywordStats = useMemo(() => {
    const counts = {};
    for (const d of filteredNotes) {
      for (const it of (d.items || [])) {
        const k = it.keyword || "기타";
        counts[k] = (counts[k] || 0) + 1;
      }
    }
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([k, v]) => ({ keyword: k, count: v }));
  }, [filteredNotes]);

  // 현재 검색어가 특정 키워드와 정확히 일치하는지(배지 활성화 표시)
  const isActiveKeyword = (kw) =>
    debounced && debounced.toLowerCase() === String(kw).toLowerCase();

  return (
    <div style={styles.page}>
      <Header />

      <div style={styles.container}>
        {/* 상단 바: 환자/날짜 (검색은 히스토리 섹션으로 이동) */}
        <div style={styles.topBar}>
          <div style={styles.titleWrap}>
            <h2 style={styles.title}>환자 상태 정보</h2>
            <p style={styles.subtitle}>
              간호기록지 특이사항을 날짜별로 확인합니다.
            </p>
          </div>

          <div style={styles.controls}>
            <label style={styles.label}>
              환자번호
              <input
                value={patientId}
                onChange={(e) => setPatientId(e.target.value.trim())}
                style={styles.input}
                placeholder="예: 25-0000032"
              />
            </label>

            <label style={styles.label}>
              날짜 선택
              <select
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                style={styles.select}
              >
                {dates.length === 0 && <option value="">데이터 없음</option>}
                {dates.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        {loading && <div style={styles.stateBox}>불러오는 중…</div>}
        {!!error && !loading && (
          <div style={{ ...styles.stateBox, color: "#ef4444" }}>에러: {error}</div>
        )}
        {!loading && !error && filteredNotes.length === 0 && (
          <div style={styles.stateBox}>
            {notes.length === 0 ? "표시할 간호기록이 없습니다." : "검색 결과가 없습니다."}
          </div>
        )}

        {!loading && !error && filteredNotes.length > 0 && (
          <>
            {/* 요약 카드 (필터링 결과 기준) */}
            <div style={styles.cardsGrid}>
              <SummaryCard title="총 기록 일수(필터 적용)" value={`${filteredNotes.length}일`} />
              <SummaryCard title="키워드 종류" value={`${keywordStats.length}개`} />
              <SummaryCard
                title="가장 최근 날짜"
                value={filteredNotes[filteredNotes.length - 1]?.date || "-"}
              />
            </div>

            {/* 키워드 요약 (배지 클릭: 토글) */}
            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>키워드 요약</h3>
              <div style={styles.badgeWrap}>
                {keywordStats.length === 0 && <span>— 없음 —</span>}
                {keywordStats.map(({ keyword, count }) => (
                  <Badge
                    key={keyword}
                    text={`${keyword} ${count}`}
                    color={keywordColor[keyword] || keywordColor["기타"]}
                    isActive={isActiveKeyword(keyword)}
                    onClick={() =>
                      setQuery(isActiveKeyword(keyword) ? "" : keyword) // 같은 배지 다시 클릭 → 해제
                    }
                  />
                ))}
              </div>
            </div>

            {/* 선택된 날짜 카드 — 상단 날짜 헤더 제거(중복 방지) */}
            <div style={styles.section}>
              <PatientHistoryCard
                date={selectedDate}
                items={selectedItems}
                keywordColor={keywordColor}
                highlightQuery={debounced}
              />
            </div>

            {/* 전체 히스토리 카드 목록 (검색창을 타이틀 옆으로 배치) */}
            <div style={styles.section}>
              <div style={styles.sectionHeader}>
                <h3 style={styles.sectionTitle}>전체 히스토리</h3>
                <div style={{ position: "relative" }}>
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    style={{ ...styles.input, paddingRight: 28, minWidth: 240 }}
                    placeholder="키워드/내용 검색"
                  />
                  {!!query && (
                    <button
                      onClick={() => setQuery("")}
                      style={styles.clearBtn}
                      title="검색어 지우기"
                    >
                      ×
                    </button>
                  )}
                </div>
              </div>

              <div style={styles.timelineGrid}>
                {[...filteredNotes].reverse().map((d) => (
                  <PatientHistoryCard
                    key={d.date}
                    date={d.date}
                    items={d.items || []}
                    keywordColor={keywordColor}
                    highlightQuery={debounced}
                  />
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/* ===== Sub components ===== */

function SummaryCard({ title, value }) {
  return (
    <div style={styles.card}>
      <div style={styles.cardTitle}>{title}</div>
      <div style={styles.cardValue}>{value}</div>
    </div>
  );
}

function Badge({ text, color = "#64748b", onClick, isActive = false }) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={{
        display: "inline-block",
        padding: "6px 10px",
        borderRadius: 999,
        background: isActive ? `${color}30` : `${color}20`,
        color,
        fontSize: 13,
        fontWeight: 700,
        margin: "4px 8px 4px 0",
        border: `1px solid ${isActive ? color : "transparent"}`,
        cursor: "pointer",
      }}
      title={isActive ? "필터 해제" : "이 키워드로 필터"}
    >
      {text}
    </button>
  );
}

/* ===== Styles ===== */

const styles = {
  page: {
    minHeight: "100vh",
    background: "#f8fafc",
  },
  container: {
    maxWidth: 1100,
    margin: "0 auto",
    padding: "20px 16px 48px",
  },
  topBar: {
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "space-between",
    gap: 16,
    margin: "12px 0 20px",
    flexWrap: "wrap",
  },
  titleWrap: { maxWidth: 640 },
  title: { margin: 0, fontSize: 24, fontWeight: 800, color: "#0f172a" },
  subtitle: { margin: "6px 0 0", color: "#475569" },
  controls: { display: "flex", gap: 12, flexWrap: "wrap" },
  label: { display: "flex", flexDirection: "column", fontSize: 13, color: "#334155" },
  input: {
    height: 38,
    border: "1px solid #e5e7eb",
    borderRadius: 10,
    padding: "0 12px",
    minWidth: 180,
    outline: "none",
    background: "#fff",
  },
  select: {
    height: 38,
    border: "1px solid #e5e7eb",
    borderRadius: 10,
    padding: "0 12px",
    minWidth: 160,
    outline: "none",
    background: "#fff",
  },
  stateBox: {
    background: "#fff",
    border: "1px dashed #e5e7eb",
    borderRadius: 14,
    padding: 18,
    textAlign: "center",
    color: "#334155",
  },
  cardsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
    gap: 12,
    marginTop: 8,
  },
  card: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 16,
    padding: 16,
    boxShadow: "0 1px 2px rgba(0,0,0,0.03)",
  },
  cardTitle: { fontSize: 12, color: "#6b7280", marginBottom: 6 },
  cardValue: { fontSize: 22, fontWeight: 800, color: "#0f172a" },
  section: { marginTop: 28 },

  // 섹션 타이틀 + 우측 검색창 정렬
  sectionHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
    gap: 12,
  },

  sectionTitle: { fontSize: 16, fontWeight: 800, margin: 0, color: "#0f172a" },
  badgeWrap: { display: "flex", flexWrap: "wrap" },

  // 검색 X 버튼
  clearBtn: {
    position: "absolute",
    right: 6,
    top: 6,
    width: 20,
    height: 20,
    borderRadius: 999,
    border: "1px solid #e5e7eb",
    background: "#fff",
    cursor: "pointer",
    lineHeight: "16px",
    fontSize: 14,
  },

  // 카드형 목록 레이아웃
  timelineGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0,1fr))",
    gap: 12,
  },
};
