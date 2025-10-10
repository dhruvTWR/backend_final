"""
Student Model - Handles student management and face encoding operations
"""

import pickle
from datetime import datetime
from database.db import Database

class Student:
    def __init__(self):
        self.db = Database()
    
    def add_student(self, roll_number, name, email, branch_id, year, section, face_encoding=None, photo_path=None):
        """Add new student with face encoding"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Serialize face encoding if provided
            encoding_blob = pickle.dumps(face_encoding) if face_encoding is not None else None
            
            query = """
                INSERT INTO students 
                (roll_number, name, email, branch_id, year, section, face_encoding, photo_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (roll_number, name, email, branch_id, year, section, encoding_blob, photo_path))
            
            student_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Student added: {name} ({roll_number})")
            return student_id
            
        except Exception as e:
            print(f"Error adding student: {e}")
            raise
    
    # def get_student_by_id(self, student_id):
    #     """Get student by ID"""
    #     try:
    #         conn = self.db.get_connection()
    #         cursor = conn.cursor(dictionary=True)
            
    #         query = """
    #             SELECT s.*, b.branch_name, b.branch_code
    #             FROM students s
    #             JOIN branches b ON s.branch_id = b.id
    #             WHERE s.id = %s AND s.is_active = TRUE
    #         """
    #         cursor.execute(query, (student_id,))
    #         student = cursor.fetchone()
            
    #         # Deserialize face encoding if present
    #         if student and student['face_encoding']:
    #             student['face_encoding'] = pickle.loads(student['face_encoding'])
            
    #         cursor.close()
    #         conn.close()
            
    #         return student
            
    #     except Exception as e:
    #         print(f"Error getting student: {e}")
    #         raise
    
    
    
    def get_students_by_class(self, branch_id, year, section):
        """Get all students in a specific class"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT s.id, s.roll_number, s.name, s.email, s.year, s.section,
                       b.branch_name, b.branch_code, s.photo_path
                FROM students s
                JOIN branches b ON s.branch_id = b.id
                WHERE s.branch_id = %s AND s.year = %s AND s.section = %s 
                      AND s.is_active = TRUE
                ORDER BY s.roll_number
            """
            cursor.execute(query, (branch_id, year, section))
            students = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return students
            
        except Exception as e:
            print(f"Error getting students by class: {e}")
            raise
    
    
    
    def update_student(self, student_id, **kwargs):
        """Update student information"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            allowed_fields = ['name', 'email', 'branch_id', 'year', 'section', 'photo_path', 'is_active']
            
            for field in allowed_fields:
                if field in kwargs:
                    set_clauses.append(f"{field} = %s")
                    values.append(kwargs[field])
            
            # Handle face encoding separately
            if 'face_encoding' in kwargs:
                set_clauses.append("face_encoding = %s")
                values.append(pickle.dumps(kwargs['face_encoding']))
            
            if not set_clauses:
                return
            
            values.append(student_id)
            query = f"UPDATE students SET {', '.join(set_clauses)} WHERE id = %s"
            
            cursor.execute(query, tuple(values))
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Student updated: ID {student_id}")
            
        except Exception as e:
            print(f"Error updating student: {e}")
            raise
    
    def delete_student(self, student_id, soft_delete=True):
        """Delete student (soft delete by default)"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            if soft_delete:
                query = "UPDATE students SET is_active = FALSE WHERE id = %s"
            else:
                query = "DELETE FROM students WHERE id = %s"
            
            cursor.execute(query, (student_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Student {'deactivated' if soft_delete else 'deleted'}: ID {student_id}")
            
        except Exception as e:
            print(f"Error deleting student: {e}")
            raise
    
    
    def search_students(self, search_term):
        """Search students by name or roll number"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT s.id, s.roll_number, s.name, s.email, s.year, s.section,
                       b.branch_name, b.branch_code
                FROM students s
                JOIN branches b ON s.branch_id = b.id
                WHERE (s.name LIKE %s OR s.roll_number LIKE %s) AND s.is_active = TRUE
                ORDER BY s.name
                LIMIT 50
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern))
            students = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return students
            
        except Exception as e:
            print(f"Error searching students: {e}")
            raise
    
    def get_student_attendance_summary(self, student_id):
        """Get attendance summary for a student across all subjects"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    s.subject_name,
                    cs.semester,
                    asummary.total_classes,
                    asummary.classes_attended,
                    asummary.attendance_percentage
                FROM attendance_summary asummary
                JOIN class_subjects cs ON asummary.class_subject_id = cs.id
                JOIN subjects s ON cs.subject_id = s.id
                WHERE asummary.student_id = %s
                ORDER BY cs.semester, s.subject_name
            """
            cursor.execute(query, (student_id,))
            summary = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return summary
            
        except Exception as e:
            print(f"Error getting attendance summary: {e}")
            raise
        
    def get_encodings_for_class(self, branch_id, year, section):
        """
        Get face encodings for all active students in a class
        Returns list of dicts with student_id, name, roll_number, encoding
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
        
            cursor.execute("""
                SELECT 
                    id as student_id,
                    roll_number,
                    name,
                    face_encoding
                FROM students
                WHERE branch_id = %s 
                AND year = %s 
                AND section = %s
                AND is_active = TRUE
                AND face_encoding IS NOT NULL
                ORDER BY roll_number
            """, (branch_id, year, section))
        
            students = cursor.fetchall()
            cursor.close()
            conn.close()
        
            # Deserialize face encodings
            result = []
            for student in students:
                if student['face_encoding']:
                    try:
                        import pickle
                        encoding = pickle.loads(student['face_encoding'])
                        result.append({
                            'student_id': student['student_id'],
                            'name': student['name'],
                            'roll_number': student['roll_number'],
                            'encoding': encoding
                        })
                    except Exception as e:
                        print(f"Error deserializing encoding for {student['name']}: {e}")
        
            print(f"Loaded {len(result)} encodings for class {branch_id}-{year}-{section}")
            return result
        
        except Exception as e:
            print(f"Error getting encodings for class: {e}")
            import traceback
            traceback.print_exc()
            raise
        
        
    def bulk_import_students(self, students_data):
        """Bulk import students from list"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO students 
                (roll_number, name, email, branch_id, year, section, face_encoding, photo_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            imported = 0
            errors = 0
            
            for student in students_data:
                try:
                    encoding_blob = pickle.dumps(student.get('face_encoding')) if student.get('face_encoding') else None
                    cursor.execute(query, (
                        student['roll_number'],
                        student['name'],
                        student.get('email'),
                        student['branch_id'],
                        student['year'],
                        student['section'],
                        encoding_blob,
                        student.get('photo_path')
                    ))
                    imported += 1
                except Exception as e:
                    errors += 1
                    print(f"Error importing {student.get('roll_number')}: {e}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Bulk import complete: {imported} imported, {errors} errors")
            return {'imported': imported, 'errors': errors}
            
        except Exception as e:
            print(f"Error in bulk import: {e}")
            raise
        

    
    # def get_encodings_for_class(self, branch_id, year, section):
    #     try:
    #         conn = self.db.get_connection()
    #         cursor = conn.cursor(dictionary=True)
        
    #         cursor.execute("""
    #             SELECT 
    #                 id as student_id,
    #                 roll_number,
    #                 name,
    #                 face_encoding
    #             FROM students
    #             WHERE branch_id = %s 
    #             AND year = %s 
    #             AND section = %s
    #             AND is_active = TRUE
    #             AND face_encoding IS NOT NULL
    #             ORDER BY roll_number
    #         """, (branch_id, year, section))
        
    #         students = cursor.fetchall()
    #         cursor.close()
    #         conn.close()
        
    #         # Deserialize face encodings
    #         result = []
    #         for student in students:
    #             if student['face_encoding']:
    #                 try:
    #                     import pickle
    #                     encoding = pickle.loads(student['face_encoding'])
    #                     result.append({
    #                         'student_id': student['student_id'],
    #                         'name': student['name'],
    #                         'roll_number': student['roll_number'],
    #                         'encoding': encoding
    #                     })
    #                 except Exception as e:
    #                     print(f"Error deserializing encoding for {student['name']}: {e}")
        
    #         print(f"Loaded {len(result)} encodings for class {branch_id}-{year}-{section}")
    #         return result
        
    #     except Exception as e:
    #         print(f"Error getting encodings for class: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         raise