"""
Flask Application Factory
Initializes Flask app with all blueprints and configurations
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app(config=None):
    """
    Application factory
    Creates and configures Flask application
    """
    
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        from config.config import Config
        config = Config
    
    app.config.from_object(config)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup CORS
    allowed_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(
        app,
        supports_credentials=True,
        origins=allowed_origins,
        allow_headers=['Content-Type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    )
    
    # Create required directories
    _create_directories()
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'app': 'Face Recognition Attendance System',
            'version': '2.0'
        }), 200
    
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'message': 'Face Recognition Attendance System API',
            'version': '2.0',
            'status': 'running'
        }), 200
    
    return app


def _create_directories():
    """Create required application directories"""
    directories = [
        'uploads',
        'uploads/student_images',
        'uploads/attendance_images',
        'uploads/unrecognized_faces',
        'exports',
        'logs',
        'backups',
        'app/static'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def _register_blueprints(app):
    """Register all API blueprints"""
    
    from app.routes import (
        auth_bp, attendance_bp, students_bp, teachers_bp, admin_bp,
        utils_bp, unrecognized_bp, logs_bp
    )
    
    # Register main blueprints with url_prefix already set in Blueprint
    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(admin_bp)
    
    # Register utility blueprints (no /utils prefix - endpoints are /api/branches, /api/dropdowns/*, etc)
    app.register_blueprint(utils_bp, url_prefix='/api')
    app.register_blueprint(unrecognized_bp, url_prefix='/api/unrecognized-faces')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')


def _register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False, 'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'success': False, 'error': 'Forbidden'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        app.logger.error(f'Server error: {error}')
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', True)
    )
