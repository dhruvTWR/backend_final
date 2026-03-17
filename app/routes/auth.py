"""Authentication Routes"""

from flask import request, jsonify, session
import logging
from app.routes import auth_bp

logger = logging.getLogger(__name__)


@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin login"""
    try:
        from models.admin import Admin
        admin_model = Admin()
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        admin = admin_model.authenticate(username, password)
        
        if admin:
            session['user_id'] = admin['id']
            session['user_type'] = 'admin'
            session['username'] = admin['username']
            
            return jsonify({'success': True, 'message': 'Login successful', 'user': admin}), 200
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/teacher/login', methods=['POST'])
def teacher_login():
    """Teacher login"""
    try:
        from models.teacher import Teacher
        teacher_model = Teacher()
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        teacher = teacher_model.authenticate(username, password)
        
        if teacher:
            session['user_id'] = teacher['id']
            session['user_type'] = 'teacher'
            session['username'] = teacher['username']
            
            return jsonify({'success': True, 'message': 'Login successful', 'user': teacher}), 200
        
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
    except Exception as e:
        logger.error(f"Teacher login error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'}), 200


@auth_bp.route('/verify', methods=['GET'])
def verify_session():
    """Verify session"""
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session.get('username'),
                'type': session.get('user_type')
            }
        }), 200
    return jsonify({'success': True, 'authenticated': False}), 200
