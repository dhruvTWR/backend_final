# # auth/auth.py
# from flask import Blueprint, request, jsonify
# from functools import wraps
# import jwt
# import datetime
# from werkzeug.security import check_password_hash, generate_password_hash
# import os

# auth_bp = Blueprint('auth', __name__)

# # Secret key for JWT - should be in environment variable in production
# SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# # Mock user database - Replace with your actual database queries
# USERS_DB = {
#     'teacher': {
#         'username': 'teacher',
#         'password_hash': generate_password_hash('teacher123'),
#         'role': 'teacher',
#         'id': 'teacher_001'
#     },
#     'admin': {
#         'username': 'admin',
#         'password_hash': generate_password_hash('admin123'),
#         'role': 'admin',
#         'id': 'admin_001'
#     }
# }

# def create_token(user_data):
#     """Create JWT token for authenticated user"""
#     payload = {
#         'user_id': user_data['id'],
#         'username': user_data['username'],
#         'role': user_data['role'],
#         'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),  # Token expires in 24 hours
#         'iat': datetime.datetime.utcnow()
#     }
#     return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# def verify_token(token):
#     """Verify JWT token"""
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
#         return payload
#     except jwt.ExpiredSignatureError:
#         return None
#     except jwt.InvalidTokenError:
#         return None

# def token_required(f):
#     """Decorator to protect routes that require authentication"""
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
        
#         # Get token from Authorization header
#         if 'Authorization' in request.headers:
#             auth_header = request.headers['Authorization']
#             try:
#                 token = auth_header.split(' ')[1]  # Bearer <token>
#             except IndexError:
#                 return jsonify({'message': 'Invalid token format'}), 401
        
#         if not token:
#             return jsonify({'message': 'Authentication token is missing'}), 401
        
#         try:
#             payload = verify_token(token)
#             if not payload:
#                 return jsonify({'message': 'Token is invalid or expired'}), 401
            
#             # Add user info to request context
#             request.current_user = payload
            
#         except Exception as e:
#             return jsonify({'message': 'Token verification failed', 'error': str(e)}), 401
        
#         return f(*args, **kwargs)
    
#     return decorated

# def role_required(allowed_roles):
#     """Decorator to check if user has required role"""
#     def decorator(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             if not hasattr(request, 'current_user'):
#                 return jsonify({'message': 'Authentication required'}), 401
            
#             user_role = request.current_user.get('role')
#             if user_role not in allowed_roles:
#                 return jsonify({'message': 'Insufficient permissions'}), 403
            
#             return f(*args, **kwargs)
#         return decorated
#     return decorator

# @auth_bp.route('/login', methods=['POST'])
# def login():
#     """Login endpoint"""
#     try:
#         data = request.get_json()
        
#         if not data:
#             return jsonify({'message': 'No data provided'}), 400
        
#         username = data.get('username')
#         password = data.get('password')
#         role = data.get('role')
        
#         if not all([username, password, role]):
#             return jsonify({'message': 'Username, password, and role are required'}), 400
        
#         # Find user in database
#         user = USERS_DB.get(username)
        
#         if not user:
#             return jsonify({'message': 'Invalid credentials'}), 401
        
#         # Check password
#         if not check_password_hash(user['password_hash'], password):
#             return jsonify({'message': 'Invalid credentials'}), 401
        
#         # Check role matches
#         if user['role'] != role:
#             return jsonify({'message': 'Invalid role for this user'}), 401
        
#         # Create token
#         token = create_token(user)
        
#         # Return user data (without password)
#         user_data = {
#             'id': user['id'],
#             'username': user['username'],
#             'role': user['role']
#         }
        
#         return jsonify({
#             'message': 'Login successful',
#             'token': token,
#             'user': user_data
#         }), 200
        
#     except Exception as e:
#         return jsonify({'message': 'Login failed', 'error': str(e)}), 500

# @auth_bp.route('/verify', methods=['GET'])
# @token_required
# def verify():
#     """Verify token validity"""
#     return jsonify({
#         'valid': True,
#         'user': {
#             'user_id': request.current_user['user_id'],
#             'username': request.current_user['username'],
#             'role': request.current_user['role']
#         }
#     }), 200

# @auth_bp.route('/logout', methods=['POST'])
# @token_required
# def logout():
#     """Logout endpoint (client-side token removal)"""
#     return jsonify({'message': 'Logout successful'}), 200

# @auth_bp.route('/me', methods=['GET'])
# @token_required
# def get_current_user():
#     """Get current user information"""
#     username = request.current_user['username']
#     user = USERS_DB.get(username)
    
#     if not user:
#         return jsonify({'message': 'User not found'}), 404
    
#     user_data = {
#         'id': user['id'],
#         'username': user['username'],
#         'role': user['role']
#     }
    
#     return jsonify(user_data), 200


# def get_user_from_db(username):
#     """
#     Replace this with your actual database query
#     Example using MySQL:
    
#     from database.db import get_db_connection
    
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
#     user = cursor.fetchone()
#     cursor.close()
#     conn.close()
    
#     return user
#     """
#     return USERS_DB.get(username)

# def create_user_in_db(username, password, role):
#     """
#     Create a new user in database
#     Example:
    
#     from database.db import get_db_connection
    
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     password_hash = generate_password_hash(password)
    
#     query = '''
#         INSERT INTO users (username, password_hash, role)
#         VALUES (%s, %s, %s)
#     '''
    
#     cursor.execute(query, (username, password_hash, role))
#     conn.commit()
    
#     user_id = cursor.lastrowid
#     cursor.close()
#     conn.close()
    
#     return user_id
#     """
#     pass