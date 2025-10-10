"""
Face Recognition Service - Integrates with your ML model
Works with new database structure (branch, year, section based)
"""

import face_recognition
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import uuid
import os
from config import Config
from models.student import Student

class FaceRecognitionService:
    def __init__(self):
        self.student_model = Student()
        self.tolerance = Config.RECOGNITION_TOLERANCE if hasattr(Config, 'RECOGNITION_TOLERANCE') else 0.46
        self.model = Config.DETECTION_MODEL if hasattr(Config, 'DETECTION_MODEL') else 'hog'
        
        # Cache for loaded encodings
        self.encodings_cache = {}
    
    def load_class_encodings(self, branch_id, year, section):
        """
        Load face encodings for a specific class
        Uses your ML model's recognition logic
        """
        cache_key = f"{branch_id}_{year}_{section}"
        
        # Return cached encodings if available
        if cache_key in self.encodings_cache:
            return self.encodings_cache[cache_key]
        
        try:
            # Get encodings from database using Student model
            encodings_data = self.student_model.get_encodings_for_class(branch_id, year, section)
            
            known_encodings = []
            known_names = []
            known_ids = []
            known_roll_numbers = []
            
            for data in encodings_data:
                known_encodings.append(data['encoding'])
                known_names.append(data['name'])
                known_ids.append(data['student_id'])
                known_roll_numbers.append(data['roll_number'])
            
            result = {
                'encodings': known_encodings,
                'names': known_names,
                'ids': known_ids,
                'roll_numbers': known_roll_numbers
            }
            
            # Cache the result
            self.encodings_cache[cache_key] = result
            
            print(f"Loaded {len(known_encodings)} encodings for class {branch_id}-{year}-{section}")
            return result
            
        except Exception as e:
            print(f"Error loading encodings: {e}")
            return {
                'encodings': [],
                'names': [],
                'ids': [],
                'roll_numbers': []
            }
    
    def generate_encoding(self, image_path):
        """
        Generate face encoding from image
        Matches your generate_encodings.py logic
        """
        try:
            image = face_recognition.load_image_file(image_path)
            
            # Generate encodings (your ML model logic)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                print(f"Encoded {Path(image_path).name}")
                return face_encodings[0]
            else:
                print(f"No face found in {Path(image_path).name}")
                return None
                
        except Exception as e:
            print(f"Error generating encoding: {e}")
            return None
    
    def recognize_students(self, image_path, branch_id, year, section, class_subject_id=None):
        """
        Recognize students in uploaded image
        Matches your recognize_students.py logic with tolerance=0.46
        
        Returns dict with recognized and unrecognized faces
        """
        try:
            # Load class encodings
            class_encodings = self.load_class_encodings(branch_id, year, section)
            
            if not class_encodings['encodings']:
                return {
                    'recognized': [],
                    'unrecognized': [],
                    'total_faces': 0,
                    'error': 'No student encodings found for this class'
                }
            
            # Load and process image (your ML model logic)
            image = face_recognition.load_image_file(image_path)
            opencv_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            print(f"Detected {len(face_locations)} face(s) in the image.")
            print(f"Encodings generated for {len(face_encodings)} face(s).")
            
            recognized_set = set()
            recognized_list = []
            unrecognized = []
            
            # Process each detected face (your recognize_students.py logic)
            for i, (face_encoding, face_location) in enumerate(zip(face_encodings, face_locations)):
                # Compare with known faces using your tolerance (0.46)
                matches = face_recognition.compare_faces(
                    class_encodings['encodings'],
                    face_encoding,
                    tolerance=self.tolerance
                )
                face_distances = face_recognition.face_distance(
                    class_encodings['encodings'],
                    face_encoding
                )
                
                name = "Unrecognized"
                student_id = None
                roll_number = None
                confidence = 0.0
                
                # Find best match (your logic)
                if len(face_distances) > 0 and True in matches:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = class_encodings['names'][best_match_index]
                        student_id = class_encodings['ids'][best_match_index]
                        roll_number = class_encodings['roll_numbers'][best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                
                # Handle recognized students
                if name != "Unrecognized" and name not in recognized_set:
                    recognized_set.add(name)
                    recognized_list.append({
                        'student_id': student_id,
                        'name': name,
                        'roll_number': roll_number,
                        'confidence': float(confidence)
                    })
                    print(f"Recognized: {name} (confidence: {confidence:.2%})")
                
                # Handle unrecognized faces (your logic - save cropped image)
                elif name == "Unrecognized":
                    top, right, bottom, left = face_location
                    face_crop = opencv_image[top:bottom, left:right]
                    
                    # Create unrecognized folder
                    unrecognized_dir = 'uploads/unrecognized_faces'
                    os.makedirs(unrecognized_dir, exist_ok=True)
                    
                    # Save with UUID filename (your logic)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = os.path.join(
                        unrecognized_dir,
                        f"{uuid.uuid4().hex}.jpg"
                    )
                    cv2.imwrite(filename, face_crop)
                    
                    unrecognized.append({
                        'image_path': filename,
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'source_image': Path(image_path).name,
                        'location': face_location,
                        'class_subject_id': class_subject_id
                    })
                    print(f"Unrecognized face saved: {filename}")
            
            result = {
                'recognized': recognized_list,
                'unrecognized': unrecognized,
                'total_faces': len(face_locations)
            }
            
            return result
            
        except Exception as e:
            print(f"Recognition error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def batch_generate_encodings(self, images_folder):
        """
        Generate encodings for all images in folder
        Matches your generate_encodings.py with folder structure
        """
        images_folder = Path(images_folder)
        
        if not images_folder.exists():
            print(f"Error: Directory '{images_folder}' does not exist")
            return []
        
        print("Starting batch encoding process...")
        
        encodings_list = []
        
        # Iterate through each person's folder (your structure)
        for person_name in os.listdir(images_folder):
            person_folder = images_folder / person_name
            
            if not person_folder.is_dir():
                continue
            
            # Iterate through each image in person's folder
            for filename in os.listdir(person_folder):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = person_folder / filename
                    
                    encoding = self.generate_encoding(str(image_path))
                    
                    if encoding is not None:
                        encodings_list.append({
                            'name': person_name.strip(),
                            'encoding': encoding,
                            'image_path': str(image_path),
                            'filename': filename
                        })
                        print(f"Encoded {filename} for {person_name}")
                    else:
                        print(f"No face found in {filename}. Skipping.")
        
        student_count = len(set(e['name'] for e in encodings_list))
        print(f"\nBatch encoding complete.")
        print(f"Total students encoded: {student_count}")
        print(f"Total images processed: {len(encodings_list)}")
        
        return encodings_list
    
    def clear_cache(self, branch_id=None, year=None, section=None):
        """Clear encodings cache for a specific class or all"""
        if branch_id and year and section:
            cache_key = f"{branch_id}_{year}_{section}"
            if cache_key in self.encodings_cache:
                del self.encodings_cache[cache_key]
                print(f"Cache cleared for class {branch_id}-{year}-{section}")
        else:
            self.encodings_cache.clear()
            print("All caches cleared")
    
    def get_face_count(self, image_path):
        """Get number of faces in image (for validation)"""
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image, model=self.model)
            return len(face_locations)
        except Exception as e:
            print(f"Error counting faces: {e}")
            return 0
    
    def update_tolerance(self, new_tolerance):
        """Update recognition tolerance"""
        self.tolerance = new_tolerance
        print(f"Tolerance updated to {new_tolerance}")
    
    def validate_image_quality(self, image_path):
        """Validate if image is suitable for recognition"""
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                return {'valid': False, 'reason': 'No faces detected'}
            
            # Check image resolution
            height, width = image.shape[:2]
            if width < 640 or height < 480:
                return {'valid': False, 'reason': 'Image resolution too low'}
            
            return {'valid': True, 'face_count': len(face_locations)}
            
        except Exception as e:
            return {'valid': False, 'reason': str(e)}