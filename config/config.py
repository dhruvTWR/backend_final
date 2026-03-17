"""Configuration Module"""

import os
from datetime import timedelta

class Config:
    """Base Configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Database
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '@Dhruv08')
    DB_NAME = os.environ.get('DB_NAME', 'attendance_system')
    
    # Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    STUDENT_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'student_images')
    ATTENDANCE_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'attendance_images')
    UNRECOGNIZED_FOLDER = os.path.join(UPLOAD_FOLDER, 'unrecognized_faces')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Face Recognition
    ENCODINGS_FILE = 'encodings.pickle'
    RECOGNITION_TOLERANCE = float(os.environ.get('RECOGNITION_TOLERANCE', 0.46))
    DETECTION_MODEL = os.environ.get('DETECTION_MODEL', 'hog')
    NUM_JITTERS = int(os.environ.get('NUM_JITTERS', 1))
    BLUR_THRESHOLD = int(os.environ.get('BLUR_THRESHOLD', 0))
    MIN_BRIGHTNESS = int(os.environ.get('MIN_BRIGHTNESS', 0))
    MAX_BRIGHTNESS = int(os.environ.get('MAX_BRIGHTNESS', 10000000000))
    
    # Export
    EXCEL_EXPORT_PATH = 'exports'
    
    # Logging
    LOG_FILE = 'logs/attendance.log'
    LOG_LEVEL = 'INFO'
    
    # Backup
    BACKUP_FOLDER = 'backups'
    AUTO_BACKUP_ENABLED = True
    BACKUP_RETENTION_DAYS = 30
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Set True for production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    

class TestingConfig(Config):
    """Testing Configuration"""
    TESTING = True
    DEBUG = True
    DB_NAME = 'attendance_system_test'


# Config mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
