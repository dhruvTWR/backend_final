# Smart Attendance System - Backend

A Flask-based face recognition attendance system with role-based access control.

## Project Structure

```
├── app/                           # Main application package
│   ├── __init__.py               # Flask app factory
│   ├── routes/                   # API endpoints (blueprints)
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── attendance.py        # Attendance endpoints
│   │   ├── students.py          # Student management
│   │   ├── teachers.py          # Teacher management
│   │   └── admin.py             # Admin endpoints
│   ├── models/                   # Database models
│   ├── services/                 # Business logic
│   ├── utils/                    # Utility functions
│   ├── middleware/               # Middleware (auth, error handling)
│   └── static/                   # CSS, JS files
├── config/                        # Configuration
│   ├── config.py                # Main config
│   └── constants.py             # System constants
├── database/                      # Database setup
│   └── db.py                     # Database connection
├── uploads/                       # User-uploaded files
│   ├── student_images/          # Student photos
│   ├── attendance_images/       # Attendance captures
│   └── unrecognized_faces/      # Unrecognized captures
├── exports/                       # Generated exports (Excel, etc)
├── logs/                          # Application logs
├── backups/                       # Database backups
├── tests/                         # Unit & integration tests
├── docs/                          # Documentation
├── templates/                     # HTML templates
├── run_app.py                    # Entry point
└── requirements.txt              # Python dependencies
```

## Quick Start

### Setup

1. **Clone and navigate:**
   ```bash
   cd backend_final
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Initialize database:**
   ```bash
   python setup_db.py
   ```

6. **Run application:**
   ```bash
   python run_app.py
   ```

Server runs on `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/register` - Register

### Attendance
- `POST /api/attendance/mark` - Mark attendance with face
- `GET /api/attendance/history` - Get attendance history
- `GET /api/attendance/report` - Generate report

### Students
- `GET /api/students` - List all students
- `POST /api/students` - Create student
- `POST /api/students/<id>/upload-photo` - Upload student photo

### Teachers
- `GET /api/teachers` - List all teachers
- `POST /api/teachers` - Create teacher

### Admin
- `GET /api/admin/dashboard` - Dashboard stats
- `POST /api/admin/export` - Export attendance data

## Configuration

Environment variables in `.env`:
- `DB_HOST`, `DB_USER`, `DB_PASSWORD` - Database
- `RECOGNITION_TOLERANCE` - Face recognition strictness (lower = stricter)
- `CORS_ORIGINS` - Allowed frontend URLs

## Database Models

- **Student** - Student information and enrollment
- **Teacher** - Teacher records
- **Admin** - Admin users
- **Subject** - Subject/Course
- **ClassSubject** - Class-Subject mapping
- **Attendance** - Attendance records
- **UnrecognizedFace** - Unrecognized face captures
- **Log** - System logs

## Key Features

- ✅ Face recognition-based attendance
- ✅ Role-based access control
- ✅ Real-time face detection
- ✅ Excel export
- ✅ Attendance history
- ✅ Image quality checking
- ✅ Comprehensive logging

## Development

Run tests:
```bash
pytest tests/
```

Check code quality:
```bash
pylint app/
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use production WSGI server (Gunicorn):
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
   ```
3. Use environment-specific config
4. Setup SSL/HTTPS
5. Configure database backups

## Troubleshooting

- **Database connection error**: Check `DB_HOST`, `DB_USER`, `DB_PASSWORD`
- **Face recognition slow**: Try `DETECTION_MODEL=hog` (faster) vs `cnn` (accurate)
- **CORS errors**: Verify `CORS_ORIGINS` in `.env` matches frontend URL

## License

Proprietary - Smart Attendance System
