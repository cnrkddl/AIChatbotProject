import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <div style={styles.page}>
      <Header />

      <main style={styles.main}>
        <h1 style={styles.mainTitle}>효림의료재단 챗봇입니다</h1>
        <p style={styles.description}>보호자님, 무엇을 도와드릴까요?</p>

        <div style={styles.cardContainer}>
          <div style={styles.card}>
  <div>
    <h3 style={{ ...styles.cardTitle, margin: '0 0 2px 0' }}>대표번호</h3>
    <p style={{ ...styles.cardText, margin: 0, marginBottom: '18px' }}>031-919-0041</p> {/* 여기 marginBottom 키포인트 */}
  </div>
  <div>
    <h3 style={{ ...styles.cardTitle, margin: '0 0 2px 0' }}>입원상담</h3>
    <p style={{ ...styles.cardText, margin: 0 }}>010-4130-0041</p>
  </div>
</div>


          <div style={styles.card}>
            <h3 style={styles.cardTitle}>외래 진료시간 안내</h3>
            <p style={styles.cardText}>
              평일 08:30 ~ 17:30<br />
              토요일 08:30 ~ 13:00
            </p>
          </div>
        </div>

        <div style={styles.menuCardContainer}>
          <div
            style={styles.menuCard}
            onClick={() => navigate('/chat')}
            className="menu-btn"
          >
            💬 챗봇 질문하기
          </div>
          <div
            style={styles.menuCard}
            onClick={() => navigate('/patient-info')}
            className="menu-btn"
          >
            🧑‍⚕️ 환자 정보 보기
          </div>
          <div
            style={styles.menuCard}
            onClick={() => navigate('/feedback')}
            className="menu-btn"
          >
            📝 고객 평가 남기기
          </div>
        </div>
      </main>

      <footer style={styles.footer}>
        경기도 고양시 일산서구 주화로 88 효림빌딩   /   {' '}
        <a
          href="http://hyorim-h.com"
          target="_blank"
          rel="noopener noreferrer"
          className="hospital-link"
        >
          효림요양병원 홈페이지
        </a>

        <style>
          {`
            .hospital-link {
              color: #f1f1f1;
              text-decoration: underline;
              transition: color 0.3s ease;
            }
            .hospital-link:hover {
              color: #005BAC;
            }
            .menu-btn {
              transition: transform 0.2s ease, background-color 0.2s ease;
            }
            .menu-btn:hover {
              transform: translateY(-3px);
              background-color: #f0f8ff;
            }
          `}
        </style>
      </footer>
    </div>
  );
};

const styles = {
  page: {
    backgroundImage: `url("http://hyorim-h.com/images/greetings-img-3.png")`,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: "'Noto Sans KR', sans-serif",
  },
  main: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '40px 20px',
    textAlign: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: '12px',
  },
  mainTitle: {
    fontSize: '32px',
    color: '#005BAC',
    fontWeight: 'bold',
    marginBottom: '10px',
    lineHeight: '1.4',
  },
  description: {
    fontSize: '16px',
    color: '#333',
    marginBottom: '40px',
  },
  cardContainer: {
    display: 'flex',
    gap: '20px',
    justifyContent: 'center',
    marginBottom: '40px',
    flexWrap: 'wrap',
  },
  card: {
    background: '#fff',
    borderRadius: '12px',
    padding: '20px',
    minWidth: '300px',
    flex: 1,
    minHeight: '180px',
    boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  cardTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#222',
    marginBottom: '4px',
  },
  cardText: {
    fontSize: '16px',
    fontWeight: '500',
    color: '#333',
    marginBottom: '6px',
  },
  cardSubText: {
    fontSize: '14px',
    color: '#555',
    marginTop: '4px',
  },
  menuCardContainer: {
    display: 'flex',
    justifyContent: 'center',
    flexWrap: 'wrap',
    gap: '16px',
    marginTop: '40px',
  },
  menuCard: {
    background: '#fff',
    border: '1px solid #ccc',
    borderRadius: '10px',
    padding: '16px 24px',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
  },
  // 📍 주소 푸터 (항상 아래에 위치)
  footer: {
    textAlign: 'center',
    padding: '16px 0',
    color: '#f1f1f1',
    fontSize: '14px',
    backgroundColor: 'rgba(0,0,0,0.3)',
    marginTop: 'auto',
  },
};

export default HomePage;