import bcrypt
from datetime import datetime
from database.db import Database

class Teacher:
    def __init__(self):
        self.db = Database()
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8') if isinstance(hashed, str) else hashed)
    
    def add_teacher(self, username, password):
        """Add new teacher"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            query = "INSERT INTO teachers (username, password_hash) VALUES (%s, %s)"
            cursor.execute(query, (username, password_hash))
            
            teacher_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Teacher added: {username}")
            return teacher_id
            
        except Exception as e:
            print(f"Error adding teacher: {e}")
            raise
    
    def authenticate(self, username, password):
        """Authenticate teacher"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM teachers WHERE username = %s AND is_active = TRUE"
            cursor.execute(query, (username,))
            teacher = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if teacher and self.verify_password(password, teacher['password_hash']):
                return {
                    'id': teacher['id'],
                    'username': teacher['username'],
                    'role': 'teacher'
                }
            
            return None
            
        except Exception as e:
            print(f"Error authenticating teacher: {e}")
            raise
    
    def get_teacher_by_id(self, teacher_id):
        """Get teacher by ID"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT id, username, is_active, created_at FROM teachers WHERE id = %s"
            cursor.execute(query, (teacher_id,))
            teacher = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return teacher
            
        except Exception as e:
            print(f"Error getting teacher: {e}")
            raise
    
    def update_teacher(self, teacher_id, **kwargs):
        """Update teacher information"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            set_clauses = []
            values = []
            
            if 'username' in kwargs:
                set_clauses.append("username = %s")
                values.append(kwargs['username'])
            
            if 'password' in kwargs:
                set_clauses.append("password_hash = %s")
                values.append(self.hash_password(kwargs['password']))
            
            if not set_clauses:
                return
            
            values.append(teacher_id)
            query = f"UPDATE teachers SET {', '.join(set_clauses)} WHERE id = %s"
            
            cursor.execute(query, tuple(values))
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Teacher updated: ID {teacher_id}")
            
        except Exception as e:
            print(f"Error updating teacher: {e}")
            raise
    
    def delete_teacher(self, teacher_id):
        """Delete teacher"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM teachers WHERE id = %s"
            cursor.execute(query, (teacher_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Teacher deleted: ID {teacher_id}")
            
        except Exception as e:
            print(f"Error deleting teacher: {e}")
            raise
        

    def get_all_teachers(self):
        """Get all teachers"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT id, username, is_active, created_at, updated_at
                FROM teachers
                WHERE is_active = TRUE
                ORDER BY username
            """
            cursor.execute(query)
            teachers = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return teachers
            
        except Exception as e:
            print(f"Error getting all teachers: {e}")
            raise