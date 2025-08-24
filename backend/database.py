# backend/database.py
import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "database/carebot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        # 데이터베이스 디렉토리 생성
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
        
        # 피드백 테이블 (기존 JSON 파일 대신)
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
        
        # ===== 여기서 샘플 데이터를 수정할 수 있습니다 =====
        
        # 환자 정보 삽입 (환자 ID, 이름, 생년월일, 병실, 입원일)
        cursor.execute('''
            INSERT OR IGNORE INTO patients (patient_id, name, birth_date, room_number, admission_date)
            VALUES (?, ?, ?, ?, ?)
        ''', ("25-0000032", "김x애", "1935-03-15", "301", "2024-01-15"))
        
        # 사용자-환자 연결 삽입 (사용자 이메일, 환자 ID, 환자 이름, 관계)
        cursor.execute('''
            INSERT OR IGNORE INTO user_patient_relations (user_email, patient_id, patient_name, relationship)
            VALUES (?, ?, ?, ?)
        ''', ("ㅇㅇㅇ@naver.com", "25-0000032", "김x애", "딸"))
        
        # # ===== 추가 환자 예시 (샘플 데이터) =====
        # # 환자 2: 박영희
        # cursor.execute('''
        #     INSERT OR IGNORE INTO patients (patient_id, name, birth_date, room_number, admission_date)
        #     VALUES (?, ?, ?, ?, ?)
        # ''', ("25-0000033", "박영희", "1940-07-20", "302", "2024-02-01"))
        
        # cursor.execute('''
        #     INSERT OR IGNORE INTO user_patient_relations (user_email, patient_id, patient_name, relationship)
        #     VALUES (?, ?, ?, ?)
        # ''', ("보호자 이메일", "25-0000033", "박영희", "어머니"))
        
        # # 환자 3: 이민수
        # cursor.execute('''
        #     INSERT OR IGNORE INTO patients (patient_id, name, birth_date, room_number, admission_date)
        #     VALUES (?, ?, ?, ?, ?)
        # ''', ("25-0000034", "이민수", "1938-11-10", "303", "2024-01-20"))
        
        # cursor.execute('''
        #     INSERT OR IGNORE INTO user_patient_relations (user_email, patient_id, patient_name, relationship)
        #     VALUES (?, ?, ?, ?)
        # ''', ("보호자 이메일", "25-0000034", "이민수", "아버지"))
        
        # # ===== 다른 사용자 예시 =====
        # # 다른 사용자: kim@example.com
        # cursor.execute('''
        #     INSERT OR IGNORE INTO user_patient_relations (user_email, patient_id, patient_name, relationship)
        #     VALUES (?, ?, ?, ?)
        # ''', ("kim@example.com", "25-0000035", "장영희", "딸"))
        
        # cursor.execute('''
        #     INSERT OR IGNORE INTO patients (patient_id, name, birth_date, room_number, admission_date)
        #     VALUES (?, ?, ?, ?, ?)
        # ''', ("25-0000035", "장영희", "1942-05-15", "304", "2024-02-15"))
        
        conn.commit()
        conn.close()
    
    def get_user_patients(self, user_email: str) -> List[Dict]:
        """사용자의 환자 목록 조회"""
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
        
        patients = []
        for row in rows:
            patients.append({
                "patient_id": row[0],
                "patient_name": row[1],
                "relationship": row[2],
                "birth_date": row[3],
                "room_number": row[4],
                "admission_date": row[5]
            })
        
        return patients
    
    def add_user_patient(self, user_email: str, patient_id: str, patient_name: str, relationship: str = None):
        """사용자-환자 연결 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_patient_relations (user_email, patient_id, patient_name, relationship)
                VALUES (?, ?, ?, ?)
            ''', (user_email, patient_id, patient_name, relationship))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 이미 존재하는 연결
            return False
        finally:
            conn.close()
    
    def save_feedback(self, user_email: str, rating: int, comment: str, timestamp: str):
        """피드백 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (user_email, rating, comment, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (user_email, rating, comment, timestamp))
        
        conn.commit()
        conn.close()
        
        return cursor.lastrowid
    
    def get_feedback(self, user_email: str = None) -> List[Dict]:
        """피드백 조회 (특정 사용자 또는 전체)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_email:
            cursor.execute('''
                SELECT id, user_email, rating, comment, timestamp, created_at
                FROM feedback
                WHERE user_email = ?
                ORDER BY created_at DESC
            ''', (user_email,))
        else:
            cursor.execute('''
                SELECT id, user_email, rating, comment, timestamp, created_at
                FROM feedback
                ORDER BY created_at DESC
            ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        feedback = []
        for row in rows:
            feedback.append({
                "id": row[0],
                "user_email": row[1],
                "rating": row[2],
                "comment": row[3],
                "timestamp": row[4],
                "created_at": row[5]
            })
        
        return feedback

# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()