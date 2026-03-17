"""Admin Routes - Core admin operations"""

from flask import request, jsonify
import logging
from app.routes import admin_bp
from models.subjects import Subject
from models.class_subject import ClassSubject

logger = logging.getLogger(__name__)


@admin_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Admin dashboard statistics"""
    try:
        # TODO: Implement dashboard stats
        return jsonify({
            'success': True,
            'message': 'Dashboard endpoint',
            'stats': {}
        }), 200
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/subjects', methods=['GET'])
def get_subjects():
    """Get all subjects"""
    try:
        subject_model = Subject()
        subjects = subject_model.get_all_subjects()
        
        return jsonify({'success': True, 'subjects': subjects}), 200
        
    except Exception as e:
        logger.error(f"Get subjects error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/subjects', methods=['POST'])
def add_subject():
    """Add subject"""
    try:
        data = request.get_json()
        subject_code = data.get('subject_code')
        subject_name = data.get('subject_name')
        
        if not subject_code or not subject_name:
            return jsonify({'success': False, 'message': 'Code and name required'}), 400
        
        subject_model = Subject()
        subject_id = subject_model.add_subject(subject_code, subject_name)
        
        return jsonify({
            'success': True,
            'message': 'Subject added',
            'subject_id': subject_id
        }), 201
        
    except Exception as e:
        logger.error(f"Add subject error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
def delete_subject(subject_id):
    """Delete subject"""
    try:
        subject_model = Subject()
        subject_model.delete_subject(subject_id)
        
        return jsonify({'success': True, 'message': 'Subject deleted'}), 200
        
    except Exception as e:
        logger.error(f"Delete subject error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/subjects/search', methods=['GET'])
def search_subjects():
    """Search subjects"""
    try:
        query = request.args.get('q', '')
        
        subject_model = Subject()
        subjects = subject_model.search_subjects(query)
        
        return jsonify({'success': True, 'subjects': subjects}), 200
        
    except Exception as e:
        logger.error(f"Search subjects error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/class-subjects', methods=['GET'])
def get_class_subjects():
    """Get all class-subject mappings"""
    try:
        academic_year = request.args.get('academic_year')
        branch_id = request.args.get('branch_id', type=int)
        
        class_subject_model = ClassSubject()
        mappings = class_subject_model.get_all_mappings(academic_year, branch_id)
        
        # Format response
        formatted_mappings = []
        for mapping in mappings:
            formatted_mappings.append({
                'class_subject_id': mapping['id'],
                'subject_id': mapping.get('subject_id'),
                'branch_id': mapping['branch_id'],
                'year': mapping['year'],
                'section': mapping['section'],
                'semester': mapping['semester'],
                'academic_year': mapping['academic_year'],
                'is_active': mapping['is_active'],
                'subject_name': mapping['subject_name'],
                'subject_code': mapping['subject_code'],
                'branch_name': mapping['branch_name'],
                'branch_code': mapping['branch_code'],
                'created_at': mapping['created_at']
            })
        
        return jsonify({'success': True, 'mappings': formatted_mappings}), 200
        
    except Exception as e:
        logger.error(f"Get class subjects error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/class-subjects', methods=['POST'])
def add_class_subject():
    """Assign subject to class"""
    try:
        data = request.get_json()
        
        required = ['subject_id', 'branch_id', 'year', 'section', 'semester', 'academic_year']
        if not all(data.get(f) for f in required):
            return jsonify({'success': False, 'message': 'Missing fields'}), 400
        
        class_subject_model = ClassSubject()
        class_subject_id = class_subject_model.assign_subject_to_class(
            subject_id=data['subject_id'],
            branch_id=data['branch_id'],
            year=data['year'],
            section=data['section'],
            semester=data['semester'],
            academic_year=data['academic_year']
        )
        
        return jsonify({
            'success': True,
            'message': 'Subject assigned to class',
            'class_subject_id': class_subject_id
        }), 201
        
    except Exception as e:
        logger.error(f"Add class subject error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/class-subjects/<int:class_subject_id>', methods=['PUT'])
def update_class_subject(class_subject_id):
    """Update class-subject mapping"""
    try:
        data = request.get_json()
        
        class_subject_model = ClassSubject()
        class_subject_model.update_class_subject(
            class_subject_id,
            semester=data.get('semester'),
            academic_year=data.get('academic_year')
        )
        
        return jsonify({'success': True, 'message': 'Mapping updated'}), 200
        
    except Exception as e:
        logger.error(f"Update class subject error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/class-subjects/<int:class_subject_id>', methods=['DELETE'])
def delete_class_subject(class_subject_id):
    """Delete class-subject mapping"""
    try:
        class_subject_model = ClassSubject()
        class_subject_model.delete_class_subject(class_subject_id)
        
        return jsonify({'success': True, 'message': 'Mapping deleted'}), 200
        
    except Exception as e:
        logger.error(f"Delete class subject error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# ADMIN - TEACHER MANAGEMENT
# ============================================================================

@admin_bp.route('/teachers', methods=['GET'])
def get_teachers():
    """Get all teachers"""
    try:
        from models.teacher import Teacher
        
        teacher_model = Teacher()
        teachers = teacher_model.get_all_teachers()
        
        return jsonify({'success': True, 'teachers': teachers}), 200
        
    except Exception as e:
        logger.error(f"Get teachers error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/teachers', methods=['POST'])
def add_teacher():
    """Add new teacher"""
    try:
        from models.teacher import Teacher
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        teacher_model = Teacher()
        teacher_id = teacher_model.add_teacher(username, password)
        
        return jsonify({
            'success': True,
            'message': 'Teacher added',
            'teacher_id': teacher_id
        }), 201
        
    except Exception as e:
        logger.error(f"Add teacher error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/teachers/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    """Update teacher"""
    try:
        from models.teacher import Teacher
        
        data = request.get_json()
        
        teacher_model = Teacher()
        teacher_model.update_teacher(teacher_id, **data)
        
        return jsonify({'success': True, 'message': 'Teacher updated'}), 200
        
    except Exception as e:
        logger.error(f"Update teacher error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/teachers/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    """Delete teacher"""
    try:
        from models.teacher import Teacher
        
        teacher_model = Teacher()
        teacher_model.delete_teacher(teacher_id)
        
        return jsonify({'success': True, 'message': 'Teacher deleted'}), 200
        
    except Exception as e:
        logger.error(f"Delete teacher error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
