import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime

# ✅ backend/database/carebot.db 절대경로 고정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "carebot.db")

class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        print("✅ 현재 사용하는 DB 경로:", self.db_path)
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 사용자-환자 연결 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_patient_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                patient_id TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                relationship TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_email, patient_id)
            )
        ''')
        
        # 환자 정보 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                birth_date TEXT,
                room_number TEXT,
                admission_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 피드백 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                rating INTEGER NOT NULL,
                comment TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # 초기 데이터 삽입 (테스트용)
        self.insert_initial_data()
    
    def insert_initial_data(self):
        """초기 테스트 데이터 삽입"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 환자 정보 삽입
        cursor.execute('''
            INSERT OR IGNORE INTO patients (patient_id, name, birth_date, room_number, admission_date)
            VALUES (?, ?, ?, ?, ?)
        ''', ("25-0000032", "김x애", "1935-03-15", "301", "2024-01-15"))
        
        # 사용자-환자 연결 삽입
        cursor.execute('''
            INSERT OR IGNORE INTO user_patient_relations (user_email, patient_id, patient_name, relationship)
            VALUES (?, ?, ?, ?)
        ''', ("sample@sample.com", "25-0000032", "김x애", "딸"))
        
        conn.commit()
        conn.close()
    
    def get_user_patients(self, user_email: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT upr.patient_id, upr.patient_name, upr.relationship, 
                   p.birth_date, p.room_number, p.admission_date
            FROM user_patient_relations upr
            LEFT JOIN patients p ON upr.patient_id = p.patient_id
            WHERE upr.user_email = ?
            ORDER BY upr.created_at DESC
        ''', (user_email,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "patient_id": row[0],
                "patient_name": row[1],
                "relationship": row[2],
                "birth_date": row[3],
                "room_number": row[4],
                "admission_date": row[5]
            }
            for row in rows
        ]
    
    def add_user_patient(self, user_email: str, patient_id: str, patient_name: str, relationship: str = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                '''
                INSERT INTO user_patient_relations (user_email, patient_id, patient_name, relationship)
                VALUES (?, ?, ?, ?)
                ''',
                (user_email, patient_id, patient_name, relationship)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def save_feedback(self, user_email: str, rating: int, comment: str, timestamp: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO feedback (user_email, rating, comment, timestamp)
            VALUES (?, ?, ?, ?)
            ''',
            (user_email, rating, comment, timestamp)
        )
        
        conn.commit()
        feedback_id = cursor.lastrowid
        conn.close()
        return feedback_id
    
    def get_feedback(self, user_email: str = None) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_email:
            cursor.execute(
                '''
                SELECT id, user_email, rating, comment, timestamp, created_at
                FROM feedback
                WHERE user_email = ?
                ORDER BY created_at DESC
                ''',
                (user_email,)
            )
        else:
            cursor.execute(
                '''
                SELECT id, user_email, rating, comment, timestamp, created_at
                FROM feedback
                ORDER BY created_at DESC
                '''
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "user_email": row[1],
                "rating": row[2],
                "comment": row[3],
                "timestamp": row[4],
                "created_at": row[5]
            }
            for row in rows
        ]

# ✅ 전역 인스턴스
db_manager = DatabaseManager()
