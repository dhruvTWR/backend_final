"""Student Management Routes - Admin operations"""

from flask import request, jsonify, session
import logging
from app.routes import students_bp
from app.services.student_service import StudentService
from models.student import Student
from services.face_recognition_service import FaceRecognitionService

logger = logging.getLogger(__name__)


def _get_student_service():
    """Get student service instance"""
    student_model = Student()
    face_service = FaceRecognitionService()
    return StudentService(student_model, face_service)


@students_bp.route('/', methods=['GET'])
def list_students():
    """Get all students with optional filters"""
    try:
        branch_id = request.args.get('branch_id', type=int)
        year = request.args.get('year', type=int)
        section = request.args.get('section')
        
        student_model = Student()
        
        if branch_id and year and section:
            students = student_model.get_students_by_class(branch_id, year, section)
        else:
            students = student_model.get_all_students(branch_id, year)
        
        return jsonify({'success': True, 'count': len(students), 'students': students}), 200
        
    except Exception as e:
        logger.error(f"List students error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@students_bp.route('/', methods=['POST'])
def create_student():
    """Create new student with photo"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'Photo required'}), 400
        
        file = request.files['file']
        roll_number = request.form.get('roll_number')
        name = request.form.get('name')
        email = request.form.get('email')
        branch_id = request.form.get('branch_id', type=int)
        year = request.form.get('year', type=int)
        section = request.form.get('section')
        
        if not all([roll_number, name, branch_id, year, section]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        service = _get_student_service()
        student_id = service.add_student(
            roll_number=roll_number,
            name=name,
            email=email or '',
            branch_id=branch_id,
            year=year,
            section=section,
            file=file
        )
        
        return jsonify({
            'success': True,
            'message': 'Student added successfully',
            'student_id': student_id
        }), 201
        
    except Exception as e:
        logger.error(f"Create student error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@students_bp.route('/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    """Update student information"""
    try:
        file = request.files.get('file')
        
        service = _get_student_service()
        service.update_student(
            student_id=student_id,
            name=request.form.get('name'),
            email=request.form.get('email'),
            file=file
        )
        
        return jsonify({'success': True, 'message': 'Student updated'}), 200
        
    except Exception as e:
        logger.error(f"Update student error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@students_bp.route('/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete student"""
    try:
        service = _get_student_service()
        service.delete_student(student_id)
        
        return jsonify({'success': True, 'message': 'Student deleted'}), 200
        
    except Exception as e:
        logger.error(f"Delete student error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@students_bp.route('/search', methods=['GET'])
def search_students():
    """Search students"""
    try:
        query = request.args.get('q', '')
        
        student_model = Student()
        students = student_model.search_students(query)
        
        return jsonify({'success': True, 'students': students}), 200
        
    except Exception as e:
        logger.error(f"Search students error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@students_bp.route('/promote-year', methods=['POST'])
def promote_students_year():
    """Bulk promote students to next year"""
    try:
        data = request.get_json()
        current_year = data.get('current_year')
        branch_id = data.get('branch_id')
        
        if not current_year:
            return jsonify({'success': False, 'message': 'Current year is required'}), 400
        
        # Convert to integers
        current_year = int(current_year)
        if branch_id and branch_id != 'all':
            branch_id = int(branch_id)
        else:
            branch_id = None
        
        next_year = current_year + 1
        
        student_model = Student()
        affected_count = student_model.promote_students_to_next_year(current_year, branch_id)
        
        return jsonify({
            'success': True,
            'message': f'Successfully promoted {affected_count} students from Year {current_year} to Year {next_year}',
            'affected_count': affected_count,
            'promoted_to_year': next_year
        }), 200
        
    except Exception as e:
        logger.error(f"Promote students error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500