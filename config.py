import os
from datetime import timedelta

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    DEBUG = True
    HOST = '0.0.0.0'  # Allow access from phone on same network
    PORT = 5000
    
    # Database Configuration
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '@Dhruv08'
    DB_NAME = os.environ.get('DB_NAME') or 'attendance_system'
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    STUDENT_IMAGES_FOLDER = 'student_images'
    UNRECOGNIZED_FOLDER = 'unrecognized'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Face Recognition Configuration
    ENCODINGS_FILE = 'encodings.pickle'
    RECOGNITION_TOLERANCE = 0.46  # Lower is more strict
    DETECTION_MODEL = 'hog'  # 'hog' or 'cnn' (cnn is more accurate but slower)
    NUM_JITTERS = 1  # Higher number increases accuracy but slower
    
    # Excel Export Configuration
    EXCEL_EXPORT_PATH = 'exports'
    
    # Logging Configuration
    LOG_FILE = 'logs/attendance.log'
    LOG_LEVEL = 'INFO'
    
    # Backup Configuration
    BACKUP_FOLDER = 'backups'
    AUTO_BACKUP_ENABLED = True
    BACKUP_RETENTION_DAYS = 30