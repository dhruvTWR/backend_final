
    #!/usr/bin/env python3
"""
Database Setup Script
Creates the attendance_system database, tables, and seeds initial data.
"""

import mysql.connector
from mysql.connector import Error
from config import Config
import sys

def create_database_and_tables():
    """Create the database and all tables if they don't exist"""
    try:
        print("\n" + "="*60)
        print("🔧 SETTING UP DATABASE AND TABLES")
        print("="*60 + "\n")

        # Connect without specifying database to create it
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        cursor = connection.cursor()
        print(f"Creating database: {Config.DB_NAME}")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
        print(f"✅ Database '{Config.DB_NAME}' created successfully\n")
        cursor.close()
        connection.close()

        # Now connect to the new database to create tables
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = connection.cursor()

        print("Creating tables...")

        # List of all CREATE TABLE statements
        table_queries = [
            """
            CREATE TABLE IF NOT EXISTS branches (
                id INT PRIMARY KEY AUTO_INCREMENT, branch_code VARCHAR(10) UNIQUE NOT NULL,
                branch_name VARCHAR(100) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS admins (
                id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(100) NOT NULL,
                password_hash VARCHAR(255) NOT NULL, is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS teachers (
                id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(100) NOT NULL,
                password_hash VARCHAR(255) NOT NULL, is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS students (
                id INT PRIMARY KEY AUTO_INCREMENT, roll_number VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL, email VARCHAR(100), branch_id INT NOT NULL,
                year INT NOT NULL CHECK (year BETWEEN 1 AND 4), section VARCHAR(10) NOT NULL,
                face_encoding BLOB, photo_path VARCHAR(255), is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE RESTRICT,
                INDEX idx_branch_year_section (branch_id, year, section), INDEX idx_roll_number (roll_number)
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS subjects (
                id INT PRIMARY KEY AUTO_INCREMENT, subject_code VARCHAR(20) UNIQUE NOT NULL,
                subject_name VARCHAR(100) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS class_subjects (
                id INT PRIMARY KEY AUTO_INCREMENT, subject_id INT NOT NULL, teacher_id INT NOT NULL,
                branch_id INT NOT NULL, year INT NOT NULL CHECK (year BETWEEN 1 AND 4),
                section VARCHAR(10) NOT NULL, semester INT NOT NULL CHECK (semester BETWEEN 1 AND 8),
                academic_year VARCHAR(10) NOT NULL, is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE RESTRICT,
                FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE RESTRICT,
                UNIQUE KEY unique_class_subject (subject_id, branch_id, year, section, semester, academic_year)
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INT PRIMARY KEY AUTO_INCREMENT, student_id INT NOT NULL, class_subject_id INT NOT NULL,
                attendance_date DATE NOT NULL, attendance_time TIME NOT NULL,
                status ENUM('present', 'absent') DEFAULT 'absent', confidence FLOAT DEFAULT 0.0,
                image_path VARCHAR(255), marked_by INT, remarks TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (class_subject_id) REFERENCES class_subjects(id) ON DELETE CASCADE,
                FOREIGN KEY (marked_by) REFERENCES teachers(id) ON DELETE SET NULL,
                UNIQUE KEY unique_attendance (student_id, class_subject_id, attendance_date)
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS unrecognized_faces (
                id INT PRIMARY KEY AUTO_INCREMENT, class_subject_id INT NOT NULL,
                image_path VARCHAR(255) NOT NULL, original_upload VARCHAR(255),
                attendance_date DATE NOT NULL, detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE, resolved_student_id INT, resolved_by INT, resolved_at TIMESTAMP NULL,
                FOREIGN KEY (class_subject_id) REFERENCES class_subjects(id) ON DELETE CASCADE,
                FOREIGN KEY (resolved_student_id) REFERENCES students(id) ON DELETE SET NULL
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INT PRIMARY KEY AUTO_INCREMENT, log_type ENUM('info', 'warning', 'error', 'attendance', 'admin') NOT NULL,
                user_type ENUM('admin', 'teacher', 'system') NOT NULL, user_id INT,
                action VARCHAR(100) NOT NULL, message TEXT, details JSON, ip_address VARCHAR(45),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB
            """,
            """
            CREATE TABLE IF NOT EXISTS attendance_summary (
                id INT PRIMARY KEY AUTO_INCREMENT, student_id INT NOT NULL, class_subject_id INT NOT NULL,
                total_classes INT DEFAULT 0, classes_attended INT DEFAULT 0,
                attendance_percentage FLOAT DEFAULT 0.0, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (class_subject_id) REFERENCES class_subjects(id) ON DELETE CASCADE,
                UNIQUE KEY unique_summary (student_id, class_subject_id)
            ) ENGINE=InnoDB
            """
        ]

        for query in table_queries:
            cursor.execute(query)
        
        print("✅ All 10 tables created successfully.")
        
        connection.commit()
        cursor.close()
        connection.close()

        print("\n" + "="*60)
        print("✨ DATABASE SETUP COMPLETE!")
        print("="*60)
        return True

    except Error as e:
        print(f"\n❌ Error during setup: {e}")
        return False

