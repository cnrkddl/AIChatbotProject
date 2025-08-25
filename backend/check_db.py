# backend/check_db.py
import sqlite3
import os

def check_database():
    db_path = "database/carebot.db"
    
    if not os.path.exists(db_path):
        print("❌ 데이터베이스 파일이 존재하지 않습니다.")
        return
    
    print("✅ 데이터베이스 파일 발견:", db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블 목록 확인
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📋 생성된 테이블 ({len(tables)}개):")
    for table in tables:
        print(f"  - {table[0]}")
    
    # 각 테이블의 데이터 확인
    for table in tables:
        table_name = table[0]
        print(f"\n🔍 {table_name} 테이블:")
        
        # 테이블 구조 확인
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print("  컬럼:")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")
        
        # 데이터 개수 확인
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  데이터 개수: {count}개")
        
        # 실제 데이터 확인 (최대 5개)
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            print("  샘플 데이터:")
            for row in rows:
                print(f"    {row}")
    
    conn.close()

if __name__ == "__main__":
    check_database()