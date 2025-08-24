// src/components/Header.jsx
import React, { useState, useEffect, useCallback } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import AuthActions from "./AuthActions";

export default function Header({ onFAQClick }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [userInfo, setUserInfo] = useState(null);

  const pathname = location?.pathname || "/";
  const isChatPage = pathname === "/chat";

  // ✅ API base url (배포 기본값 → 로컬 fallback)
  const API_BASE =
    (process.env.REACT_APP_API_BASE &&
      process.env.REACT_APP_API_BASE.replace(/\/+$/, "")) ||
    "https://aichatbotproject.onrender.com";

  const whoamiUrl = `${API_BASE}/auth/kakao/whoami`;

  // 🔹 사용자 정보 조회
  const fetchUserInfo = useCallback(async () => {
    try {
      const res = await fetch(whoamiUrl, { credentials: "include" });
      if (!res.ok) {
        setUserInfo(null);
        return;
      }
      const data = await res.json();
      if (data?.logged_in) {
        setUserInfo({
          email: data.email || "",
          nickname: data.nickname || "",
          profile_image: data.profile_image || "",
          id: data.id,
        });
      } else {
        setUserInfo(null);
      }
    } catch (err) {
      console.error("사용자 정보 가져오기 실패:", err);
      setUserInfo(null);
    }
  }, [whoamiUrl]);

  // 최초 + 라우트 변경 시
  useEffect(() => {
    fetchUserInfo();
  }, [fetchUserInfo, pathname]);

  // 창 포커스 돌아올 때 재조회
  useEffect(() => {
    const onFocus = () => fetchUserInfo();
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, [fetchUserInfo]);

  const handleLogoClick = () => navigate("/home");

  const initialChar =
    (userInfo?.nickname && userInfo.nickname.trim().charAt(0)) || "U";

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: "64px",
        padding: "0 1rem",
        borderBottom: "1px solid #ddd",
        background: "#fff",
        boxSizing: "border-box",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        position: "relative",
      }}
    >
      {/* 🔹 로고 */}
      <img
        src="https://search.pstatic.net/sunny/?src=https%3A%2F%2Flh3.googleusercontent.com%2FvIEP7BRkOXpvJCTKH6c_zs78w2CfZer0fSrkkBN_zhYr4WF9o9H5ffJ23IGisjW45w%3Dh500&type=sc960_832"
        alt="효림의료재단 로고"
        style={{
          height: 40,
          objectFit: "contain",
          cursor: "pointer",
          display: "block",
        }}
        onClick={handleLogoClick}
      />

      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
        {isChatPage && (
          <button style={buttonStyle} onClick={onFAQClick} aria-label="FAQ">
            ?
          </button>
        )}

        {/* 로그인 한 경우만 표시 */}
        {userInfo && (
          <>
            {/* 사용자 프로필 */}
            <div
              style={styles.userProfile}
              title={userInfo.nickname || userInfo.email}
            >
              <div style={styles.profileImage}>
                {userInfo.profile_image ? (
                  <img
                    src={userInfo.profile_image}
                    alt="프로필"
                    style={styles.profileImg}
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <div style={styles.profileInitial}>{initialChar}</div>
                )}
              </div>
              <span style={styles.userEmail} title={userInfo.email || ""}>
                {userInfo.email || "이메일 없음"}
              </span>
            </div>

            {/* 로그아웃 / 연결해제 버튼 */}
            <AuthActions
              loggedIn={!!userInfo}
              onLogout={fetchUserInfo}
              onUnlink={fetchUserInfo}
              onDone={fetchUserInfo}
            />
          </>
        )}
      </div>
    </header>
  );
}

const buttonStyle = {
  width: 40,
  height: 40,
  fontSize: "1.25rem",
  borderRadius: "50%",
  border: "none",
  background: "#f5f5f5",
  fontWeight: "bold",
  cursor: "pointer",
  color: "#333",
};

const styles = {
  userProfile: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "4px 8px",
    borderRadius: "20px",
    background: "#f8f9fa",
    border: "1px solid #e9ecef",
  },
  profileImage: {
    width: "32px",
    height: "32px",
    borderRadius: "50%",
    overflow: "hidden",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#007bff",
  },
  profileImg: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    display: "block",
  },
  profileInitial: {
    color: "white",
    fontSize: "14px",
    fontWeight: "bold",
    lineHeight: 1,
  },
  userEmail: {
    fontSize: "12px",
    color: "#495057",
    fontWeight: 500,
    maxWidth: "150px",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
};
