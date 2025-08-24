// src/pages/LoginPage.jsx
import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const API_BASE = process.env.REACT_APP_API_BASE || 'https://aichatbotproject.onrender.com';

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // 1) 페이지 진입 시: ?login=success 있으면 즉시 홈으로
  useEffect(() => {
    const params = new URLSearchParams(location.search || window.location.search || "");
    if (params.get("login") === "success") {
      navigate("/home", { replace: true });
    }
  }, [location, navigate]);

  // 2) 로그인 상태면 홈으로 (쿠키 이미 있으면 빠르게 통과)
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/kakao/whoami`, {
          credentials: "include",
        });
        const me = await res.json();
        if (!alive) return;
        if (me?.logged_in) {
          navigate("/home", { replace: true });
        }
      } catch (err) {
        console.warn("[whoami] failed:", err);
      }
    })();
    return () => { alive = false; };
  }, [navigate, API_BASE]); // ✅ API_BASE 추가

  const handleKakaoLogin = () => {
    setLoading(true);
    // 페이지 이동이어야 함 (fetch X)
    window.location.assign(`${API_BASE}/auth/kakao/login`);
  };

  return (
    <div style={styles.wrap}>
      <div style={styles.backgroundDecoration}>
        <div style={styles.circle1}></div>
        <div style={styles.circle2}></div>
        <div style={styles.circle3}></div>
      </div>

      <div style={styles.card}>
        <div style={styles.logoContainer}>
          <img
            src="https://search.pstatic.net/sunny/?src=https%3A%2F%2Flh3.googleusercontent.com%2FvIEP7BRkOXpvJCTKH6c_zs78w2CfZer0fSrkkBN_zhYr4WF9o9H5ffJ23IGisjW45w%3Dh500&type=sc960_832"
            alt="효림의료재단 로고"
            style={styles.logo}
          />
        </div>

        <div style={styles.content}>
          <h1 style={styles.title}>효림요양병원</h1>
          <h2 style={styles.subtitle}>AI 챗봇 서비스</h2>
          <p style={styles.description}>
            환자 상태 확인부터 상담까지<br />
            언제든 편리하게 이용하세요
          </p>

          <button
            onClick={handleKakaoLogin}
            style={{ ...styles.kakaoBtn, opacity: loading ? 0.7 : 1, pointerEvents: loading ? "none" : "auto" }}
            disabled={loading}
          >
            {loading ? (
              <div style={styles.loadingContent}>
                <div style={styles.spinner}></div>
                <span>카카오 연결 중...</span>
              </div>
            ) : (
              <div style={styles.btnContent}>
                <span style={styles.kakaoIcon}>💬</span>
                <span>카카오로 시작하기</span>
              </div>
            )}
          </button>

          <div style={styles.features}>
            <div style={styles.feature}>
              <span style={styles.featureIcon}>🔒</span>
              <span>안전한 인증</span>
            </div>
            <div style={styles.feature}>
              <span style={styles.featureIcon}>😊</span>
              <span>친절한 응답</span>
            </div>
            <div style={styles.feature}>
              <span style={styles.featureIcon}>📱</span>
              <span>쉬운 사용</span>
            </div>
          </div>
        </div>
      </div>

      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
          }
          .card {
            animation: float 3s ease-in-out infinite;
          }
        `}
      </style>
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
    paddingTop: "5vh",
  },
  backgroundDecoration: {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    overflow: "hidden",
    zIndex: -1,
  },
  circle1: { position: "absolute", width: 300, height: 300, borderRadius: "50%", background: "rgba(255,255,255,0.1)", top: -50, left: -100 },
  circle2: { position: "absolute", width: 200, height: 200, borderRadius: "50%", background: "rgba(255,255,255,0.08)", bottom: 100, right: 100 },
  circle3: { position: "absolute", width: 150, height: 150, borderRadius: "50%", background: "rgba(255,255,255,0.05)", top: 300, left: "50%", transform: "translateX(-50%)" },
  card: {
    width: 360,
    background: "#fff",
    borderRadius: 16,
    boxShadow: "0 8px 24px rgba(0,0,0,0.08)",
    padding: 20,
    position: "relative",
    zIndex: 1,
    textAlign: "center",
  },
  logoContainer: { textAlign: "center", marginBottom: 8 },
  logo: { width: 80, height: 80, objectFit: "contain" },
  content: { textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", marginTop: -5 },
  title: { fontSize: "2.2rem", fontWeight: 700, marginBottom: 4, color: "#333", textAlign: "center", width: "100%" },
  subtitle: { fontSize: "1.1rem", color: "#666", marginBottom: 8, textAlign: "center", width: "100%" },
  description: { fontSize: "0.85rem", color: "#999", marginBottom: 20, lineHeight: 1.5, textAlign: "center", width: "100%" },
  kakaoBtn: { width: "100%", height: 44, borderRadius: 10, border: "1px solid #FEE500", background: "#FEE500", fontWeight: 700, cursor: "pointer", marginTop: 10, display: "flex", alignItems: "center", justifyContent: "center", gap: 8 },
  loadingContent: { display: "flex", alignItems: "center", gap: 8 },
  spinner: { border: "2px solid #f3f3f3", borderTop: "2px solid #FEE500", borderRadius: "50%", width: 18, height: 18, animation: "spin 1s linear infinite" },
  btnContent: { display: "flex", alignItems: "center", gap: 8 },
  kakaoIcon: { fontSize: "1.2rem" },
  features: { display: "flex", justifyContent: "space-around", marginTop: 15, padding: "0 10px" },
  feature: { display: "flex", alignItems: "center", gap: 8, color: "#666" },
  featureIcon: { fontSize: "1rem" },
};
