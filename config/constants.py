"""Project Constants"""

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Role definitions
ROLES = {
    'ADMIN': 'admin',
    'TEACHER': 'teacher',
    'STUDENT': 'student'
}

# API Response codes
RESPONSE_CODES = {
    'SUCCESS': 200,
    'CREATED': 201,
    'BAD_REQUEST': 400,
    'UNAUTHORIZED': 401,
    'FORBIDDEN': 403,
    'NOT_FOUND': 404,
    'CONFLICT': 409,
    'SERVER_ERROR': 500
}

# Face recognition settings
FACE_RECOGNITION = {
    'MIN_CONFIDENCE': 0.6,
    'TOLERANCE': 0.46,
    'NUM_JITTERS': 1,
    'MODEL': 'hog'  # or 'cnn'
}

# Image quality settings
IMAGE_QUALITY = {
    'BLUR_THRESHOLD': 100,
    'MIN_BRIGHTNESS': 30,
    'MAX_BRIGHTNESS': 200
}
