"""API Route Blueprints - Register all routes here"""

from flask import Blueprint

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
attendance_bp = Blueprint('attendance', __name__, url_prefix='/api/teacher/attendance')
students_bp = Blueprint('students', __name__, url_prefix='/api/admin/students')
teachers_bp = Blueprint('teachers', __name__, url_prefix='/api/teacher')
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Import route handlers (must be after blueprint creation)
from app.routes import auth
from app.routes import attendance
from app.routes import students
from app.routes import teachers
from app.routes import admin

# Register standalone blueprints
from app.routes.utils import utils_bp
from app.routes.unrecognized_faces import unrecognized_bp
from app.routes.logs import logs_bp

__all__ = [
    'auth_bp', 'attendance_bp', 'students_bp', 'teachers_bp', 'admin_bp',
    'utils_bp', 'unrecognized_bp', 'logs_bp'
]
