// src/routes/Router.jsx
import React from "react";
import { HashRouter, Routes, Route } from "react-router-dom";

import LoginPage from "../pages/LoginPage";
import HomePage from "../pages/HomePage";
import ChatBotPage from "../pages/ChatBotPage";
import PatientInfoPage from "../pages/PatientInfoPage";
import FeedbackPage from "../pages/FeedbackPage";

export default function AppRouter() {
  return (
    // ✅ GitHub Pages는 HashRouter 사용
    <HashRouter>
      <Routes>
        {/* 최초 진입은 로그인 페이지 */}
        <Route path="/" element={<LoginPage />} />

        {/* 로그인 후 이동할 페이지 */}
        <Route path="/home" element={<HomePage />} />

        {/* 기타 페이지들 */}
        <Route path="/chat" element={<ChatBotPage />} />
        <Route path="/patient-info" element={<PatientInfoPage />} />
        <Route path="/feedback" element={<FeedbackPage />} />

        {/* 잘못된 경로 -> 로그인으로 */}
        <Route path="*" element={<LoginPage />} />
      </Routes>
    </HashRouter>
  );
}
