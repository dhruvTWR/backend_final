import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from config import Config

def setup_logger():
    """Setup application logger with file and console handlers"""
    
    # Create logs directory if not exists
    log_dir = os.path.dirname(Config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create logger
    logger = logging.getLogger('attendance_system')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Remove existing handlers
    logger.handlers = []
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger