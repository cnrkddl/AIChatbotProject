// src/pages/ChatBotPage.jsx
import React, { useState, useRef, useEffect } from 'react';
import Header from '../components/Header';
import FAQModal from '../components/FAQModal';

const API_BASE =
  process.env.REACT_APP_API_BASE || 'https://aichatbotproject.onrender.com';

export default function ChatBotPage() {
  const [isFAQOpen, setIsFAQOpen] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'bot', text: '안녕하세요! 무엇을 도와드릴까요?' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const toggleFAQ = () => setIsFAQOpen(prev => !prev);

  const handleSend = async () => {
    if (loading) return;
    const trimmed = input.trim();
    if (!trimmed) return;

    const newUserMsg = { sender: 'user', text: trimmed };
    setMessages(prev => [...prev, newUserMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: trimmed,        // ✅ 백엔드 스키마
          session_id: 'demo-web',  // ⬅️ 선택(없으면 서버가 "web" 사용)
        }),
      });

      if (!res.ok) {
        const errText = await res.text().catch(() => '');
        throw new Error(`HTTP ${res.status} ${res.statusText} ${errText || ''}`);
      }

      const data = await res.json();
      const botText =
        data && typeof data.reply === 'string'
          ? data.reply
          : '⚠️ 알 수 없는 응답 형식입니다.';

      setMessages(prev => [...prev, { sender: 'bot', text: botText }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        { sender: 'bot', text: '⚠️ 서버 연결/처리 중 오류가 발생했습니다.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div style={styles.page}>
      <style>{`
        @keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }
        button:disabled { opacity: 0.7; cursor: not-allowed; }
      `}</style>

      <Header onFAQClick={toggleFAQ} />

      <div style={styles.chatArea}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              ...styles.message,
              ...(msg.sender === 'user' ? styles.userMessage : styles.botMessage),
            }}
          >
            {msg.text}
          </div>
        ))}

        {loading && (
          <div style={styles.botMessage}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={styles.spinner} />
              <em style={{ color: '#555' }}>응답 생성 중...</em>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      <div style={styles.inputArea}>
        <input
          style={styles.input}
          placeholder="메시지를 입력하세요..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !loading && handleSend()}
        />
        <button
          style={styles.sendBtn}
          onClick={handleSend}
          disabled={!input.trim() || loading}
          aria-busy={loading}
        >
          전송
        </button>
      </div>

      {isFAQOpen && <FAQModal onClose={toggleFAQ} />}
    </div>
  );
}

const styles = {
  page: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    background: '#f7f9fc',
    fontFamily: "'Pretendard', sans-serif",
    color: '#2C2C2C',
  },
  chatArea: {
    flex: 1,
    padding: 24,
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: 14,
  },
  message: {
    maxWidth: '75%',
    padding: '14px 18px',
    borderRadius: 18,
    fontSize: 15,
    lineHeight: 1.6,
    wordBreak: 'break-word',
    whiteSpace: 'pre-wrap',
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
  },
  userMessage: {
    alignSelf: 'flex-end',
    background: 'linear-gradient(135deg, #4B6EF5, #6A89F7)',
    color: '#fff',
    borderTopRightRadius: 4,
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  },
  botMessage: {
    alignSelf: 'flex-start',
    background: '#F0F2F5',
    color: '#333',
    borderTopLeftRadius: 4,
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
  },
  inputArea: {
    display: 'flex',
    padding: 16,
    borderTop: '1px solid #ddd',
    background: '#ffffff',
  },
  input: {
    flex: 1,
    padding: 14,
    borderRadius: 20,
    border: '1px solid #ccc',
    outline: 'none',
    fontSize: 15,
    background: '#fff',
    color: '#333',
    fontFamily: 'inherit',
    boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.05)',
  },
  sendBtn: {
    marginLeft: 12,
    padding: '14px 20px',
    border: 'none',
    borderRadius: 20,
    background: '#4B6EF5',
    color: '#fff',
    fontWeight: 600,
    fontSize: 15,
    cursor: 'pointer',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    transition: 'background 0.3s ease',
  },
  spinner: {
    width: 16,
    height: 16,
    border: '2px solid #ccc',
    borderTop: '2px solid #4B6EF5',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
};
