import React, { useState } from 'react';
import Header from '../components/Header';

const FeedbackPage = () => {
  const [selectedRating, setSelectedRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState("");

  const getStarWidth = (index) => {
    const rating = hoverRating || selectedRating;
    const value = index + 1;
    if (rating >= value) return "100%";
    return "0%";
  };

  return (
    <>
      <Header />
      <div style={styles.container}>
        <h2 style={styles.title}>만족도 평가</h2>
        <p style={styles.subtitle}>서비스는 만족스러우셨나요?</p>

        <div style={styles.stars}>
          {[0, 1, 2, 3, 4].map((i) => (
            <div
              key={i}
              style={styles.starWrapper}
              onMouseMove={() => setHoverRating(i + 1)}
              onMouseLeave={() => setHoverRating(0)}
              onClick={() => setSelectedRating(i + 1)}
            >
              <span style={styles.starBg}>★</span>
              <span style={{ ...styles.starFg, width: getStarWidth(i) }}>★</span>
            </div>
          ))}
        </div>

        <div style={styles.ratingText}>
          {selectedRating ? `현재 평점: ${selectedRating}점` : "별점을 선택해주세요"}
        </div>

        <textarea
          style={styles.commentBox}
          placeholder="서비스에 대한 의견을 자유롭게 작성해주세요."
          value={comment}
          onChange={(e) => setComment(e.target.value)}
        />

        <button
          style={styles.submitBtn}
          onClick={() => alert(`평점: ${selectedRating}, 코멘트: ${comment}`)}
        >
          제출하기
        </button>
      </div>

      <style>{`
        button:hover {
          transform: scale(1.6);
          box-shadow: 0 4px 12px rgba(0,0,0,0.2);
          transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
      `}</style>
    </>
  );
};

const styles = {
  container: {
    width: "450px",
    background: "#ffffff",
    padding: "40px",
    borderRadius: "24px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.1)",
    margin: "100px auto",
    fontFamily: "'Pretendard', sans-serif",
    boxSizing: "border-box", // ✅
  },
  title: {
    fontSize: "26px",
    fontWeight: "700",
    color: "#222",
    textAlign: "center",
    marginBottom: "10px",
  },
  subtitle: {
    fontSize: "16px",
    color: "#777",
    textAlign: "center",
    marginBottom: "25px",
  },
  stars: {
    display: "flex",
    justifyContent: "center",
    gap: "10px",
    marginBottom: "20px",
  },
  starWrapper: {
    position: "relative",
    width: "40px",
    height: "40px",
    cursor: "pointer",
    transition: "transform 0.2s ease",
  },
  starBg: {
    fontSize: "40px",
    color: "#e2e2e2",
    position: "absolute",
    top: 0,
    left: 0,
  },
  starFg: {
    fontSize: "40px",
    color: "#ffc107",
    position: "absolute",
    top: 0,
    left: 0,
    overflow: "hidden",
    whiteSpace: "nowrap",
    transition: "width 0.2s ease",
  },
  ratingText: {
    textAlign: "center",
    fontSize: "15px",
    color: "#666",
    marginBottom: "20px",
  },
  commentBox: {
    width: "100%",
    height: "100px",
    padding: "14px",
    border: "1px solid #ddd",
    borderRadius: "12px",
    resize: "none",
    fontSize: "15px",
    lineHeight: "1.5",
    margin: "0 auto 24px",  // ✅ 가운데 정렬
    fontFamily: "inherit",
    display: "block",
    boxSizing: "border-box",
  },
  submitBtn: {
    width: "100%",
    display: "block",     // ✅ 수평 가운데 정렬 가능
    margin: "0 auto",     // ✅ 중앙 정렬
    padding: "16px",
    background: "#3772a6ff",
    color: "#fff",
    border: "none",
    borderRadius: "12px",
    fontSize: "16px",
    fontWeight: "600",
    cursor: "pointer",
    transition: "all 0.3s ease",
    transform: "scale(1)",
  },
};

export default FeedbackPage;