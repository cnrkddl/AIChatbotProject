// src/routes/Router.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// 페이지 컴포넌트 경로는 프로젝트 구조에 맞게 조정하세요.
import LoginPage       from '../pages/LoginPage';
import HomePage        from '../pages/HomePage';
import ChatBotPage     from '../pages/ChatBotPage';
import PatientInfoPage from '../pages/PatientInfoPage';
import FeedbackPage    from '../pages/FeedbackPage';

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 기본 진입은 /login */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        <Route path="/login"        element={<LoginPage />} />
        <Route path="/home"         element={<HomePage />} />
        <Route path="/chat"         element={<ChatBotPage />} />
        <Route path="/patient-info" element={<PatientInfoPage />} />
        <Route path="/feedback"     element={<FeedbackPage />} />

        {/* 없는 경로는 /login 으로 */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
