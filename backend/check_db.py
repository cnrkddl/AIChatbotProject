import os
import psycopg2
import psycopg2.extras
from typing import List, Dict, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise RuntimeError("❌ DATABASE_URL 이 .env에 설정되지 않았습니다.")

    def _get_conn(self):
        return psycopg2.connect(self.db_url, sslmode="require")

    def init_database(self):
        """Postgres 테이블 생성"""
        conn = self._get_conn()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_patient_relations (
            id SERIAL PRIMARY KEY,
            user_email TEXT NOT NULL,
            patient_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            relationship TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_email, patient_id)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            birth_date TEXT,
            room_number TEXT,
            admission_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            user_email TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        cur.close()
        conn.close()

    # ----------------------------
    # 환자 관련
    # ----------------------------
    def get_user_patients(self, user_email: str) -> List[Dict]:
        conn = self._get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("""
        SELECT upr.patient_id, upr.patient_name, upr.relationship,
               p.birth_date, p.room_number, p.admission_date
        FROM user_patient_relations upr
        LEFT JOIN patients p ON upr.patient_id = p.patient_id
        WHERE upr.user_email = %s
        ORDER BY upr.created_at DESC
        """, (user_email,))

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [dict(row) for row in rows]

    def add_user_patient(self, user_email: str, patient_id: str, patient_name: str, relationship: str = None):
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
            INSERT INTO user_patient_relations (user_email, patient_id, patient_name, relationship)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_email, patient_id) DO NOTHING
            """, (user_email, patient_id, patient_name, relationship))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    # ----------------------------
    # 피드백 관련
    # ----------------------------
    def save_feedback(self, user_email: str, rating: int, comment: str, timestamp: str):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO feedback (user_email, rating, comment, timestamp)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """, (user_email, rating, comment, timestamp))
        feedback_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return feedback_id

    def get_feedback(self, user_email: Optional[str] = None) -> List[Dict]:
        conn = self._get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if user_email:
            cur.execute("""
            SELECT * FROM feedback WHERE user_email = %s ORDER BY created_at DESC
            """, (user_email,))
        else:
            cur.execute("""
            SELECT * FROM feedback ORDER BY created_at DESC
            """)

        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [dict(row) for row in rows]


# 전역 인스턴스
db_manager = DatabaseManager()
db_manager.init_database()
