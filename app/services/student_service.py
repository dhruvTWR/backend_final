"""Student Service - Business logic for student operations"""

import os
from werkzeug.utils import secure_filename
from datetime import datetime


class StudentService:
    """Handles all student-related business logic"""
    
    def __init__(self, student_model, face_service):
        self.student_model = student_model
        self.face_service = face_service
    
    def get_all_students(self, branch_id=None, year=None):
        """Get all students with optional filters"""
        return self.student_model.get_all_students(branch_id, year)
    
    def get_students_by_class(self, branch_id, year, section):
        """Get students for a specific class"""
        return self.student_model.get_students_by_class(branch_id, year, section)
    
    def add_student(self, roll_number, name, email, branch_id, year, section, file):
        """Add new student with photo"""
        # Save photo
        filename = secure_filename(f"{roll_number}_{file.filename}")
        photo_path = os.path.join('uploads/student_images', filename)
        file.save(photo_path)
        
        # Generate face encoding
        encoding = self.face_service.generate_encoding(photo_path)
        if encoding is None:
            os.remove(photo_path)
            raise ValueError('No face detected in image')
        
        # Add to database
        student_id = self.student_model.add_student(
            roll_number=roll_number,
            name=name,
            email=email,
            branch_id=branch_id,
            year=year,
            section=section,
            face_encoding=encoding,
            photo_path=photo_path
        )
        
        return student_id
    
    def update_student(self, student_id, name=None, email=None, file=None):
        """Update student information with photo and face encoding"""
        update_data = {}
        
        if name:
            update_data['name'] = name
        if email:
            update_data['email'] = email
        
        if file:
            # Get existing student to retrieve roll_number for consistent filename
            existing_student = self.student_model.get_student_by_id(student_id)
            if not existing_student:
                raise ValueError('Student not found')
            
            roll_number = existing_student.get('roll_number') or f"student_{student_id}"
            
            # Save new photo with consistent naming
            filename = secure_filename(f"{roll_number}_{file.filename}")
            photo_path = os.path.join('uploads/student_images', filename)
            file.save(photo_path)
            
            # Generate new face encoding
            encoding = self.face_service.generate_encoding(photo_path)
            if encoding is None:
                # Delete uploaded photo if face detection failed
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                raise ValueError('No face detected in image. Please upload a clear photo.')
            
            # Update both photo path and face encoding
            update_data['photo_path'] = photo_path
            update_data['face_encoding'] = encoding
        
        self.student_model.update_student(student_id, **update_data)
    
    def delete_student(self, student_id):
        """Soft delete a student"""
        self.student_model.delete_student(student_id, soft_delete=True)
    
    def search_students(self, query):
        """Search students by name or roll number"""
        return self.student_model.search_students(query)
    
    def get_class_strength(self, branch_id, year, section):
        """Get total student count for a class"""
        return self.student_model.get_class_strength(branch_id, year, section)
