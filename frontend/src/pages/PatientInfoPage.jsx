// src/pages/PatientInfoPage.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import Header from "../components/Header";
import HistorySection from "../components/HistorySection"; // 독립 컴포넌트 사용

// 키워드 → 색상 (배지/칩용)
const KEYWORD_COLORS = {
  발열: "#ffebee",
  가래: "#e3f2fd",
  자가배뇨: "#e8f5e9",
  수면: "#fff8e1",
  욕창: "#f3e5f5",
  통증: "#fff3e0",
  식사: "#e8f5e9",
  산소: "#e0f2fe",
  기타: "#f5f5f5",
  _default: "#f5f5f5",
};

// 간단 텍스트 정리
function sanitize(s) {
  return String(s || "").replace(/\s+/g, " ").replace(/^[-*•]\s*/, "").trim();
}

export default function PatientInfoPage() {
  // URL의 :patientId 사용(없으면 기본값)
  const { patientId: routePatientId } = useParams();
  const [patientId, setPatientId] = useState(routePatientId || "25-0000032");

  const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8001";

  const [notes, setNotes] = useState([]); // [{date, items:[{keyword, detail}]}]
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedDate, setSelectedDate] = useState("");

  // 데이터 로드
  useEffect(() => {
    let ignore = false;
    (async () => {
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
          setNotes(Array.isArray(data) ? data : []);
          setSelectedDate(Array.isArray(data) && data.length ? data[data.length - 1].date : "");
        }
      } catch (e) {
        if (!ignore) setError(e.message || "불러오기에 실패했습니다.");
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => {
      ignore = true;
    };
  }, [API_BASE, patientId]);

  // 날짜 목록 / 선택 날짜 항목 / 키워드 통계
  const dates = useMemo(() => notes.map((n) => n.date), [notes]);
  const selectedItems = useMemo(() => {
    const day = notes.find((n) => n.date === selectedDate);
    return day?.items || [];
  }, [notes, selectedDate]);
  const keywordStats = useMemo(() => {
    const counts = {};
    for (const d of notes) for (const it of d.items || []) {
      const k = it.keyword || "기타";
      counts[k] = (counts[k] || 0) + 1;
    }
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([k, v]) => ({ keyword: k, count: v }));
  }, [notes]);

  return (
    <div style={styles.page}>
      <Header />

      <div style={styles.container}>
        {/* 상단 */}
        <div style={styles.topBar}>
          <div style={styles.titleWrap}>
            <h2 style={styles.title}>환자 상태 정보</h2>
            <p style={styles.subtitle}>간호기록지 특이사항을 날짜별로 확인합니다.</p>
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

        {/* 상태 표시 */}
        {loading && <div style={styles.stateBox}>불러오는 중…</div>}
        {!!error && !loading && (
          <div style={{ ...styles.stateBox, color: "#ef4444" }}>에러: {error}</div>
        )}
        {!loading && !error && notes.length === 0 && (
          <div style={styles.stateBox}>표시할 간호기록이 없습니다.</div>
        )}

        {/* 데이터 표시 */}
        {!loading && !error && notes.length > 0 && (
          <>
            {/* 요약 카드 */}
            <div style={styles.cardsGrid}>
              <SummaryCard title="총 기록 일수" value={`${notes.length}일`} />
              <SummaryCard title="키워드 종류" value={`${keywordStats.length}개`} />
              <SummaryCard title="가장 최근 날짜" value={notes[notes.length - 1]?.date || "-"} />
            </div>

            {/* 키워드 요약 */}
            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>키워드 요약</h3>
              <div style={styles.badgeWrap}>
                {keywordStats.length === 0 && <span>— 없음 —</span>}
                {keywordStats.map(({ keyword, count }) => (
                  <Badge
                    key={keyword}
                    text={`${keyword} ${count}`}
                    color={KEYWORD_COLORS[keyword] || KEYWORD_COLORS["기타"]}
                  />
                ))}
              </div>
            </div>

            {/* 선택 날짜 상세 */}
            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>{selectedDate || "날짜 선택"}</h3>
              <div style={styles.list}>
                {selectedItems.length === 0 && <div style={styles.muted}>항목 없음</div>}
                {selectedItems.map((it, idx) => (
                  <div key={idx} style={styles.itemRow}>
                    <span
                      style={{
                        ...styles.itemKeyword,
                        background:
                          (KEYWORD_COLORS[it.keyword] || KEYWORD_COLORS._default) + "80",
                        color: "#111",
                      }}
                    >
                      {it.keyword || "기타"}
                    </span>
                    <span style={styles.itemDetail}>{sanitize(it.detail)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* 전체 히스토리: 독립 컴포넌트 사용 (검색/역순/카드 스타일) */}
            <HistorySection notes={notes} />
          </>
        )}
      </div>
    </div>
  );
}

/* 서브 컴포넌트 */
function SummaryCard({ title, value }) {
  return (
    <div style={styles.card}>
      <div style={styles.cardTitle}>{title}</div>
      <div style={styles.cardValue}>{value}</div>
    </div>
  );
}
function Badge({ text, color = "#f5f5f5" }) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "6px 10px",
        borderRadius: 999,
        background: color,
        color: "#1f1f1f",
        fontSize: 13,
        fontWeight: 600,
        margin: "4px 8px 4px 0",
        border: "1px solid rgba(0,0,0,0.05)",
      }}
    >
      {text}
    </span>
  );
}

