"""Utility Routes - Health checks, dropdowns, and utilities"""

from flask import jsonify
from datetime import datetime
import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

utils_bp = Blueprint('utils', __name__)


@utils_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


@utils_bp.route('/dropdowns/years', methods=['GET'])
def get_years():
    """Get available years"""
    return jsonify({
        'success': True,
        'years': [1, 2, 3, 4]
    }), 200


@utils_bp.route('/dropdowns/sections', methods=['GET'])
def get_sections():
    """Get available sections"""
    return jsonify({
        'success': True,
        'sections': ['A', 'B', 'C', 'D']
    }), 200


@utils_bp.route('/dropdowns/semesters', methods=['GET'])
def get_semesters():
    """Get available semesters"""
    return jsonify({
        'success': True,
        'semesters': list(range(1, 9))
    }), 200


@utils_bp.route('/branches', methods=['GET'])
def get_branches():
    """Get all branches"""
    try:
        from database.db import Database
        
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM branches ORDER BY branch_name")
        branches = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'branches': branches}), 200
    except Exception as e:
        logger.error(f"Get branches error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