def seed_database():
    """Insert sample data for testing"""
    try:
        print("\n" + "="*60)
        print("🌱 SEEDING DATABASE WITH SAMPLE DATA")
        print("="*60 + "\n")

        connection = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = connection.cursor()

        cursor.execute("""
            INSERT IGNORE INTO branches (branch_code, branch_name) VALUES
            ('CSE', 'Computer Science Engineering'), ('ECE', 'Electronics and Communication'),
            ('ME', 'Mechanical Engineering'), ('CE', 'Civil Engineering')
        """)
        print("✅ Sample branches inserted.")

        cursor.execute("""
            INSERT IGNORE INTO admins (username, password_hash) VALUES
            ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYKtHql7eS6')
        """)
        print("✅ Sample admin inserted.")
        
        cursor.execute("""
            INSERT IGNORE INTO teachers (username, password_hash) VALUES
            ('teacher1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYKtHql7eS6')
        """)
        print("✅ Sample teacher inserted.")

        cursor.execute("""
            INSERT IGNORE INTO subjects (subject_code, subject_name) VALUES
            ('CS101', 'Data Structures'), ('CS102', 'Database Management Systems'),
            ('CS103', 'Operating Systems'), ('MA101', 'Mathematics I')
        """)
        print("✅ Sample subjects inserted.")
        
        connection.commit()
        cursor.close()
        connection.close()

        print("\n" + "="*60)
        print("✨ DATABASE SEEDING COMPLETE!")
        print("="*60)
        return True
    
    except Error as e:
        print(f"❌ Error inserting sample data: {e}")
        return False

def verify_setup():
    """Verify database and tables exist"""
    try:
        print("\n" + "="*60)
        print("🔍 VERIFYING DATABASE SETUP")
        print("="*60 + "\n")

        connection = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"Database: {Config.DB_NAME}")
        print(f"Tables found: {len(tables)}\n")
        
        expected_tables = [
            'branches', 'admins', 'teachers', 'students', 'subjects', 
            'class_subjects', 'attendance', 'unrecognized_faces', 'logs', 
            'attendance_summary'
        ]
        found_tables = [table[0] for table in tables]
        
        all_ok = True
        for table in expected_tables:
            if table in found_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table:<25} ({count} records)")
            else:
                print(f"❌ {table:<25} (missing)")
                all_ok = False
        
        cursor.close()
        connection.close()
        
        print("\n" + "="*60 + "\n")
        return all_ok
        
    except Error as e:
        print(f"\n❌ Verification failed: {e}\n")
        return False

def test_connection():
    """Test MySQL connection"""
    try:
        print("\n🔌 Testing MySQL connection...")
        connection = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER, password=Config.DB_PASSWORD
        )
        print(f"✅ Connected to MySQL server at {Config.DB_HOST} (User: {Config.DB_USER})")
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"   MySQL Version: {version[0]}")
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Main setup function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--verify':
            verify_setup()
        elif sys.argv[1] == '--test':
            test_connection()
        elif sys.argv[1] == '--seed':
            seed_database()
        elif sys.argv[1] == '--help':
            print("""
Database Setup Script

Usage:
  python setup_database.py           # Create DB, tables, and seed data
  python setup_database.py --verify  # Verify tables exist and count records
  python setup_database.py --seed    # Insert only sample data
  python setup_database.py --test    # Test MySQL server connection
  python setup_database.py --help    # Show this help message
            """)
        else:
            print(f"Unknown option: {sys.argv[1]}. Use --help for usage information.")
    else:
        # Default action: Full setup
        if not test_connection():
            sys.exit(1)
        
        if create_database_and_tables():
            seed_database()
            verify_setup()
        else:
            sys.exit(1)

if __name__ == '__main__':
    main()