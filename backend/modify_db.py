# backend/modify_db.py
import sqlite3
import os

class DatabaseModifier:
    def __init__(self, db_path: str = "database/carebot.db"):
        self.db_path = db_path
        if not os.path.exists(db_path):
            print("❌ 데이터베이스 파일이 존재하지 않습니다.")
            return
    
    def add_patient(self, user_email: str, patient_id: str, patient_name: str, relationship: str = None):
        """새로운 환자 연결 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 환자 정보 테이블에 추가
            cursor.execute('''
                INSERT OR REPLACE INTO patients (patient_id, name, birth_date, room_number, admission_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (patient_id, patient_name, None, None, None))
            
            # 사용자-환자 연결 추가
            cursor.execute('''
                INSERT OR REPLACE INTO user_patient_relations (user_email, patient_id, patient_name, relationship)
                VALUES (?, ?, ?, ?)
            ''', (user_email, patient_id, patient_name, relationship))
            
            conn.commit()
            print(f"✅ 환자 {patient_name}({patient_id})가 {user_email}에게 추가되었습니다.")
            return True
            
        except Exception as e:
            print(f"❌ 환자 추가 실패: {e}")
            return False
        finally:
            conn.close()
    
    def update_patient_info(self, patient_id: str, **kwargs):
        """환자 정보 수정"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 수정할 컬럼들
            update_fields = []
            values = []
            
            if 'name' in kwargs:
                update_fields.append("name = ?")
                values.append(kwargs['name'])
            
            if 'birth_date' in kwargs:
                update_fields.append("birth_date = ?")
                values.append(kwargs['birth_date'])
            
            if 'room_number' in kwargs:
                update_fields.append("room_number = ?")
                values.append(kwargs['room_number'])
            
            if 'admission_date' in kwargs:
                update_fields.append("admission_date = ?")
                values.append(kwargs['admission_date'])
            
            if not update_fields:
                print("❌ 수정할 내용이 없습니다.")
                return False
            
            # SQL 쿼리 생성
            query = f"UPDATE patients SET {', '.join(update_fields)} WHERE patient_id = ?"
            values.append(patient_id)
            
            cursor.execute(query, values)
            conn.commit()
            
            print(f"✅ 환자 {patient_id} 정보가 수정되었습니다.")
            return True
            
        except Exception as e:
            print(f"❌ 환자 정보 수정 실패: {e}")
            return False
        finally:
            conn.close()
    
    def delete_patient_relation(self, user_email: str, patient_id: str):
        """사용자-환자 연결 삭제"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                DELETE FROM user_patient_relations 
                WHERE user_email = ? AND patient_id = ?
            ''', (user_email, patient_id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"✅ {user_email}의 환자 {patient_id} 연결이 삭제되었습니다.")
                return True
            else:
                print(f"❌ {user_email}의 환자 {patient_id} 연결을 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            print(f"❌ 환자 연결 삭제 실패: {e}")
            return False
        finally:
            conn.close()
    
    def add_feedback(self, user_email: str, rating: int, comment: str):
        """피드백 추가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO feedback (user_email, rating, comment, timestamp)
                VALUES (?, ?, ?, datetime('now'))
            ''', (user_email, rating, comment))
            
            conn.commit()
            print(f"✅ {user_email}의 피드백이 추가되었습니다.")
            return True
            
        except Exception as e:
            print(f"❌ 피드백 추가 실패: {e}")
            return False
        finally:
            conn.close()

def main():
    modifier = DatabaseModifier()
    
    print("🔧 데이터베이스 수정 도구")
    print("=" * 40)
    
    while True:
        print("\n📋 메뉴:")
        print("1. 새로운 환자 추가")
        print("2. 환자 정보 수정")
        print("3. 환자 연결 삭제")
        print("4. 피드백 추가")
        print("5. 종료")
        
        choice = input("\n선택하세요 (1-5): ").strip()
        
        if choice == "1":
            user_email = input("사용자 이메일: ").strip()
            patient_id = input("환자 ID: ").strip()
            patient_name = input("환자 이름: ").strip()
            relationship = input("관계 (선택사항): ").strip() or None
            
            modifier.add_patient(user_email, patient_id, patient_name, relationship)
            
        elif choice == "2":
            patient_id = input("수정할 환자 ID: ").strip()
            print("수정할 정보를 입력하세요 (수정하지 않을 항목은 엔터):")
            
            name = input("환자 이름: ").strip() or None
            birth_date = input("생년월일 (YYYY-MM-DD): ").strip() or None
            room_number = input("병실 번호: ").strip() or None
            admission_date = input("입원일 (YYYY-MM-DD): ").strip() or None
            
            kwargs = {}
            if name: kwargs['name'] = name
            if birth_date: kwargs['birth_date'] = birth_date
            if room_number: kwargs['room_number'] = room_number
            if admission_date: kwargs['admission_date'] = admission_date
            
            modifier.update_patient_info(patient_id, **kwargs)
            
        elif choice == "3":
            user_email = input("사용자 이메일: ").strip()
            patient_id = input("삭제할 환자 ID: ").strip()
            modifier.delete_patient_relation(user_email, patient_id)
            
        elif choice == "4":
            user_email = input("사용자 이메일: ").strip()
            rating = int(input("별점 (1-5): ").strip())
            comment = input("의견: ").strip()
            modifier.add_feedback(user_email, rating, comment)
            
        elif choice == "5":
            print("👋 프로그램을 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다. 1-5 중에서 선택하세요.")

if __name__ == "__main__":
    main()