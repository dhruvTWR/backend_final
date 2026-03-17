"""Unrecognized Faces Routes - Management of unrecognized face detections"""

from flask import request, jsonify, session
import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

unrecognized_bp = Blueprint('unrecognized', __name__)


@unrecognized_bp.route('/', methods=['GET'])
def get_unrecognized_faces():
    """Get unrecognized faces with filters"""
    try:
        from models.unrecognized_face import UnrecognizedFace
        
        class_subject_id = request.args.get('class_subject_id', type=int)
        resolved = request.args.get('resolved', 'false').lower() == 'true'
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        
        unrecognized_model = UnrecognizedFace()
        faces = unrecognized_model.get_unrecognized_faces(
            class_subject_id=class_subject_id,
            resolved=resolved,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return jsonify({'success': True, 'count': len(faces), 'faces': faces}), 200
        
    except Exception as e:
        logger.error(f"Get unrecognized faces error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@unrecognized_bp.route('/count', methods=['GET'])
def get_unresolved_count():
    """Get count of unresolved faces"""
    try:
        from models.unrecognized_face import UnrecognizedFace
        
        class_subject_id = request.args.get('class_subject_id', type=int)
        
        unrecognized_model = UnrecognizedFace()
        count = unrecognized_model.get_unresolved_count(class_subject_id)
        
        return jsonify({'success': True, 'count': count}), 200
        
    except Exception as e:
        logger.error(f"Get unresolved count error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@unrecognized_bp.route('/recent', methods=['GET'])
def get_recent_unresolved():
    """Get recent unresolved faces"""
    try:
        from models.unrecognized_face import UnrecognizedFace
        
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        unrecognized_model = UnrecognizedFace()
        faces = unrecognized_model.get_recent_unresolved(days=days, limit=limit)
        
        return jsonify({'success': True, 'count': len(faces), 'faces': faces}), 200
        
    except Exception as e:
        logger.error(f"Get recent unresolved error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@unrecognized_bp.route('/by-date', methods=['GET'])
def get_unrecognized_by_date():
    """Get unrecognized faces for specific date"""
    try:
        from models.unrecognized_face import UnrecognizedFace
        
        attendance_date = request.args.get('date')
        class_subject_id = request.args.get('class_subject_id', type=int)
        
        if not attendance_date:
            return jsonify({'success': False, 'message': 'date parameter required'}), 400
        
        unrecognized_model = UnrecognizedFace()
        faces = unrecognized_model.get_unrecognized_by_date(
            attendance_date=attendance_date,
            class_subject_id=class_subject_id
        )
        
        return jsonify({'success': True, 'count': len(faces), 'faces': faces}), 200
        
    except Exception as e:
        logger.error(f"Get unrecognized by date error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@unrecognized_bp.route('/<int:face_id>/resolve', methods=['POST'])
def resolve_unrecognized_face(face_id):
    """Resolve an unrecognized face by linking to student"""
    try:
        from models.unrecognized_face import UnrecognizedFace
        
        data = request.get_json()
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'success': False, 'message': 'student_id required'}), 400
        
        unrecognized_model = UnrecognizedFace()
        unrecognized_model.resolve_face(
            unrecognized_id=face_id,
            student_id=student_id,
            resolved_by=session.get('user_id')
        )
        
        return jsonify({'success': True, 'message': 'Face resolved successfully'}), 200
        
    except Exception as e:
        logger.error(f"Resolve face error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@unrecognized_bp.route('/bulk-resolve', methods=['POST'])
def bulk_resolve_faces():
    """Resolve multiple unrecognized faces"""
    try:
        from models.unrecognized_face import UnrecognizedFace
        
        data = request.get_json()
        face_ids = data.get('face_ids', [])
        student_id = data.get('student_id')
        
        if not face_ids or not student_id:
            return jsonify({'success': False, 'message': 'face_ids and student_id required'}), 400
        
        unrecognized_model = UnrecognizedFace()
        count = unrecognized_model.bulk_resolve_faces(
            unrecognized_ids=face_ids,
            student_id=student_id,
            resolved_by=session.get('user_id')
        )
        
        return jsonify({'success': True, 'message': f'Resolved {count} faces', 'count': count}), 200
        
    except Exception as e:
        logger.error(f"Bulk resolve error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@unrecognized_bp.route('/<int:face_id>', methods=['DELETE'])
def delete_unrecognized_face(face_id):
    """Delete an unrecognized face"""
    try:
        from models.unrecognized_face import UnrecognizedFace
        
        unrecognized_model = UnrecognizedFace()
        unrecognized_model.delete_unrecognized(face_id)
        
        return jsonify({'success': True, 'message': 'Face deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete face error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@unrecognized_bp.route('/cleanup', methods=['POST'])
def cleanup_old_resolved():
    """Cleanup old resolved faces (admin only)"""
    try:
        from models.unrecognized_face import UnrecognizedFace
        
        days = request.args.get('days', 90, type=int)
        
        unrecognized_model = UnrecognizedFace()
        deleted_count = unrecognized_model.cleanup_old_resolved(days=days)
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {deleted_count} old records',
            'count': deleted_count
        }), 200
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
