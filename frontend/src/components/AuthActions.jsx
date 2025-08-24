// src/components/AuthActions.jsx
import React from "react";

export default function AuthActions({ loggedIn, onLogout, onUnlink, onDone }) {
  const API_BASE =
    (process.env.REACT_APP_API_BASE &&
      process.env.REACT_APP_API_BASE.replace(/\/+$/, "")) ||
    "https://aichatbotproject.onrender.com";

  const call = async (path, method = "POST") => {
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        method,
        credentials: "include",
      });
      return res.ok;
    } catch (e) {
      console.error(path, e);
      return false;
    } finally {
      onDone && onDone();
    }
  };

  const handleLogout = async () => {
    await call("/auth/kakao/logout", "POST");
    onLogout && onLogout();
  };

  const handleUnlink = async () => {
    await call("/auth/kakao/unlink", "POST");
    onUnlink && onUnlink();
  };

  if (!loggedIn) return null;

  return (
    <div style={{ display: "flex", gap: 8 }}>
      <button
        onClick={handleLogout}
        style={{
          height: 36,
          padding: "0 12px",
          borderRadius: 18,
          border: "1px solid #e9ecef",
          background: "#fff",
          fontWeight: 600,
          cursor: "pointer",
        }}
      >
        로그아웃
      </button>
      <button
        onClick={handleUnlink}
        style={{
          height: 36,
          padding: "0 12px",
          borderRadius: 18,
          border: "1px solid #e03131",
          background: "#fff5f5",
          color: "#e03131",
          fontWeight: 700,
          cursor: "pointer",
        }}
      >
        연결해제
      </button>
    </div>
  );
}
