// src/components/HistorySection.jsx
import React, { useMemo, useState } from "react";

const KEYWORD_COLORS = {
  "발열":      "#ffebee",
  "가래":      "#e3f2fd",
  "자가배뇨":   "#e8f5e9",
  "수면":      "#fff8e1",
  "욕창":      "#f3e5f5",
  // 기본값
  "_default":  "#f5f5f5",
};

function formatKoreanDate(iso) {
  // iso: "2025-07-25"
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const yoil = ["일","월","화","수","목","금","토"][d.getDay()];
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")} (${yoil})`;
}

export default function HistorySection({ notes }) {
  const [query, setQuery] = useState("");

  // 최신일자가 위로 오도록 정렬 + 검색 필터
  const filtered = useMemo(() => {
    const q = query.trim();
    const base = Array.isArray(notes) ? [...notes] : [];
    base.sort((a, b) => (a.date < b.date ? 1 : -1));
    if (!q) return base;
    return base.filter(day =>
      day.items?.some(it =>
        (it.keyword || "").includes(q) || (it.detail || "").includes(q)
      )
    );
  }, [notes, query]);

  return (
    <section style={styles.wrap}>
      <div style={styles.toolbar}>
        <h3 style={styles.title}>전체 히스토리</h3>
        <div style={styles.searchBox}>
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="키워드/내용 검색 (예: 발열, 가래)"
            style={styles.searchInput}
          />
        </div>
      </div>

      <div style={styles.grid}>
        {filtered.map((day) => (
          <DayCard key={day.date} day={day} />
        ))}
      </div>
    </section>
  );
}

function DayCard({ day }) {
  const count = day.items?.length || 0;

  return (
    <article style={styles.card}>
      <header style={styles.cardHeader}>
        <div style={styles.dateGroup}>
          <div style={styles.dateText}>{formatKoreanDate(day.date)}</div>
          <span style={styles.countBadge}>{count}건</span>
        </div>
      </header>

      <ul style={styles.itemList}>
        {day.items?.map((it, idx) => (
          <li key={idx} style={styles.itemRow}>
            <span
              style={{
                ...styles.keywordPill,
                background: KEYWORD_COLORS[it.keyword] || KEYWORD_COLORS._default
              }}
              title={it.keyword}
            >
              {it.keyword}
            </span>
            <span style={styles.detailText}>{sanitize(it.detail)}</span>
          </li>
        ))}
      </ul>
    </article>
  );
}

// 간단한 방어 (PDF 파싱에서 붙은 별/공백 등을 정리)
function sanitize(s) {
  return String(s || "")
    .replace(/\s+/g, " ")
    .replace(/^[-*•]\s*/, "")  // 맨 앞 불릿 정리
    .trim();
}

const styles = {
  wrap: {
    marginTop: 24
  },
  toolbar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 12
  },
  title: {
    margin: 0,
    fontSize: 18,
    fontWeight: 700,
    color: "#222"
  },
  searchBox: {
    display: "flex",
    alignItems: "center",
    gap: 8
  },
  searchInput: {
    width: 260,
    padding: "10px 12px",
    borderRadius: 10,
    border: "1px solid #e0e0e0",
    outline: "none",
    fontSize: 14,
    background: "#fff",
    transition: "box-shadow .15s ease, border-color .15s ease",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))",
    gap: 16
  },
  card: {
    background: "#fff",
    border: "1px solid #eee",
    borderRadius: 14,
    padding: 14,
    boxShadow: "0 4px 10px rgba(0,0,0,.04)",
    transition: "transform .12s ease, box-shadow .12s ease",
    cursor: "default"
  },
  cardHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    paddingBottom: 8,
    borderBottom: "1px dashed #f0f0f0",
    marginBottom: 8
  },
  dateGroup: {
    display: "flex",
    alignItems: "center",
    gap: 10
  },
  dateText: {
    fontWeight: 700,
    color: "#111",
    letterSpacing: 0.2
  },
  countBadge: {
    fontSize: 12,
    padding: "2px 8px",
    borderRadius: 999,
    background: "#f6f7f9",
    border: "1px solid #e9eaee",
    color: "#666"
  },
  itemList: {
    listStyle: "none",
    padding: 0,
    margin: 0,
    display: "flex",
    flexDirection: "column",
    gap: 10
  },
  itemRow: {
    display: "grid",
    gridTemplateColumns: "120px 1fr",
    alignItems: "start",
    gap: 10
  },
  keywordPill: {
    display: "inline-block",
    padding: "6px 10px",
    borderRadius: 10,
    fontSize: 13,
    fontWeight: 700,
    color: "#1f1f1f",
    border: "1px solid rgba(0,0,0,0.05)",
    boxShadow: "inset 0 1px 0 rgba(255,255,255,.6)"
  },
  detailText: {
    color: "#333",
    lineHeight: 1.5,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word"
  }
};
