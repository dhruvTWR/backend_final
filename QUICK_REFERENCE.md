"""
QUICK REFERENCE - Developer Cheat Sheet
═════════════════════════════════════════════════════════════════════════════

🚀 RUNNING THE APPLICATION
───────────────────────────────────────────────────────────────────────────

Development:
  $ python run_app.py
  → Runs with debug=True, auto-reload enabled
  → Access: http://localhost:5000

Production:
  $ gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
  → 4 worker processes
  → Access: http://0.0.0.0:5000

Direct:
  $ python -m app
  → Runs from app/__init__.py

═════════════════════════════════════════════════════════════════════════════

📁 FOLDER REFERENCE
───────────────────────────────────────────────────────────────────────────

app/                     - Main Flask application
  ├── routes/           - API endpoints (organized by domain)
  ├── services/         - Business logic layer
  ├── models/           - [TODO] Move models here
  ├── utils/            - [TODO] Move utilities here
  ├── middleware/       - Middleware & decorators
  ├── static/           - CSS, JS, images
  └── __init__.py       - App factory

config/                  - Configuration files
  ├── config.py         - Environment configs (dev/prod/test)
  └── constants.py      - Application constants

tests/                   - Unit & integration tests
docs/                    - Documentation (API, SETUP, DATABASE)
uploads/                 - User uploads (gitignored)
exports/                 - Generated files (gitignored)
logs/                    - Application logs (gitignored)
backups/                 - Database backups (gitignored)

═════════════════════════════════════════════════════════════════════════════

🔌 ADDING A NEW ENDPOINT
───────────────────────────────────────────────────────────────────────────

1. Create route in appropriate file:
   app/routes/students.py (if student-related)

2. Use the blueprint:
   from app.routes import students_bp
   
   @students_bp.route('/new', methods=['GET'])
   def new_endpoint():
       return jsonify({'success': True}), 200

3. Route auto-registers via app/routes/__init__.py

4. Access at: /api/students/new

═════════════════════════════════════════════════════════════════════════════

🛠️ ADDING A SERVICE
───────────────────────────────────────────────────────────────────────────

1. Create service class:
   app/services/my_service.py

   class MyService:
       def __init__(self, model):
           self.model = model
       
       def do_something(self):
           return self.model.get_data()

2. Use in routes:
   from app.services.my_service import MyService
   
   service = MyService(my_model)
   result = service.do_something()

═════════════════════════════════════════════════════════════════════════════

📝 BLUEPRINT STRUCTURE
───────────────────────────────────────────────────────────────────────────

Main blueprints (already registered with url_prefix):
  - auth_bp       → /api/auth/
  - attendance_bp → /api/attendance/
  - students_bp   → /api/students/
  - teachers_bp   → /api/teachers/
  - admin_bp      → /api/admin/

Utility blueprints (registered in app/__init__.py):
  - utils_bp           → /api/utils/
  - unrecognized_bp    → /api/unrecognized-faces/
  - logs_bp            → /api/logs/

═════════════════════════════════════════════════════════════════════════════

🔑 COMMON IMPORTS
───────────────────────────────────────────────────────────────────────────

# From Flask
from flask import request, jsonify, session, send_file
from datetime import datetime, date

# Models
from models.student import Student
from models.attendance import Attendance
from models.teacher import Teacher

# Services
from app.services.student_service import StudentService
from app.services.attendance_service import AttendanceService

# Configuration
from config.config import Config
from config.constants import ROLES

# App routes
from app.routes import auth_bp, attendance_bp, students_bp

═════════════════════════════════════════════════════════════════════════════

🧪 TESTING ENDPOINTS
───────────────────────────────────────────────────────────────────────────

Health Check:
  GET /api/health
  → {'status': 'healthy', 'app': '...', 'version': '2.0'}

Authentication:
  POST /api/auth/admin/login
  → {'success': true, 'user': {...}}

Attendance:
  POST /api/attendance/mark
  → Form data with file
  → {'success': true, 'recognized_count': 5}

Students:
  GET /api/students
  → {'success': true, 'count': 50, 'students': [...]}

═════════════════════════════════════════════════════════════════════════════

🔒 ERROR HANDLING
───────────────────────────────────────────────────────────────────────────

Common response patterns:

Success:
  return jsonify({'success': True, 'data': {...}}), 200

Error:
  return jsonify({'success': False, 'message': 'Error description'}), 400

Not Found:
  return jsonify({'success': False, 'message': 'Resource not found'}), 404

Server Error:
  return jsonify({'success': False, 'message': str(e)}), 500

═════════════════════════════════════════════════════════════════════════════

🌍 ENVIRONMENT VARIABLES (.env)
───────────────────────────────────────────────────────────────────────────

Flask:
  FLASK_ENV=development
  SECRET_KEY=your-secret-key
  DEBUG=True
  HOST=0.0.0.0
  PORT=5000

Database:
  DB_HOST=localhost
  DB_USER=root
  DB_PASSWORD=password
  DB_NAME=attendance_system

Face Recognition:
  RECOGNITION_TOLERANCE=0.46
  DETECTION_MODEL=hog
  NUM_JITTERS=1

CORS:
  CORS_ORIGINS=http://localhost:3000,http://localhost:3001

═════════════════════════════════════════════════════════════════════════════

📊 LOG LEVELS
───────────────────────────────────────────────────────────────────────────

import logging
logger = logging.getLogger(__name__)

logger.debug('Debug message')      # Development details
logger.info('Info message')        # Important events
logger.warning('Warning message')  # Warnings
logger.error('Error message')      # Errors
logger.critical('Critical msg')    # System failures

═════════════════════════════════════════════════════════════════════════════

💾 DATABASE OPERATIONS
───────────────────────────────────────────────────────────────────────────

Initialize database:
  $ python setup_db.py

Query database:
  from database.db import Database
  db = Database()
  conn = db.get_connection()
  cursor = conn.cursor(dictionary=True)
  cursor.execute("SELECT * FROM students")
  results = cursor.fetchall()

═════════════════════════════════════════════════════════════════════════════

🐛 DEBUGGING
───────────────────────────────────────────────────────────────────────────

Print debug info:
  print(f"Debug: {variable}")
  logger.debug(f"Debug: {variable}")

Check imports:
  python -c "from app.routes import attendance_bp"

Validate syntax:
  python -m py_compile app/routes/attendance.py

Test specific route:
  python -c "from app import create_app; app = create_app()"

═════════════════════════════════════════════════════════════════════════════

📚 DOCUMENTATION
───────────────────────────────────────────────────────────────────────────

API Endpoints:        docs/API.md
Setup Guide:          docs/SETUP.md
Database Schema:      docs/DATABASE.md
Project Overview:     README.md
Migration Guide:      MIGRATION_GUIDE.md
Migration Summary:    MIGRATION_SUMMARY.md
Project Structure:    PROJECT_STRUCTURE.md

═════════════════════════════════════════════════════════════════════════════

⚠️ COMMON MISTAKES
───────────────────────────────────────────────────────────────────────────

❌ Running from wrong directory:
   cd /path/to/backend_final
   python run_app.py

❌ Forgetting to import blueprint:
   from app.routes import my_bp

❌ Wrong blueprint url_prefix assignment:
   # Don't modify - it's already set!
   # @my_bp.route() works because url_prefix is in Blueprint()

❌ Not handling exceptions:
   try:
       # code
   except Exception as e:
       logger.error(f"Error: {e}")
       return jsonify({'success': False, 'message': str(e)}), 500

❌ Not validating input:
   data = request.get_json()
   if not data.get('required_field'):
       return jsonify({'success': False}), 400

═════════════════════════════════════════════════════════════════════════════

🎯 DEVELOPMENT WORKFLOW
───────────────────────────────────────────────────────────────────────────

1. Plan your feature
2. Create service class in app/services/
3. Add routes in appropriate app/routes/ file
4. Test with curl or Postman
5. Update tests in tests/
6. Update documentation
7. Commit and deploy

═════════════════════════════════════════════════════════════════════════════

🚢 DEPLOYMENT CHECKLIST
───────────────────────────────────────────────────────────────────────────

□ Update .env for production
□ Set DEBUG=False
□ Set SECRET_KEY to secure value
□ Verify database credentials
□ Run database migrations
□ Install Gunicorn
□ Test with: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
□ Setup Nginx/Apache reverse proxy
□ Configure SSL/HTTPS
□ Setup logging
□ Configure monitoring
□ Test all endpoints
□ Backup database

═════════════════════════════════════════════════════════════════════════════

📞 TROUBLESHOOTING
───────────────────────────────────────────────────────────────────────────

Cannot import module:
  → Check if you're in project root
  → Verify __init__.py files exist
  → Check sys.path

Port already in use:
  → Change PORT in .env
  → Or kill process: lsof -ti:5000 | xargs kill -9

Database connection error:
  → Verify MySQL is running
  → Check credentials in .env
  → Run: python setup_db.py

CORS errors:
  → Check CORS_ORIGINS in .env
  → Verify frontend URL is in the list
  → Test with curl -H "Origin: ..."

═════════════════════════════════════════════════════════════════════════════

✅ READY TO GO!

Your modular Face Recognition Attendance System is now ready for development,
testing, and deployment. Happy coding!

═════════════════════════════════════════════════════════════════════════════
"""
