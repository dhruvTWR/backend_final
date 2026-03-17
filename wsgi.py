"""
Production WSGI Entry Point
Used by Gunicorn and other WSGI servers
"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create application instance for WSGI servers
app = create_app()

if __name__ == '__main__':
    # Development only
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('DEBUG', 'False') == 'True'
    )
