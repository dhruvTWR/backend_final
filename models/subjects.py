from database.db import Database

class Subject:
    def __init__(self):
        self.db = Database()
    
    def add_subject(self, subject_code, subject_name):
        """Add new subject (Admin only)"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO subjects (subject_code, subject_name)
                VALUES (%s, %s)
            """
            cursor.execute(query, (subject_code.upper(), subject_name))
            
            subject_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Subject added: {subject_name} ({subject_code})")
            return subject_id
            
        except Exception as e:
            print(f"❌ Error adding subject: {e}")
            raise
    
 
    
    def get_subject_by_code(self, subject_code):
        """Get subject by code"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM subjects WHERE subject_code = %s"
            cursor.execute(query, (subject_code.upper(),))
            subject = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return subject
            
        except Exception as e:
            print(f"❌ Error getting subject by code: {e}")
            raise
    
    def get_all_subjects(self):
        """Get all subjects"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM subjects ORDER BY subject_code"
            cursor.execute(query)
            subjects = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return subjects
            
        except Exception as e:
            print(f"❌ Error getting all subjects: {e}")
            raise
    
    def search_subjects(self, search_term):
        """Search subjects by code or name"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT * FROM subjects 
                WHERE subject_code LIKE %s OR subject_name LIKE %s
                ORDER BY subject_code
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern))
            subjects = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return subjects
            
        except Exception as e:
            print(f"❌ Error searching subjects: {e}")
            raise
    

    
    def delete_subject(self, subject_id):
        """Delete subject (Admin only) - WARNING: Cascades to class_subjects and attendance!"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get subject name before deleting
            cursor.execute("SELECT subject_name FROM subjects WHERE id = %s", (subject_id,))
            result = cursor.fetchone()
            
            if not result:
                print("❌ Subject not found")
                return
            
            subject_name = result[0]
            
            query = "DELETE FROM subjects WHERE id = %s"
            cursor.execute(query, (subject_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Subject deleted: {subject_name}")
            
        except Exception as e:
            print(f"❌ Error deleting subject: {e}")
            raise
    
   
    
    
    
   