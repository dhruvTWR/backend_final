import bcrypt
from datetime import datetime
from database.db import Database

# ============================================
# FILE: models/admin.py
# ============================================

class Admin:
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
    
    def add_admin(self, username, password):
        """Add new admin"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            query = "INSERT INTO admins (username, password_hash) VALUES (%s, %s)"
            cursor.execute(query, (username, password_hash))
            
            admin_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Admin added: {username}")
            return admin_id
            
        except Exception as e:
            print(f"Error adding admin: {e}")
            raise
    
    def authenticate(self, username, password):
        """Authenticate admin"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM admins WHERE username = %s AND is_active = TRUE"
            cursor.execute(query, (username,))
            admin = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if admin and self.verify_password(password, admin['password_hash']):
                return {
                    'id': admin['id'],
                    'username': admin['username'],
                    'role': 'admin'
                }
            
            return None
            
        except Exception as e:
            print(f"Error authenticating admin: {e}")
            raise
    
    def get_admin_by_id(self, admin_id):
        """Get admin by ID"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT id, username, is_active, created_at FROM admins WHERE id = %s"
            cursor.execute(query, (admin_id,))
            admin = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return admin
            
        except Exception as e:
            print(f"Error getting admin: {e}")
            raise
    
    def get_all_admins(self):
        """Get all admins"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT id, username, is_active, created_at FROM admins ORDER BY username"
            cursor.execute(query)
            admins = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return admins
            
        except Exception as e:
            print(f"Error getting admins: {e}")
            raise
    
    def update_password(self, admin_id, new_password):
        """Update admin password"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(new_password)
            query = "UPDATE admins SET password_hash = %s WHERE id = %s"
            cursor.execute(query, (password_hash, admin_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Admin password updated: ID {admin_id}")
            
        except Exception as e:
            print(f"Error updating password: {e}")
            raise
    
    def deactivate_admin(self, admin_id):
        """Deactivate admin"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = "UPDATE admins SET is_active = FALSE WHERE id = %s"
            cursor.execute(query, (admin_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Admin deactivated: ID {admin_id}")
            
        except Exception as e:
            print(f"Error deactivating admin: {e}")
            raise