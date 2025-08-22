// src/components/Header.jsx
import React from "react";
import { useNavigate, useLocation } from "react-router-dom";

const API_BASE = process.env.REACT_APP_API_BASE || "https://aichatbotproject.onrender.com";

export default function Header() {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE}/logout`, {
        method: "GET",
        credentials: "include", // ★ 쿠키 동반
      });
    } catch (e) {
      console.error(e);
    } finally {
      // 프론트 로컬 상태 초기화 후 로그인 페이지로
      window.localStorage.clear();
      navigate("/", { replace: true });
    }
  };

  const handleUnlink = async () => {
    try {
      await fetch(`${API_BASE}/unlink`, {
        method: "GET",
        credentials: "include",
      });
    } catch (e) {
      console.error(e);
    } finally {
      window.localStorage.clear();
      navigate("/", { replace: true });
    }
  };

  const isHomeLike = ["/", "/home"].includes(pathname);

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: 64,
        padding: "0 20px",
        borderBottom: "1px solid #e5e7eb",
        background: "#fff",
        boxSizing: "border-box",
      }}
    >
      <div
        onClick={() => navigate("/home")}
        style={{ fontWeight: 800, fontSize: 20, cursor: "pointer" }}
      >
        AI Care
      </div>

      <div style={{ display: "flex", gap: 10 }}>
        <button
          onClick={handleLogout}
          style={{
            padding: "8px 12px",
            borderRadius: 10,
            border: "1px solid #e5e7eb",
            background: "#fff",
            cursor: "pointer",
          }}
        >
          로그아웃
        </button>
        <button
          onClick={handleUnlink}
          style={{
            padding: "8px 12px",
            borderRadius: 10,
            border: "1px solid #ef4444",
            background: "#fff",
            color: "#ef4444",
            cursor: "pointer",
          }}
        >
          연결해제
        </button>
      </div>
    </header>
  );
}
