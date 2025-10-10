"""
Recognition Compatibility Layer
Redirects old API calls to new FaceRecognitionService
Maintains backward compatibility with existing code
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.face_recognition_service import FaceRecognitionService

class FaceRecognition:
    """
    Compatibility wrapper for old FaceRecognition class
    Redirects to new FaceRecognitionService
    """
    
    def __init__(self, database=None):
        """Initialize with optional database (for backward compatibility)"""
        self.service = FaceRecognitionService()
        self.db = database
        
        # Default values for backward compatibility
        self.tolerance = self.service.tolerance
        self.model = self.service.model
        self.known_encodings = []
        self.known_names = []
        self.known_ids = []
        self.known_roll_numbers = []
    
    def load_encodings(self, branch_id=1, year=1, section='A'):
        """
        Load encodings (backward compatible)
        Now requires class information
        """
        encodings = self.service.load_class_encodings(branch_id, year, section)
        
        self.known_encodings = encodings['encodings']
        self.known_names = encodings['names']
        self.known_ids = encodings['ids']
        self.known_roll_numbers = encodings['roll_numbers']
        
        return True
    
    def generate_encoding(self, image_path):
        """Generate encoding from image"""
        return self.service.generate_encoding(image_path)
    
    def recognize_students(self, image_path, branch_id=1, year=1, section='A', class_subject_id=None):
        """
        Recognize students in image
        Now requires class information
        """
        return self.service.recognize_students(
            image_path, 
            branch_id, 
            year, 
            section, 
            class_subject_id
        )
    
    def batch_generate_encodings(self, images_folder):
        """Generate encodings for all images in folder"""
        return self.service.batch_generate_encodings(images_folder)
    
    def rebuild_encodings(self, branch_id=1, year=1, section='A'):
        """
        Rebuild encodings (backward compatible)
        Clears cache for specific class
        """
        self.service.clear_cache(branch_id, year, section)
        self.load_encodings(branch_id, year, section)
        print("Encodings rebuilt successfully")
    
    def update_tolerance(self, new_tolerance):
        """Update recognition tolerance"""
        self.service.update_tolerance(new_tolerance)
        self.tolerance = new_tolerance
    
    def get_face_count(self, image_path):
        """Get number of faces in image"""
        return self.service.get_face_count(image_path)
    
    def get_encoding_stats(self):
        """Get statistics about loaded encodings"""
        return {
            'total_students': len(self.known_encodings),
            'unique_names': len(set(self.known_names)),
            'tolerance': self.tolerance,
            'model': self.model
        }

# For backward compatibility with direct imports
if __name__ == '__main__':
    print("This module provides backward compatibility.")
    print("Please use services.face_recognition_service.FaceRecognitionService directly.")