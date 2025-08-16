// src/App.js
import React, { useState } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from 'react-router-dom';

import LoginPage       from './pages/LoginPage';
import HomePage        from './pages/HomePage';
import ChatBotPage     from './pages/ChatBotPage';
import PatientInfoPage from './pages/PatientInfoPage';
import FeedbackPage    from './pages/FeedbackPage';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  return (
    <Router>
      <Routes>
        {!isLoggedIn ? (
          // 로그인 전: 로그인 페이지로 고정
          <>
            <Route
              path="/"
              element={<LoginPage onLogin={() => setIsLoggedIn(true)} />}
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </>
        ) : (
          // 로그인 후 접근 가능 라우트
          <>
            <Route path="/" element={<HomePage />} />
            <Route path="/chat" element={<ChatBotPage />} />
            {/* 기본 /patient 접근 시 기본 환자번호로 리다이렉트 */}
            <Route path="/patient" element={<Navigate to="/patient/25-0000032" replace />} />
            {/* 환자번호 파라미터 라우트 */}
            <Route path="/patient/:patientId" element={<PatientInfoPage />} />
            <Route path="/feedback" element={<FeedbackPage />} />
            {/* 나머지는 홈으로 */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </>
        )}
      </Routes>
    </Router>
  );
}
