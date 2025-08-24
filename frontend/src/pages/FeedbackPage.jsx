import React, { useState } from 'react';
import Header from '../components/Header';

const FeedbackPage = () => {
  const [selectedRating, setSelectedRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const API_BASE = process.env.REACT_APP_API_BASE || 'https://aichatbotproject.onrender.com';
  
  const getStarWidth = (index) => {
    const rating = hoverRating || selectedRating;
    const value = index + 1;
    if (rating >= value) return "100%";
    return "0%";
  };

  const handleSubmit = async () => {
    if (selectedRating === 0) {
      alert("별점을 선택해주세요!");
      return;
    }

    if (comment.trim() === "") {
      alert("의견을 입력해주세요!");
      return;
    }

    setIsSubmitting(true);
    setSubmitStatus(null);

    try {
      const response = await fetch(`${API_BASE}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          rating: selectedRating,
          comment: comment.trim(),
          timestamp: new Date().toISOString(),
        }),
      });

      if (response.ok) {
        setSubmitStatus('success');
        // 성공 후 폼 초기화
        setTimeout(() => {
          setSelectedRating(0);
          setComment("");
          setSubmitStatus(null);
        }, 2000);
      } else {
        throw new Error('피드백 저장에 실패했습니다.');
      }
    } catch (error) {
      console.error('Error:', error);
      setSubmitStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setSelectedRating(0);
    setComment("");
    setSubmitStatus(null);
  };

  return (
    <>
      <Header />
      <div style={styles.container}>
        <h2 style={styles.title}>만족도 평가</h2>
        <p style={styles.subtitle}>서비스는 만족스러우셨나요?</p>

        {/* 성공/실패 메시지 */}
        {submitStatus === 'success' && (
          <div style={styles.successMessage}>
            ✅ 답변 감사합니다!
          </div>
        )}
        
        {submitStatus === 'error' && (
          <div style={styles.errorMessage}>
            ❌ 답변 저장에 실패했습니다. 다시 시도해주세요.
          </div>
        )}

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
          maxLength={500}
        />
        
        <div style={styles.charCount}>
          {comment.length}/500자
        </div>

        <div style={styles.buttonContainer}>
          <button
            style={styles.resetBtn}
            onClick={resetForm}
            disabled={isSubmitting}
          >
            다시 작성
          </button>
          
          <button
            style={styles.submitBtn}
            onClick={handleSubmit}
            disabled={isSubmitting || selectedRating === 0 || comment.trim() === ""}
          >
            {isSubmitting ? "저장 중..." : "제출하기"}
          </button>
        </div>
      </div>

      <style>{`
        button:hover:not(:disabled) {
          transform: scale(1.05);
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
    flex: 1,
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
  resetBtn: {
    flex: 1,
    padding: "16px",
    background: "#f8f9fa",
    color: "#6c757d",
    border: "1px solid #dee2e6",
    borderRadius: "12px",
    fontSize: "16px",
    fontWeight: "600",
    cursor: "pointer",
    transition: "all 0.3s ease",
    transform: "scale(1)",
  },
  buttonContainer: {
    display: "flex",
    gap: "12px",
  },
  successMessage: {
    textAlign: "center",
    color: "#4CAF50",
    fontSize: "16px",
    marginBottom: "20px",
  },
  errorMessage: {
    textAlign: "center",
    color: "#F44336",
    fontSize: "16px",
    marginBottom: "20px",
  },
  charCount: {
    textAlign: "right",
    fontSize: "14px",
    color: "#999",
    marginTop: "-10px",
    marginBottom: "20px",
  },
};

export default FeedbackPage;