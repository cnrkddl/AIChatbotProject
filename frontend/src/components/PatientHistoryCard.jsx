import React from "react";

/**
 * PatientHistoryCard
 * - 한 날짜의 간호기록(items)을 카드로 표시
 *
 * props:
 *  - date: "YYYY-MM-DD"
 *  - items: Array<{ keyword?: string, detail?: string }>
 *  - keywordColor: Record<string, string>
 *  - highlightQuery?: string   // 검색어 하이라이트
 */
export default function PatientHistoryCard({
  date,
  items = [],
  keywordColor = {},
  highlightQuery = "",
}) {
  const grouped = groupByKeyword(items);

  return (
    <div style={S.card}>
      <div style={S.header}>
        <div style={S.date}>{formatDate(date)}</div>
        <div style={S.count}>{items.length}건</div>
      </div>

      {items.length === 0 ? (
        <div style={S.empty}>항목 없음</div>
      ) : (
        <div style={S.body}>
          {Object.entries(grouped).map(([kw, arr]) => {
            const color = keywordColor[kw] || keywordColor["기타"] || "#64748b";
            return (
              <div key={kw} style={S.group}>
                <span
                  style={{
                    ...S.kwPill,
                    color,
                    background: `${color}20`,
                    border: `1px solid ${color}40`,
                  }}
                >
                  {kw} <span style={S.kwCount}>{arr.length}</span>
                </span>
                <ul style={S.list}>
                  {arr.map((it, i) => (
                    <li key={`${kw}-${i}`} style={S.item}>
                      {it.detail === "호전됨" ? (
                        <span style={S.improve}>
                          <span style={S.improveDot} />
                          호전됨
                        </span>
                      ) : (
                        renderHighlighted(it.detail || "-", highlightQuery)
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

/* ===== Utils ===== */

function groupByKeyword(items) {
  const out = {};
  for (const it of items) {
    const k = it.keyword || "기타";
    (out[k] ||= []).push(it);
  }
  return out;
}

function formatDate(d) {
  if (!d) return "-";
  try {
    const dt = new Date(d);
    const y = dt.getFullYear();
    const m = `${dt.getMonth() + 1}`.padStart(2, "0");
    const day = `${dt.getDate()}`.padStart(2, "0");
    return `${y}.${m}.${day}`;
  } catch {
    return d;
  }
}

function renderHighlighted(text, q) {
  if (!q) return text;
  const idx = text.toLowerCase().indexOf(q.toLowerCase());
  if (idx === -1) return text;
  const before = text.slice(0, idx);
  const match = text.slice(idx, idx + q.length);
  const after = text.slice(idx + q.length);
  return (
    <>
      {before}
      <mark style={{ padding: 0, backgroundColor: "#dbeafe", color: "#1e40af" }}>{match}</mark>
      {renderHighlighted(after, q)}
    </>
  );
}

/* ===== Styles ===== */

const S = {
  card: {
    background: "#fff",
    border: "1px solid #e5e7eb",
    borderRadius: 16,
    padding: 14,
    boxShadow: "0 1px 2px rgba(0,0,0,0.03)",
  },
  header: {
    display: "flex",
    alignItems: "baseline",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  date: { fontSize: 16, fontWeight: 800, color: "#0f172a" },
  count: { fontSize: 12, color: "#64748b" },
  empty: {
    padding: 12,
    textAlign: "center",
    color: "#94a3b8",
    background: "#f8fafc",
    borderRadius: 12,
    border: "1px dashed #e5e7eb",
  },
  body: { display: "grid", gap: 10 },
  group: {
    border: "1px solid #e5e7eb",
    borderRadius: 12,
    padding: 10,
    background: "#fafafa",
  },
  kwPill: {
    display: "inline-block",
    fontSize: 12,
    fontWeight: 800,
    padding: "4px 8px",
    borderRadius: 999,
    marginBottom: 8,
  },
  kwCount: { fontWeight: 700, marginLeft: 6, opacity: 0.8 },
  list: { margin: 0, paddingLeft: 18 },
  item: { margin: "4px 0", color: "#0f172a", fontSize: 14, lineHeight: 1.5 },

  // '호전됨' 특별 표시
  improve: {
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
    padding: "2px 8px",
    fontSize: 12,
    fontWeight: 800,
    color: "#166534",
    background: "#dcfce7",
    border: "1px solid #86efac",
    borderRadius: 999,
  },
  improveDot: {
    width: 6,
    height: 6,
    borderRadius: 99,
    background: "#22c55e",
    display: "inline-block",
  },
};
