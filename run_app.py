#!/usr/bin/env python3
"""
Smart Attendance System - Application Launcher
Entry point for development and setup
"""

import os
import sys
import socket
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


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


def print_banner():
    """Print application banner"""
    banner = """
╔════════════════════════════════════════════════════════╗
║                                                        ║
║       📸 SMART ATTENDANCE SYSTEM - API SERVER 📊      ║
║                                                        ║
║         Face Recognition Based Attendance             ║
║                      v2.0                             ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_access_info(host, port):
    """Print server access information"""
    local_ip = get_local_ip()
    
    print("\n" + "="*60)
    print("🚀  SERVER STARTED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📱 Access the server at:")
    print(f"   Local:     http://localhost:{port}")
    print(f"   Network:   http://{local_ip}:{port}")
    print(f"\n📚 API Documentation:")
    print(f"   Endpoints: http://localhost:{port}/api/")
    print(f"   Health:    http://localhost:{port}/api/health")
    print(f"\n✅ Status: Running")
    print(f"🔐 CORS Enabled: Yes")
    print(f"🐍 Python: Yes (Modular Structure)")
    print("\n⚠️  Press CTRL+C to stop the server")
    print("="*60 + "\n")


def main():
    """Main entry point"""
    
    print_banner()
    
    # Create Flask app
    from app import create_app
    
    app = create_app()
    
    # Get host and port
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') == 'True'
    
    print_access_info(host, port)
    
    # Run application
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            use_debugger=debug
        )
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    # Set up variables for printing access URLs
    import os
    port = int(os.environ.get('PORT', 5000))
    from socket import gethostbyname, gethostname
    try:
        local_ip = gethostbyname(gethostname())
    except Exception:
        local_ip = 'localhost'
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
    def create_directories():
        """Create required directories for the system"""
        required_dirs = [
            "logs",
            "uploads",
            "attendance_data",
            "models"
        ]
        for d in required_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
        print("      - Directories created:", ", ".join(required_dirs))

    create_directories()
    
    # Check dependencies
    print("   ✓ Checking dependencies...")
    def check_dependencies():
        """Check for required Python dependencies"""
        required_packages = {
            "flask": "flask",
            "mysql.connector": "mysql",
            "python-dotenv": "dotenv",
            "requests": "requests",
            "opencv-python": "cv2",
            "face-recognition": "face_recognition"
        }
        missing = []
        for pkg_name, import_name in required_packages.items():
            try:
                __import__(import_name)
            except ImportError:
                missing.append(pkg_name)
        if missing:
            print(f"   ⚠️  Missing dependencies: {', '.join(missing)}")
            print("      Please install them using pip before continuing.")
            return False
        print("      - All dependencies satisfied.")
        return True

    if not check_dependencies():
        sys.exit(1)
    
    # Check MySQL
    print("   ✓ Checking MySQL connection...")
    def check_mysql_connection():
        """Check if MySQL connection can be established"""
        try:
            import mysql.connector
            from mysql.connector import Error
            from config import Config
            
            connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
            if connection.is_connected():
                connection.close()
                print("      - MySQL connection successful.")
                return True
        except Exception as e:
            print(f"      ⚠️  MySQL connection failed: {e}")
            return False

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
        from app import create_app
        from config import Config

        app = create_app()
        port = Config.PORT

        # Print access info
        print_access_info(Config.HOST, port)

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