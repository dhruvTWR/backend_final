import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import mysql.connector
from mysql.connector import Error
import pickle
import json
from datetime import datetime, date
import subprocess
from config import Config

class Database:
    def __init__(self):
        self.config = {
            'host': Config.DB_HOST,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME
        }
        self.init_database()
    
    def get_connection(self):
        """Create database connection"""
        try:
            conn = mysql.connector.connect(**self.config)
            return conn
        except Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def init_database(self):
        """Initialize database and create tables if not exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # =============================================
            # 1. BRANCHES TABLE
            # =============================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS branches (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    branch_code VARCHAR(10) UNIQUE NOT NULL,
                    branch_name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            # =============================================
            # 2. ADMINS TABLE
            # =============================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(100) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            # =============================================
            # 3. TEACHERS TABLE
            # =============================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(100) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            # =============================================
            # 4. STUDENTS TABLE
            # =============================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    roll_number VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    branch_id INT NOT NULL,
                    year INT NOT NULL CHECK (year BETWEEN 1 AND 4),
                    section VARCHAR(10) NOT NULL,
                    face_encoding BLOB,
                    photo_path VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE RESTRICT,
                    INDEX idx_branch_year_section (branch_id, year, section),
                    INDEX idx_roll_number (roll_number)
                ) ENGINE=InnoDB
            """)
            
            # =============================================
            # 5. SUBJECTS TABLE
            # =============================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subjects (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    subject_code VARCHAR(20) UNIQUE NOT NULL,
                    subject_name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB
            """)
            
            # =============================================
            # 6. CLASS_SUBJECTS TABLE (Mapping)
            # =============================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS class_subjects (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    subject_id INT NOT NULL,
                    branch_id INT NOT NULL,
                    year INT NOT NULL CHECK (year BETWEEN 1 AND 4),
                    section VARCHAR(10) NOT NULL,
                    semester INT NOT NULL CHECK (semester BETWEEN 1 AND 8),
                    academic_year VARCHAR(10) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                    FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE RESTRICT,
                    UNIQUE KEY unique_class_subject (subject_id, branch_id, year, section, semester, academic_year),
                    INDEX idx_class (branch_id, year, section)
                ) ENGINE=InnoDB
            """)
            
            # =============================================
            # 7. ATTENDANCE TABLE
            # =============================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    student_id INT NOT NULL,
                    class_subject_id INT NOT NULL,
                    attendance_date DATE NOT NULL,
                    attendance_time TIME NOT NULL,
                    status ENUM('present', 'absent') DEFAULT 'absent',
                    confidence FLOAT DEFAULT 0.0,
                    image_path VARCHAR(255),
                    marked_by INT,
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (class_subject_id) REFERENCES class_subjects(id) ON DELETE CASCADE,
                    FOREIGN KEY (marked_by) REFERENCES teachers(id) ON DELETE SET NULL,
                    UNIQUE KEY unique_attendance (student_id, class_subject_id, attendance_date),
                    INDEX idx_date (attendance_date),
                    INDEX idx_student_date (student_id, attendance_date),
                    INDEX idx_class_subject_date (class_subject_id, attendance_date)
                ) ENGINE=InnoDB
            """)
            
            # =============================================
            # 8. UNRECOGNIZED_FACES TABLE
            # =============================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS unrecognized_faces (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    class_subject_id INT NOT NULL,
                    image_path VARCHAR(255) NOT NULL,
                    original_upload VARCHAR(255),
                    attendance_date DATE NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_student_id INT,
                    resolved_by INT,
                    resolved_at TIMESTAMP NULL,
                    FOREIGN KEY (class_subject_id) REFERENCES class_subjects(id) ON DELETE CASCADE,
                    FOREIGN KEY (resolved_student_id) REFERENCES students(id) ON DELETE SET NULL,
                    INDEX idx_unresolved (resolved, attendance_date)
                ) ENGINE=InnoDB
            """)
            
            # =============================================
            # 9. LOGS TABLE
            # =============================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    log_type ENUM('info', 'warning', 'error', 'attendance', 'admin') NOT NULL,
                    user_type ENUM('admin', 'teacher', 'system') NOT NULL,
                    user_id INT,
                    action VARCHAR(100) NOT NULL,
                    message TEXT,
                    details JSON,
                    ip_address VARCHAR(45),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_log_type (log_type),
                    INDEX idx_created_at (created_at),
                    INDEX idx_user (user_type, user_id)
                ) ENGINE=InnoDB
            """)
            
            # =============================================
            # 10. ATTENDANCE_SUMMARY TABLE
            # =============================================
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance_summary (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    student_id INT NOT NULL,
                    class_subject_id INT NOT NULL,
                    total_classes INT DEFAULT 0,
                    classes_attended INT DEFAULT 0,
                    attendance_percentage FLOAT DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                    FOREIGN KEY (class_subject_id) REFERENCES class_subjects(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_summary (student_id, class_subject_id)
                ) ENGINE=InnoDB
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Database initialized successfully - All tables created")
            
        except Error as e:
            print(f"❌ Database initialization error: {e}")
            raise
    
    def insert_sample_data(self):
        """Insert sample data for testing"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Insert sample branches
            cursor.execute("""
                INSERT IGNORE INTO branches (branch_code, branch_name) VALUES
                ('CSE', 'Computer Science Engineering'),
                ('ECE', 'Electronics and Communication'),
                ('ME', 'Mechanical Engineering'),
                ('CE', 'Civil Engineering')
            """)
            
            # Insert sample admin
            cursor.execute("""
                INSERT IGNORE INTO admins (username, password_hash) VALUES
                ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYKtHql7eS6')
            """)
            
            # Insert sample teacher
            cursor.execute("""
                INSERT IGNORE INTO teachers (username, password_hash) VALUES
                ('teacher1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYKtHql7eS6')
            """)
            
            # Insert sample subjects
            cursor.execute("""
                INSERT IGNORE INTO subjects (subject_code, subject_name) VALUES
                ('CS101', 'Data Structures'),
                ('CS102', 'Database Management Systems'),
                ('CS103', 'Operating Systems'),
                ('MA101', 'Mathematics I')
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Sample data inserted successfully")
            
        except Error as e:
            print(f"❌ Error inserting sample data: {e}")
            raise
        
        

if __name__ == "__main__":
    print("Database module is running...")
    db = Database()
