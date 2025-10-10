#!/usr/bin/env python3
"""
Smart Attendance System Launcher
Initializes all components and starts the Flask server
"""

import os
import sys
import socket
import webbrowser
from pathlib import Path

def get_local_ip():
    """Get local IP address for network access"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def create_directories():
    """Create required directories if they don't exist"""
    directories = [
        'uploads',
        'student_images',
        'unrecognized',
        'exports',
        'backups',
        'logs',
        'templates',
        'static',
        'database',
        'recognition',
        'utils'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files for packages
    packages = ['database', 'recognition', 'utils']
    for package in packages:
        init_file = Path(package) / '__init__.py'
        if not init_file.exists():
            init_file.touch()

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'flask',
        'flask_cors',
        'mysql.connector',
        'cv2',
        'face_recognition',
        'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'mysql.connector':
                import mysql.connector
            elif package == 'cv2':
                import cv2
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_mysql_connection():
    """Check if MySQL is accessible"""
    try:
        import mysql.connector
        from config import Config
        
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        conn.close()
        return True
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("\n💡 Make sure MySQL is running and credentials are correct in config.py")
        return False

def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║        📸  SMART ATTENDANCE SYSTEM  📊                ║
    ║                                                       ║
    ║         Face Recognition Based Attendance            ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(banner)

def print_access_info(port=5000):
    """Print access information"""
    local_ip = get_local_ip()
    
    print("\n" + "="*55)
    print("🚀 SERVER STARTED SUCCESSFULLY!")
    print("="*55)
    print(f"\n📍 Access URLs:")
    print(f"   Local:    http://localhost:{port}")
    print(f"   Network:  http://{local_ip}:{port}")
    print(f"\n📱 Phone Access:")
    print(f"   Connect phone to same Wi-Fi")
    print(f"   Open: http://{local_ip}:{port}")
    print("\n⌨️  Press Ctrl+C to stop the server")
    print("="*55 + "\n")

def initialize_system():
    """Initialize the attendance system"""
    print("\n🔧 Initializing system...")
    
    # Create directories
    print("   ✓ Creating directories...")
    create_directories()
    
    # Check dependencies
    print("   ✓ Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Check MySQL
    print("   ✓ Checking MySQL connection...")
    if not check_mysql_connection():
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Initialize database
    try:
        print("   ✓ Initializing database...")
        from database.db import Database
        db = Database()
        print("   ✓ Database ready!")
    except Exception as e:
        print(f"   ⚠️  Database initialization warning: {e}")
    
    print("\n✅ System initialization complete!\n")

def main():
    """Main entry point"""
    # Set working directory to script location
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Print banner
    print_banner()
    
    # Initialize system
    initialize_system()
    
    # Import and start Flask app
    try:
        from server import app
        from config import Config
        
        port = Config.PORT
        
        # Print access info
        print_access_info(port)
        
        # Start server
        app.run(
            host=Config.HOST,
            port=port,
            debug=Config.DEBUG,
            use_reloader=False  # Disable reloader for cleaner startup
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\n💡 Check logs/attendance.log for details")
        sys.exit(1)

if __name__ == '__main__':
    main()