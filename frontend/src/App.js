// src/App.js
import React, { useEffect, useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import ChatBotPage from "./pages/ChatBotPage";
import FeedbackPage from "./pages/FeedbackPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import PatientInfoPage from "./pages/PatientInfoPage";

// 배포/로컬 자동 스위칭 (github.io면 Render로)
const API_BASE = (
  process.env.REACT_APP_API_BASE ||
  (typeof window !== "undefined" && window.location.hostname.endsWith("github.io")
    ? "https://aichatbotproject.onrender.com"
    : "http://localhost:8000")
).replace(/\/+$/, "");

export default function App() {
  const [authChecked, setAuthChecked] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // 앱 최초 로드 시 세션 확인 → 새로고침/직접접속 시에도 로그인 유지
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/session`, {
          credentials: "include",
        });
        const data = await res.json().catch(() => ({}));
        setIsLoggedIn(!!data?.ok);
      } catch {
        setIsLoggedIn(false);
      } finally {
        setAuthChecked(true);
      }
    })();
  }, []);

  if (!authChecked) return <div style={{ padding: 24 }}>Loading...</div>;

  return (
    // GH Pages 하위 경로
    <Router basename="/AIChatbotProject">
      <Routes>
        {!isLoggedIn ? (
          <>
            {/* 로그인 전: 로그인 페이지만 노출 */}
            <Route
              path="/"
              element={<LoginPage onLogin={() => setIsLoggedIn(true)} />}
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </>
        ) : (
          <>
            {/* 로그인 후: /와 /home 둘 다 홈으로 매핑 */}
            <Route path="/" element={<HomePage />} />
            <Route path="/home" element={<HomePage />} />

            <Route path="/chat" element={<ChatBotPage />} />
            {/* /patient는 기본 환자ID로 리다이렉트(원하면 수정) */}
            <Route
              path="/patient"
              element={<Navigate to="/patient/25-0000032" replace />}
            />
            <Route path="/patient/:patientId" element={<PatientInfoPage />} />
            <Route path="/feedback" element={<FeedbackPage />} />

            <Route path="*" element={<Navigate to="/" replace />} />
          </>
        )}
      </Routes>
    </Router>
  );
}
