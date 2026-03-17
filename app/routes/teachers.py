"""Teacher Routes - Teacher-specific operations"""

from flask import request, jsonify
import logging
from app.routes import teachers_bp
from models.class_subject import ClassSubject

logger = logging.getLogger(__name__)


@teachers_bp.route('/class-subjects', methods=['GET'])
def get_class_subjects():
    """Get subjects for selected class"""
    try:
        branch_id = request.args.get('branch_id', type=int)
        year = request.args.get('year', type=int)
        section = request.args.get('section')
        academic_year = request.args.get('academic_year')
        
        if not all([branch_id, year, section]):
            return jsonify({'success': False, 'message': 'branch_id, year, section required'}), 400
        
        class_subject_model = ClassSubject()
        subjects = class_subject_model.get_subjects_for_class(
            branch_id, year, section, academic_year
        )
        
        return jsonify({'success': True, 'subjects': subjects}), 200
        
    except Exception as e:
        logger.error(f"Get class subjects error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
