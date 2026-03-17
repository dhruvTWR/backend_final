"""
Database Initialization Script
Creates and initializes the database schema
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_db_connection(database=None):
    """Create database connection"""
    try:
        config = {
            'host': os.environ.get('DB_HOST', 'localhost'),
            'user': os.environ.get('DB_USER', 'root'),
            'password': os.environ.get('DB_PASSWORD', '@Dhruv08'),
        }
        
        if database:
            config['database'] = database
        
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def create_database():
    """Create database if it doesn't exist"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        db_name = os.environ.get('DB_NAME', 'attendance_system')
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"✓ Database '{db_name}' created/exists")
        
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"Error creating database: {e}")
        return False


def create_tables():
    """Create database tables"""
    connection = get_db_connection(os.environ.get('DB_NAME', 'attendance_system'))
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin', 'teacher', 'student') DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("✓ Table 'users' created/exists")
        
        # Students table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT UNIQUE,
                roll_number VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                class VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("✓ Table 'students' created/exists")
        
        # Teachers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT UNIQUE,
                name VARCHAR(100) NOT NULL,
                subject VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("✓ Table 'teachers' created/exists")
        
        # Subjects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                code VARCHAR(20) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Table 'subjects' created/exists")
        
        # Attendance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT PRIMARY KEY AUTO_INCREMENT,
                student_id INT NOT NULL,
                date DATE NOT NULL,
                time TIME,
                status ENUM('present', 'absent', 'late') DEFAULT 'present',
                confidence FLOAT,
                image_path VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE KEY unique_attendance (student_id, date)
            )
        """)
        print("✓ Table 'attendance' created/exists")
        
        # Unrecognized faces table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unrecognized_faces (
                id INT PRIMARY KEY AUTO_INCREMENT,
                image_path VARCHAR(255) NOT NULL,
                confidence FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed BOOLEAN DEFAULT FALSE
            )
        """)
        print("✓ Table 'unrecognized_faces' created/exists")
        
        # Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT,
                action VARCHAR(100),
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        print("✓ Table 'logs' created/exists")
        
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"Error creating tables: {e}")
        return False


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("  Database Initialization - Smart Attendance System")
    print("="*60 + "\n")
    
    print("Creating database...")
    if not create_database():
        print("Failed to create database!")
        sys.exit(1)
    
    print("\nCreating tables...")
    if not create_tables():
        print("Failed to create tables!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ Database initialization completed!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
