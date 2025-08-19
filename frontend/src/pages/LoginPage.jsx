// src/pages/LoginPage.jsx
import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8001";

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // 카카오 인증 후 ?login=success(또는 login%3Dsuccess) 감지 → /home 이동
  useEffect(() => {
    const raw = location.search || window.location.search || "";
    if (raw.includes("login=success") || raw.includes("login%3Dsuccess")) {
      navigate("/home", { replace: true });
    }
  }, [location, navigate]);

  const handleKakaoLogin = () => {
    setLoading(true);
    const next = "/login?login=success";           // 프론트로 돌아올 경로
    const encodedNext = encodeURIComponent(next);  // 반드시 전체 인코딩
    window.location.href = `${API_BASE}/authorize?next=${encodedNext}`;
  };

  return (
    <div style={styles.wrap}>
      <div style={styles.card}>
        <h2 style={{ margin: 0 }}>로그인</h2>
        <p style={{ color: "#666" }}>카카오로 안전하게 로그인하세요.</p>
        <button
          onClick={handleKakaoLogin}
          style={styles.kakaoBtn}
          disabled={loading}
        >
          {loading ? "카카오 연결 중..." : "카카오로 로그인"}
        </button>
      </div>
    </div>
  );
}

const styles = {
  wrap: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#f7f7f9",
    padding: 24,
  },
  card: {
    width: 360,
    background: "#fff",
    borderRadius: 16,
    boxShadow: "0 8px 24px rgba(0,0,0,0.08)",
    padding: 24,
  },
  kakaoBtn: {
    width: "100%",
    height: 48,
    borderRadius: 10,
    border: "1px solid #FEE500",
    background: "#FEE500",
    fontWeight: 700,
    cursor: "pointer",
    marginTop: 12,
  },
};
