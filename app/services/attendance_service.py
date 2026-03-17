"""Attendance Service - Business logic for attendance operations"""

import os
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename


class AttendanceService:
    """Handles all attendance-related business logic"""
    
    def __init__(self, attendance_model, face_service, student_model, 
                 unrecognized_model, class_subject_model):
        self.attendance_model = attendance_model
        self.face_service = face_service
        self.student_model = student_model
        self.unrecognized_model = unrecognized_model
        self.class_subject_model = class_subject_model
    
    def mark_attendance(self, file, class_subject_id, attendance_date_str=None, 
                        session=None, force_process=False):
        """Mark attendance from a single image"""
        
        if attendance_date_str is None:
            attendance_date = date.today()
        elif isinstance(attendance_date_str, str):
            attendance_date = datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
        else:
            attendance_date = attendance_date_str
        
        # Get class info
        class_info = self.class_subject_model.get_class_subject_by_id(class_subject_id)
        if not class_info:
            raise ValueError(f'Class subject ID {class_subject_id} not found')
        
        # Save file
        filename = secure_filename(f"att_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join('uploads/attendance_images', filename)
        file.save(filepath)
        
        # Validate image
        import cv2
        test_img = cv2.imread(filepath)
        if test_img is None:
            os.remove(filepath)
            raise ValueError('Invalid image file')
        
        # Check quality
        quality_check = self.face_service.check_image_quality(filepath)
        
        if not quality_check['acceptable'] and not force_process:
            raise ValueError('Image quality not acceptable')
        
        # Recognize faces
        result = self.face_service.recognize_students(
            image_path=filepath,
            branch_id=class_info['branch_id'],
            year=class_info['year'],
            section=class_info['section'],
            class_subject_id=class_subject_id
        )
        
        if 'error' in result:
            raise ValueError(result['error'])
        
        # Mark attendance
        attendance_ids = []
        attendance_time = datetime.now().time()
        user_id = session.get('user_id') if session else None
        
        # Get all active students in the class
        all_students = self.student_model.get_students_by_class(
            branch_id=class_info['branch_id'],
            year=class_info['year'],
            section=class_info['section']
        )
        
        recognized_student_ids = set(student['student_id'] for student in result.get('recognized', []))
        
        # Mark recognized students as present
        for student in result.get('recognized', []):
            attendance_id = self.attendance_model.mark_attendance(
                student_id=student['student_id'],
                class_subject_id=class_subject_id,
                attendance_date=attendance_date,
                attendance_time=attendance_time,
                status='present',
                confidence=student.get('confidence', 0.0),
                image_path=filepath,
                marked_by=user_id,
                remarks='Face recognition'
            )
            attendance_ids.append(attendance_id)
        
        # Mark absent students (those not recognized)
        for student in all_students:
            if student['id'] not in recognized_student_ids:
                attendance_id = self.attendance_model.mark_attendance(
                    student_id=student['id'],
                    class_subject_id=class_subject_id,
                    attendance_date=attendance_date,
                    attendance_time=attendance_time,
                    status='absent',
                    confidence=0.0,
                    image_path=filepath,
                    marked_by=user_id,
                    remarks='Absent - not recognized'
                )
                attendance_ids.append(attendance_id)
        
        # Save unrecognized faces
        for unrec in result.get('unrecognized', []):
            self.unrecognized_model.add_unrecognized(
                class_subject_id=class_subject_id,
                status='absent',
                image_path=unrec.get('image_path', ''),
                original_upload=filepath,
                attendance_date=attendance_date
            )
        
        # Prepare complete attendance data with all students
        complete_students = []
        for student in all_students:
            if student['id'] in recognized_student_ids:
                # Find recognized student data
                rec_student = next((s for s in result.get('recognized', []) if s['student_id'] == student['id']), None)
                complete_students.append({
                    'student_id': student['id'],
                    'name': student['name'],
                    'roll_number': student['roll_number'],
                    'status': 'present',
                    'confidence': rec_student.get('confidence', 0.0) if rec_student else 0.0,
                    'image_path': filepath,
                    'remarks': 'Face recognition'
                })
            else:
                complete_students.append({
                    'student_id': student['id'],
                    'name': student['name'],
                    'roll_number': student['roll_number'],
                    'status': 'absent',
                    'confidence': 0.0,
                    'image_path': filepath,
                    'remarks': 'Absent - not recognized'
                })
        
        return {
            'attendance_ids': attendance_ids,
            'recognized_count': len(result.get('recognized', [])),
            'unrecognized_count': len(result.get('unrecognized', [])),
            'total_faces': result.get('total_faces', 0),
            'students': complete_students,
            'class_strength': self.student_model.get_class_strength(
                class_info['branch_id'],
                class_info['year'],
                class_info['section']
            )
        }
    
    def mark_attendance_batch(self, files, class_subject_id, attendance_date_str=None, 
                             session=None, skip_quality_check=False):
        """Mark attendance from multiple images"""
        
        if attendance_date_str is None:
            attendance_date = date.today()
        elif isinstance(attendance_date_str, str):
            attendance_date = datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
        else:
            attendance_date = attendance_date_str
        
        # Get class info
        class_info = self.class_subject_model.get_class_subject_by_id(class_subject_id)
        if not class_info:
            raise ValueError(f'Class subject ID {class_subject_id} not found')
        
        # Process files
        saved_files = []
        quality_checks = []
        
        for idx, file in enumerate(files):
            filename = secure_filename(f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}_{file.filename}")
            filepath = os.path.join('uploads/attendance_images', filename)
            file.save(filepath)
            
            # Validate
            import cv2
            test_img = cv2.imread(filepath)
            if test_img is None:
                os.remove(filepath)
                quality_checks.append({
                    'filename': file.filename,
                    'acceptable': False,
                    'error': 'Invalid image format'
                })
                continue
            
            # Check quality
            if not skip_quality_check:
                quality_result = self.face_service.check_image_quality(filepath)
                quality_checks.append({
                    'filename': file.filename,
                    **quality_result
                })
                
                if not quality_result['acceptable']:
                    continue
            
            saved_files.append(filepath)
        
        if not saved_files:
            raise ValueError('No acceptable images found')
        
        # Recognize in batch
        result = self.face_service.batch_recognize_students(
            image_paths=saved_files,
            branch_id=class_info['branch_id'],
            year=class_info['year'],
            section=class_info['section'],
            class_subject_id=class_subject_id
        )
        
        # Mark attendance
        attendance_ids = []
        attendance_time = datetime.now().time()
        user_id = session.get('user_id') if session else None
        
        # Get all active students in the class
        all_students = self.student_model.get_students_by_class(
            branch_id=class_info['branch_id'],
            year=class_info['year'],
            section=class_info['section']
        )
        
        recognized_student_ids = set(student['student_id'] for student in result.get('recognized', []))
        
        # Mark recognized students as present
        for student in result.get('recognized', []):
            attendance_id = self.attendance_model.mark_attendance(
                student_id=student['student_id'],
                class_subject_id=class_subject_id,
                attendance_date=attendance_date,
                attendance_time=attendance_time,
                status='present',
                confidence=student.get('confidence', 0.0),
                image_path=saved_files[0],
                marked_by=user_id,
                remarks=f'Batch recognition ({len(saved_files)} images)'
            )
            attendance_ids.append(attendance_id)
        
        # Mark absent students (those not recognized)
        for student in all_students:
            if student['id'] not in recognized_student_ids:
                attendance_id = self.attendance_model.mark_attendance(
                    student_id=student['id'],
                    class_subject_id=class_subject_id,
                    attendance_date=attendance_date,
                    attendance_time=attendance_time,
                    status='absent',
                    confidence=0.0,
                    image_path=saved_files[0],
                    marked_by=user_id,
                    remarks='Absent - not recognized in batch'
                )
                attendance_ids.append(attendance_id)
        
        # Save unrecognized
        for unrec in result.get('unrecognized', []):
            self.unrecognized_model.add_unrecognized(
                class_subject_id=class_subject_id,
                status='absent',
                image_path=unrec.get('image_path', ''),
                original_upload=unrec.get('source_image', ''),
                attendance_date=attendance_date
            )
        
        # Prepare complete attendance data with all students
        complete_students = []
        for student in all_students:
            if student['id'] in recognized_student_ids:
                # Find recognized student data
                rec_student = next((s for s in result.get('recognized', []) if s['student_id'] == student['id']), None)
                complete_students.append({
                    'student_id': student['id'],
                    'name': student['name'],
                    'roll_number': student['roll_number'],
                    'status': 'present',
                    'confidence': rec_student.get('confidence', 0.0) if rec_student else 0.0,
                    'image_path': saved_files[0],
                    'remarks': f'Batch recognition ({len(saved_files)} images)'
                })
            else:
                complete_students.append({
                    'student_id': student['id'],
                    'name': student['name'],
                    'roll_number': student['roll_number'],
                    'status': 'absent',
                    'confidence': 0.0,
                    'image_path': saved_files[0],
                    'remarks': 'Absent - not recognized in batch'
                })
        
        return {
            'attendance_ids': attendance_ids,
            'recognized_count': len(result.get('recognized', [])),
            'unrecognized_count': len(result.get('unrecognized', [])),
            'students': complete_students,
            'class_strength': self.student_model.get_class_strength(
                class_info['branch_id'],
                class_info['year'],
                class_info['section']
            )
        }
    
    def mark_attendance_manual(self, student_id, class_subject_id, status='present',
                              attendance_date_str=None, session=None, remarks='Manually marked'):
        """Manually mark attendance for a student"""
        
        if attendance_date_str is None:
            attendance_date = date.today()
        elif isinstance(attendance_date_str, str):
            attendance_date = datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
        else:
            attendance_date = attendance_date_str
        
        user_id = session.get('user_id') if session else None
        
        attendance_id = self.attendance_model.mark_attendance(
            student_id=student_id,
            class_subject_id=class_subject_id,
            attendance_date=attendance_date,
            attendance_time=datetime.now().time(),
            status=status,
            marked_by=user_id,
            remarks=remarks
        )
        
        return attendance_id
    
    def get_attendance_report(self, class_subject_id, start_date, end_date):
        """Get attendance report for date range"""
        return self.attendance_model.get_attendance_by_date_range(
            class_subject_id, start_date, end_date
        )
    
    def get_attendance_report_aggregated(self, class_subject_id, start_date, end_date):
        """Get aggregated attendance report with counts"""
        return self.attendance_model.get_class_attendance_report(
            class_subject_id, start_date, end_date
        )
    
    def get_attendance_by_date(self, class_subject_id, attendance_date):
        """Get attendance for specific date"""
        return self.attendance_model.get_attendance_by_date(
            class_subject_id, attendance_date
        )
    
    def check_image_quality(self, file):
        """Check image quality before processing"""
        filename = secure_filename(f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        temp_path = os.path.join('uploads/attendance_images', filename)
        file.save(temp_path)
        
        quality_result = self.face_service.check_image_quality(temp_path)
        quality_result['temp_path'] = filename
        
        return quality_result
