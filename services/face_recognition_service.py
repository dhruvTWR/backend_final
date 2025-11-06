"""
Enhanced Face Recognition Service with Image Quality Checks
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
        # Use config values or defaults
        self.BLUR_THRESHOLD = getattr(Config, 'BLUR_THRESHOLD', 50.0)
        self.MIN_BRIGHTNESS = getattr(Config, 'MIN_BRIGHTNESS', 40)
        self.MAX_BRIGHTNESS = getattr(Config, 'MAX_BRIGHTNESS', 220)
    
        self.encodings_cache = {}
    
    def check_image_quality(self, image_path):
        """
        Check image quality for blur, lighting, and resolution
        Returns quality report with accept/reject decision
        """
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                return {
                    'acceptable': False,
                    'error': 'Could not read image file',
                    'issues': ['Invalid image format']
                }
            
            issues = []
            warnings = []
            
            # 1. Check blur using Laplacian variance
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if blur_score < self.BLUR_THRESHOLD:
                issues.append({
                    'type': 'blur',
                    'severity': 'critical',
                    'message': f'Image is too blurred (score: {blur_score:.2f})',
                    'recommendation': 'Hold camera steady and ensure proper focus'
                })
            
            # 2. Check brightness
            mean_brightness = np.mean(gray)
            
            if mean_brightness < self.MIN_BRIGHTNESS:
                issues.append({
                    'type': 'lighting',
                    'severity': 'critical',
                    'message': 'Image is too dark',
                    'recommendation': 'Improve lighting conditions'
                })
            elif mean_brightness > self.MAX_BRIGHTNESS:
                warnings.append({
                    'type': 'lighting',
                    'severity': 'warning',
                    'message': 'Image may be overexposed',
                    'recommendation': 'Avoid direct bright light'
                })
            
            # 3. Check resolution
            height, width = image.shape[:2]
            if width < 640 or height < 480:
                warnings.append({
                    'type': 'resolution',
                    'severity': 'warning',
                    'message': f'Low resolution ({width}x{height})',
                    'recommendation': 'Use higher resolution if possible'
                })
            
            # Calculate quality score
            quality_score = 100
            if blur_score < self.BLUR_THRESHOLD:
                quality_score -= 50
            if mean_brightness < self.MIN_BRIGHTNESS or mean_brightness > self.MAX_BRIGHTNESS:
                quality_score -= 30
            if width < 640 or height < 480:
                quality_score -= 20
            
            return {
                'acceptable': len(issues) == 0,
                'quality_score': max(0, quality_score),
                'blur_score': float(blur_score),
                'brightness': float(mean_brightness),
                'resolution': {'width': width, 'height': height},
                'issues': issues,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'acceptable': False,
                'error': str(e),
                'issues': [{'type': 'error', 'message': str(e)}]
            }
    
    def load_class_encodings(self, branch_id, year, section):
        """Load face encodings for a specific class"""
        cache_key = f"{branch_id}_{year}_{section}"
        
        if cache_key in self.encodings_cache:
            return self.encodings_cache[cache_key]
        
        try:
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
            
            self.encodings_cache[cache_key] = result
            print(f"Loaded {len(known_encodings)} encodings for class {branch_id}-{year}-{section}")
            return result
            
        except Exception as e:
            print(f"Error loading encodings: {e}")
            return {'encodings': [], 'names': [], 'ids': [], 'roll_numbers': []}
    
    def generate_encoding(self, image_path):
        """Generate face encoding from image"""
        try:
            image = face_recognition.load_image_file(image_path)
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
        Recognize students with quality check
        """
        try:
            # First check image quality
            quality_check = self.check_image_quality(image_path)
        
        # ADD THIS: Resize large images for faster processing
            import cv2
            from PIL import Image
        
        # Load and resize if needed
            img = cv2.imread(image_path)
            height, width = img.shape[:2]
        
        # If image is larger than 1920px, resize it
            max_width = 1920
            if width > max_width:
                scale = max_width / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
                cv2.imwrite(image_path, img)  # Save resized version
        
            if not quality_check['acceptable']:
                return {
                    'recognized': [],
                    'unrecognized': [],
                    'total_faces': 0,
                    'quality_check': quality_check,
                    'error': 'Image quality not acceptable',
                    'issues': quality_check.get('issues', [])
                }
            
            # Load class encodings
            class_encodings = self.load_class_encodings(branch_id, year, section)
            
            if not class_encodings['encodings']:
                return {
                    'recognized': [],
                    'unrecognized': [],
                    'total_faces': 0,
                    'quality_check': quality_check,
                    'error': 'No student encodings found for this class'
                }
            
            # Load and process image
            image = face_recognition.load_image_file(image_path)
            opencv_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            print(f"Detected {len(face_locations)} face(s) in the image.")
            
            recognized_set = set()
            recognized_list = []
            unrecognized = []
            
            # Process each detected face
            for i, (face_encoding, face_location) in enumerate(zip(face_encodings, face_locations)):
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
                
                if len(face_distances) > 0 and True in matches:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = class_encodings['names'][best_match_index]
                        student_id = class_encodings['ids'][best_match_index]
                        roll_number = class_encodings['roll_numbers'][best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                
                if name != "Unrecognized" and name not in recognized_set:
                    recognized_set.add(name)
                    recognized_list.append({
                        'student_id': student_id,
                        'name': name,
                        'roll_number': roll_number,
                        'confidence': float(confidence)
                    })
                    print(f"Recognized: {name} (confidence: {confidence:.2%})")
                
                elif name == "Unrecognized":
                    top, right, bottom, left = face_location
                    face_crop = opencv_image[top:bottom, left:right]
                    
                    unrecognized_dir = 'uploads/unrecognized_faces'
                    os.makedirs(unrecognized_dir, exist_ok=True)
                    
                    filename = os.path.join(unrecognized_dir, f"{uuid.uuid4().hex}.jpg")
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
                'total_faces': len(face_locations),
                'quality_check': quality_check
            }
            
            return result
            
        except Exception as e:
            print(f"Recognition error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def batch_recognize_students(self, image_paths, branch_id, year, section, class_subject_id=None):
        """
        Process multiple images at once for better attendance coverage
        Returns combined results from all images
        """
        all_recognized = {}  # Using dict to avoid duplicates
        all_unrecognized = []
        total_faces = 0
        quality_reports = []
        failed_images = []
        
        for image_path in image_paths:
            try:
                result = self.recognize_students(
                    image_path, branch_id, year, section, class_subject_id
                )
                
                quality_reports.append({
                    'image_path': image_path,
                    'quality_check': result.get('quality_check')
                })
                
                if not result.get('quality_check', {}).get('acceptable', False):
                    failed_images.append({
                        'image_path': image_path,
                        'reason': 'quality_check_failed',
                        'issues': result.get('issues', [])
                    })
                    continue
                
                # Merge recognized students (avoid duplicates)
                for student in result.get('recognized', []):
                    student_id = student['student_id']
                    if student_id not in all_recognized:
                        all_recognized[student_id] = student
                    else:
                        # Keep higher confidence
                        if student['confidence'] > all_recognized[student_id]['confidence']:
                            all_recognized[student_id] = student
                
                all_unrecognized.extend(result.get('unrecognized', []))
                total_faces += result.get('total_faces', 0)
                
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                failed_images.append({
                    'image_path': image_path,
                    'reason': 'processing_error',
                    'error': str(e)
                })
        
        return {
            'recognized': list(all_recognized.values()),
            'unrecognized': all_unrecognized,
            'total_faces': total_faces,
            'images_processed': len(image_paths),
            'images_failed': len(failed_images),
            'quality_reports': quality_reports,
            'failed_images': failed_images
        }
    
    def clear_cache(self, branch_id=None, year=None, section=None):
        """Clear encodings cache"""
        if branch_id and year and section:
            cache_key = f"{branch_id}_{year}_{section}"
            if cache_key in self.encodings_cache:
                del self.encodings_cache[cache_key]
        else:
            self.encodings_cache.clear()