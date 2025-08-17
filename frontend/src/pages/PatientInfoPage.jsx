import React, { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import Header from "../components/Header"; // 프로젝트에 이미 있는 헤더 사용

export default function PatientInfoPage() {
  const { patientId: routePatientId } = useParams();
  const [patientId, setPatientId] = useState(routePatientId || "25-0000032");

  const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8001";

  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedDate, setSelectedDate] = useState("");

  const keywordColor = useMemo(
    () => ({
      발열: "#ef4444",
      가래: "#06b6d4",
      자가배뇨: "#8b5cf6",
      욕창: "#f59e0b",
      통증: "#f97316",
      식사: "#22c55e",
      수면: "#3b82f6",
      산소: "#0ea5e9",
      기타: "#64748b",
    }),
    []
  );

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
          setNotes(Array.isArray(data) ? data : []);
          if (Array.isArray(data) && data.length > 0) {
            setSelectedDate(data[data.length - 1].date);
          } else {
            setSelectedDate("");
          }
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

  const dates = useMemo(() => notes.map((n) => n.date), [notes]);

  const selectedItems = useMemo(() => {
    const day = notes.find((n) => n.date === selectedDate);
    return day?.items || [];
  }, [notes, selectedDate]);

  const keywordStats = useMemo(() => {
    const counts = {};
    for (const d of notes) {
      for (const it of d.items || []) {
        const k = it.keyword || "기타";
        counts[k] = (counts[k] || 0) + 1;
      }
    }
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([k, v]) => ({ keyword: k, count: v }));
  }, [notes]);

  return (
    <div style={styles.page}>
      <Header />

      <div style={styles.container}>
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

        {loading && <div style={styles.stateBox}>불러오는 중…</div>}
        {!!error && !loading && (
          <div style={{ ...styles.stateBox, color: "#ef4444" }}>에러: {error}</div>
        )}
        {!loading && !error && notes.length === 0 && (
          <div style={styles.stateBox}>표시할 간호기록이 없습니다.</div>
        )}

        {!loading && !error && notes.length > 0 && (
          <>
            <div style={styles.cardsGrid}>
              <SummaryCard title="총 기록 일수" value={`${notes.length}일`} />
              <SummaryCard title="키워드 종류" value={`${keywordStats.length}개`} />
              <SummaryCard
                title="가장 최근 날짜"
                value={notes[notes.length - 1]?.date || "-"}
              />
            </div>

            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>키워드 요약</h3>
              <div style={styles.badgeWrap}>
                {keywordStats.length === 0 && <span>— 없음 —</span>}
                {keywordStats.map(({ keyword, count }) => (
                  <Badge key={keyword} text={`${keyword} ${count}`} color={keywordColor[keyword] || keywordColor["기타"]} />
                ))}
              </div>
            </div>

            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>{selectedDate || "날짜 선택"}</h3>
              <div style={styles.list}>
                {selectedItems.length === 0 && <div style={styles.muted}>항목 없음</div>}
                {selectedItems.map((it, idx) => (
                  <div key={idx} style={styles.itemRow}>
                    <span style={{ ...styles.itemKeyword, background: (keywordColor[it.keyword] || keywordColor["기타"]) + "20" , color: keywordColor[it.keyword] || keywordColor["기타"] }}>
                      {it.keyword || "기타"}
                    </span>
                    <span style={styles.itemDetail}>{it.detail}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* 전체 히스토리 (최신이 위로 오도록 역순 정렬) */}
            <div style={styles.section}>
              <h3 style={styles.sectionTitle}>전체 히스토리</h3>
              <div style={styles.timeline}>
                {[...notes].reverse().map((d) => (
                  <div key={d.date} style={styles.dayCard}>
                    <div style={styles.dayHeader}>
                      <strong>{d.date}</strong>
                      <small style={styles.smallMuted}>{d.items?.length || 0}건</small>
                    </div>
                    <ul style={styles.ul}>
                      {(d.items || []).map((it, i) => (
                        <li key={`${d.date}-${i}`} style={styles.li}>
                          <b>{it.keyword || "기타"}</b> — {it.detail}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function SummaryCard({ title, value }) {
  return (
    <div style={styles.card}>
      <div style={styles.cardTitle}>{title}</div>
      <div style={styles.cardValue}>{value}</div>
    </div>
  );
}

function Badge({ text, color = "#64748b" }) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "6px 10px",
        borderRadius: 999,
        background: `${color}20`,
        color,
        fontSize: 13,
        fontWeight: 600,
        margin: "4px 8px 4px 0",
      }}
    >
      {text}
    </span>
  );
}

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
  sectionTitle: { fontSize: 16, fontWeight: 800, margin: "0 0 10px", color: "#0f172a" },
  badgeWrap: { display: "flex", flexWrap: "wrap" },
  list: { background: "#fff", border: "1px solid #e5e7eb", borderRadius: 14, padding: 12 },
  itemRow: { display: "flex", alignItems: "center", gap: 10, padding: "8px 6px", borderBottom: "1px solid #f1f5f9" },
  itemKeyword: {
    fontSize: 12,
    padding: "4px 8px",
    borderRadius: 999,
    fontWeight: 700,
  },
  itemDetail: { fontSize: 14, color: "#0f172a" },
  muted: { color: "#64748b" },
  smallMuted: { color: "#94a3b8" },
  timeline: { display: "grid", gridTemplateColumns: "repeat(2, minmax(0,1fr))", gap: 12 },
  dayCard: { background: "#fff", border: "1px solid #e5e7eb", borderRadius: 14, padding: 12 },
  dayHeader: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 },
  ul: { margin: 0, paddingLeft: 18 },
  li: { margin: "6px 0" },
};