/* 스타일 */
const styles = {
  page: { minHeight: "100vh", background: "#f8fafc" },
  container: { maxWidth: 1100, margin: "0 auto", padding: "20px 16px 48px" },
  topBar: {
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "space-between",
    gap: 16,
    margin: "12px 0 20px",
  },
  titleWrap: { maxWidth: 640 },
  title: { margin: 0, fontSize: 24, fontWeight: 800, color: "#0f172a" },
  subtitle: { margin: "6px 0 0", color: "#475569" },
  controls: { display: "flex", gap: 12, flexWrap: "wrap" },
  label: { display: "flex", flexDirection: "column", fontSize: 13, color: "#334155" },
  input: {
    height: 38, border: "1px solid #e5e7eb", borderRadius: 10, padding: "0 12px",
    minWidth: 180, outline: "none",
  },
  select: {
    height: 38, border: "1px solid #e5e7eb", borderRadius: 10, padding: "0 12px",
    minWidth: 160, outline: "none", background: "#fff",
  },
  stateBox: {
    background: "#fff", border: "1px dashed #e5e7eb", borderRadius: 14,
    padding: 18, textAlign: "center", color: "#334155",
  },
  cardsGrid: {
    display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12, marginTop: 8,
  },
  card: {
    background: "#fff", border: "1px solid #e5e7eb", borderRadius: 16,
    padding: 16, boxShadow: "0 1px 2px rgba(0,0,0,0.03)",
  },
  cardTitle: { fontSize: 12, color: "#6b7280", marginBottom: 6 },
  cardValue: { fontSize: 22, fontWeight: 800, color: "#0f172a" },
  section: { marginTop: 28 },
  sectionTitle: { fontSize: 16, fontWeight: 800, margin: "0 0 10px", color: "#0f172a" },
  badgeWrap: { display: "flex", flexWrap: "wrap" },

  list: { background: "#fff", border: "1px solid #e5e7eb", borderRadius: 14, padding: 12 },
  itemRow: {
    display: "flex", alignItems: "center", gap: 10, padding: "8px 6px",
    borderBottom: "1px solid #f1f5f9",
  },
  itemKeyword: { fontSize: 12, padding: "4px 8px", borderRadius: 999, fontWeight: 700 },
  itemDetail: { fontSize: 14, color: "#0f172a" },
  muted: { color: "#64748b" },
};
