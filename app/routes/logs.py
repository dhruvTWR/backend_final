"""System Logs Routes - Logging and audit trail"""

from flask import request, jsonify
import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

logs_bp = Blueprint('logs', __name__)


@logs_bp.route('/', methods=['GET'])
def get_logs():
    """Get system logs with filters"""
    try:
        from models.log import Log
        
        log_type = request.args.get('log_type')
        user_type = request.args.get('user_type')
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        
        log_model = Log()
        logs = log_model.get_logs(
            log_type=log_type,
            user_type=user_type,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        return jsonify({'success': True, 'count': len(logs), 'logs': logs}), 200
        
    except Exception as e:
        logger.error(f"Get logs error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logs_bp.route('/recent', methods=['GET'])
def get_recent_logs():
    """Get most recent logs"""
    try:
        from models.log import Log
        
        limit = request.args.get('limit', 100, type=int)
        
        log_model = Log()
        logs = log_model.get_recent_logs(limit=limit)
        
        return jsonify({'success': True, 'count': len(logs), 'logs': logs}), 200
        
    except Exception as e:
        logger.error(f"Get recent logs error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logs_bp.route('/errors', methods=['GET'])
def get_error_logs():
    """Get error logs from last N hours"""
    try:
        from models.log import Log
        
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        log_model = Log()
        errors = log_model.get_error_logs(hours=hours, limit=limit)
        
        return jsonify({'success': True, 'count': len(errors), 'errors': errors}), 200
        
    except Exception as e:
        logger.error(f"Get error logs error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logs_bp.route('/attendance', methods=['GET'])
def get_attendance_logs():
    """Get attendance-related logs"""
    try:
        from models.log import Log
        from datetime import datetime
        
        date_str = request.args.get('date')
        limit = request.args.get('limit', 100, type=int)
        
        log_model = Log()
        
        if date_str:
            from datetime import date
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            logs = log_model.get_attendance_logs(date=attendance_date, limit=limit)
        else:
            logs = log_model.get_attendance_logs(limit=limit)
        
        return jsonify({'success': True, 'count': len(logs), 'logs': logs}), 200
        
    except Exception as e:
        logger.error(f"Get attendance logs error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logs_bp.route('/admin-actions', methods=['GET'])
def get_admin_actions():
    """Get admin action logs"""
    try:
        from models.log import Log
        
        limit = request.args.get('limit', 50, type=int)
        
        log_model = Log()
        logs = log_model.get_admin_actions(limit=limit)
        
        return jsonify({'success': True, 'count': len(logs), 'logs': logs}), 200
        
    except Exception as e:
        logger.error(f"Get admin actions error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logs_bp.route('/by-action', methods=['GET'])
def get_logs_by_action():
    """Get logs filtered by specific action"""
    try:
        from models.log import Log
        
        action = request.args.get('action')
        limit = request.args.get('limit', 50, type=int)
        
        if not action:
            return jsonify({'success': False, 'message': 'action parameter required'}), 400
        
        log_model = Log()
        logs = log_model.get_logs_by_action(action, limit=limit)
        
        return jsonify({'success': True, 'count': len(logs), 'logs': logs}), 200
        
    except Exception as e:
        logger.error(f"Get logs by action error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@logs_bp.route('/cleanup', methods=['POST'])
def cleanup_old_logs():
    """Delete old logs (admin only)"""
    try:
        from models.log import Log
        
        days = request.args.get('days', 90, type=int)
        
        log_model = Log()
        deleted_count = log_model.cleanup_old_logs(days=days)
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {deleted_count} old logs',
            'count': deleted_count
        }), 200
        
    except Exception as e:
        logger.error(f"Cleanup logs error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
