// src/components/AuthActions.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8001";

/**
 * 로그아웃(세션만 종료) / 연결해제(카카오-앱 연결 자체 해제) 버튼
 * - 성공 시 로그인 페이지로 이동
 * - fetch 요청에는 credentials: "include" 필수(세션 쿠키 사용)
 * - 백엔드가 GET만 받으면 method: "GET" 그대로 사용
 *   (POST로만 받게 해두었으면 method를 "POST"로 바꾸세요)
 */
export default function AuthActions() {
  const navigate = useNavigate();
  const [busy, setBusy] = useState(false);

  const call = async (path /* '/logout' | '/unlink' */) => {
    if (busy) return;
    setBusy(true);
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method: "GET", // ← 백엔드가 GET 라우트라면 이대로. POST만 받으면 "POST"로 바꾸세요.
        credentials: "include",
      });
      try {
        await res.text();
      } catch (_) {}
      navigate("/login", { replace: true });
    } catch (err) {
      console.error(err);
      alert("요청 중 문제가 발생했어요. 콘솔을 확인해주세요.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={styles.wrap}>
      <button
        style={styles.lightBtn}
        onClick={() => call("/logout")}
        disabled={busy}
        title="세션만 종료 (다음 로그인 시 동의창은 안 뜰 수 있어요)"
      >
        {busy ? "처리 중..." : "로그아웃"}
      </button>

      <button
        style={styles.dangerBtn}
        onClick={() => call("/unlink")}
        disabled={busy}
        title="카카오-앱 연결 해제 (다음 로그인 시 동의창이 다시 뜹니다)"
      >
        {busy ? "처리 중..." : "연결해제"}
      </button>
    </div>
  );
}

const styles = {
  wrap: { display: "flex", gap: 8, alignItems: "center" },
  lightBtn: {
    padding: "10px 14px",
    borderRadius: 10,
    border: "1px solid #ddd",
    background: "#fff",
    cursor: "pointer",
    fontWeight: 600,
  },
  dangerBtn: {
    padding: "10px 14px",
    borderRadius: 10,
    border: "1px solid #d33",
    background: "#ffefef",
    color: "#a00",
    cursor: "pointer",
    fontWeight: 700,
  },
};
