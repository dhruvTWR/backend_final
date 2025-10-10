"""
Attendance Model - Handles attendance marking, tracking, and reporting
"""

from datetime import datetime, date, timedelta
from database.db import Database

class Attendance:
    def __init__(self):
        self.db = Database()
    
    def mark_attendance(self, student_id, class_subject_id, attendance_date, 
                       attendance_time, status='present', confidence=0.0, 
                       image_path=None, marked_by=None, remarks=None):
        """Mark attendance for a student"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Check if attendance already exists
            check_query = """
                SELECT id FROM attendance 
                WHERE student_id = %s AND class_subject_id = %s AND attendance_date = %s
            """
            cursor.execute(check_query, (student_id, class_subject_id, attendance_date))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                query = """
                    UPDATE attendance 
                    SET attendance_time = %s, status = %s, confidence = %s, 
                        image_path = %s, marked_by = %s, remarks = %s
                    WHERE id = %s
                """
                cursor.execute(query, (attendance_time, status, confidence, 
                                     image_path, marked_by, remarks, existing[0]))
                attendance_id = existing[0]
            else:
                # Insert new record
                query = """
                    INSERT INTO attendance 
                    (student_id, class_subject_id, attendance_date, attendance_time, 
                     status, confidence, image_path, marked_by, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (student_id, class_subject_id, attendance_date, 
                                     attendance_time, status, confidence, image_path, 
                                     marked_by, remarks))
                attendance_id = cursor.lastrowid
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Update summary
            self.update_attendance_summary(student_id, class_subject_id)
            
            return attendance_id
            
        except Exception as e:
            print(f"Error marking attendance: {e}")
            raise
    
    def mark_bulk_attendance(self, attendance_records):
        """Mark attendance for multiple students at once"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            marked = 0
            errors = 0
            
            for record in attendance_records:
                try:
                    # Check if exists
                    check_query = """
                        SELECT id FROM attendance 
                        WHERE student_id = %s AND class_subject_id = %s AND attendance_date = %s
                    """
                    cursor.execute(check_query, (record['student_id'], record['class_subject_id'], 
                                                record['attendance_date']))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update
                        query = """
                            UPDATE attendance 
                            SET attendance_time = %s, status = %s, confidence = %s, 
                                image_path = %s, marked_by = %s
                            WHERE id = %s
                        """
                        cursor.execute(query, (
                            record['attendance_time'], 
                            record.get('status', 'present'), 
                            record.get('confidence', 0.0),
                            record.get('image_path'),
                            record.get('marked_by'),
                            existing[0]
                        ))
                    else:
                        # Insert
                        query = """
                            INSERT INTO attendance 
                            (student_id, class_subject_id, attendance_date, attendance_time, 
                             status, confidence, image_path, marked_by)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(query, (
                            record['student_id'],
                            record['class_subject_id'],
                            record['attendance_date'],
                            record['attendance_time'],
                            record.get('status', 'present'),
                            record.get('confidence', 0.0),
                            record.get('image_path'),
                            record.get('marked_by')
                        ))
                    
                    # Update summary
                    self.update_attendance_summary(record['student_id'], record['class_subject_id'])
                    marked += 1
                    
                except Exception as e:
                    errors += 1
                    print(f"Error marking attendance for student {record.get('student_id')}: {e}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {'marked': marked, 'errors': errors}
            
        except Exception as e:
            print(f"Error in bulk attendance marking: {e}")
            raise
    
    def get_attendance_by_date(self, class_subject_id, attendance_date):
        """Get attendance records for a specific date"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
        
            cursor.execute("""
                SELECT 
                    a.id,
                    a.student_id,
                    s.roll_number,
                    s.name,
                    a.attendance_date,
                    a.attendance_time,
                    a.status,
                    a.confidence,
                    a.image_path,
                    a.remarks
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                WHERE a.class_subject_id = %s 
                AND a.attendance_date = %s
                ORDER BY s.roll_number
            """, (class_subject_id, attendance_date))
        
            records = cursor.fetchall()
            cursor.close()
            conn.close()
        
        # Serialize all records
            return [self._serialize_attendance(record) for record in records]
        
        except Exception as e:
            print(f"Error getting attendance by date: {e}")
            raise
    
    def get_student_attendance(self, student_id, class_subject_id=None, 
                              start_date=None, end_date=None):
        """Get attendance records for a specific student"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    a.attendance_date,
                    a.attendance_time,
                    a.status,
                    a.confidence,
                    s.subject_name,
                    cs.semester,
                    b.branch_name
                FROM attendance a
                JOIN class_subjects cs ON a.class_subject_id = cs.id
                JOIN subjects s ON cs.subject_id = s.id
                JOIN branches b ON cs.branch_id = b.id
                WHERE a.student_id = %s
            """
            params = [student_id]
            
            if class_subject_id:
                query += " AND a.class_subject_id = %s"
                params.append(class_subject_id)
            
            if start_date:
                query += " AND a.attendance_date >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND a.attendance_date <= %s"
                params.append(end_date)
            
            query += " ORDER BY a.attendance_date DESC"
            
            cursor.execute(query, tuple(params))
            records = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return records
            
        except Exception as e:
            print(f"Error getting student attendance: {e}")
            raise
    
    def get_class_attendance_report(self, class_subject_id, start_date=None, end_date=None):
        """Get complete attendance report for a class"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    s.id as student_id,
                    s.roll_number,
                    s.name,
                    COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present_count,
                    COUNT(a.id) as total_classes,
                    ROUND((COUNT(CASE WHEN a.status = 'present' THEN 1 END) * 100.0 / 
                           NULLIF(COUNT(a.id), 0)), 2) as attendance_percentage
                FROM students s
                LEFT JOIN attendance a ON s.id = a.student_id 
                    AND a.class_subject_id = %s
            """
            params = [class_subject_id]
            
            if start_date:
                query += " AND a.attendance_date >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND a.attendance_date <= %s"
                params.append(end_date)
            
            query += """
                WHERE s.is_active = TRUE
                GROUP BY s.id, s.roll_number, s.name
                ORDER BY s.roll_number
            """
            
            cursor.execute(query, tuple(params))
            report = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return report
            
        except Exception as e:
            print(f"Error getting class attendance report: {e}")
            raise
        
    def get_attendance_by_date_range(self, class_subject_id, start_date, end_date):
        """Get attendance records between two dates"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    a.id,
                    a.student_id,
                    s.roll_number,
                    s.name,
                    a.attendance_date,
                    a.attendance_time,
                    a.status,
                    a.confidence,
                    a.remarks
                FROM attendance a
                JOIN students s ON a.student_id = s.id
                WHERE a.class_subject_id = %s 
                AND a.attendance_date BETWEEN %s AND %s
                ORDER BY a.attendance_date, s.roll_number
            """, (class_subject_id, start_date, end_date))
            
            records = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [self._serialize_attendance(record) for record in records]
            
        except Exception as e:
            print(f"Error getting attendance by date range: {e}")
            raise   
    
    
    def update_attendance_summary(self, student_id, class_subject_id):
        """Update attendance summary for a student in a subject"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Calculate totals
            query = """
                SELECT 
                    COUNT(*) as total_classes,
                    SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as classes_attended
                FROM attendance
                WHERE student_id = %s AND class_subject_id = %s
            """
            cursor.execute(query, (student_id, class_subject_id))
            result = cursor.fetchone()
            
            total_classes = int(result[0]) if result[0] else 0
            classes_attended = int(result[1]) if result[1] else 0
            attendance_percentage = (classes_attended * 100.0 / total_classes) if total_classes > 0 else 0.0
            
            # Update or insert summary
            update_query = """
                INSERT INTO attendance_summary 
                (student_id, class_subject_id, total_classes, classes_attended, attendance_percentage)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    total_classes = %s,
                    classes_attended = %s,
                    attendance_percentage = %s
            """
            cursor.execute(update_query, (
                student_id, class_subject_id, total_classes, classes_attended, attendance_percentage,
                total_classes, classes_attended, attendance_percentage
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error updating attendance summary: {e}")
            raise
    
    def get_attendance_statistics(self, class_subject_id, date=None):
        """Get attendance statistics for a class"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            if date is None:
                date = datetime.now().date()
            
            # Today's attendance
            query = """
                SELECT 
                    COUNT(DISTINCT CASE WHEN status = 'present' THEN student_id END) as present_count,
                    COUNT(DISTINCT student_id) as total_students
                FROM attendance
                WHERE class_subject_id = %s AND attendance_date = %s
            """
            cursor.execute(query, (class_subject_id, date))
            today_stats = cursor.fetchone()
            
            # Overall statistics
            overall_query = """
                SELECT 
                    AVG(attendance_percentage) as avg_attendance,
                    MIN(attendance_percentage) as min_attendance,
                    MAX(attendance_percentage) as max_attendance
                FROM attendance_summary
                WHERE class_subject_id = %s
            """
            cursor.execute(overall_query, (class_subject_id,))
            overall_stats = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                'today': today_stats,
                'overall': overall_stats
            }
            
        except Exception as e:
            print(f"Error getting attendance statistics: {e}")
            raise
    
    def delete_attendance_record(self, attendance_id):
        """Delete an attendance record"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get student and class info before deleting
            query = "SELECT student_id, class_subject_id FROM attendance WHERE id = %s"
            cursor.execute(query, (attendance_id,))
            record = cursor.fetchone()
            
            if record:
                # Delete record
                delete_query = "DELETE FROM attendance WHERE id = %s"
                cursor.execute(delete_query, (attendance_id,))
                conn.commit()
                
                # Update summary
                self.update_attendance_summary(record['student_id'], record['class_subject_id'])
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error deleting attendance record: {e}")
            raise
    
    def _serialize_attendance(self, record):
        """Convert database record to JSON-serializable dict"""
        if isinstance(record.get('attendance_time'), timedelta):
            # Convert timedelta to time string
            total_seconds = int(record['attendance_time'].total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            record['attendance_time'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
        if isinstance(record.get('attendance_date'), date):
            record['attendance_date'] = record['attendance_date'].isoformat()
    
        return record

    def get_monthly_attendance(self, class_subject_id, month, year):
        """Get attendance for entire month"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    a.attendance_date,
                    COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present_count,
                    COUNT(DISTINCT a.student_id) as total_students
                FROM attendance a
                WHERE a.class_subject_id = %s 
                    AND MONTH(a.attendance_date) = %s 
                    AND YEAR(a.attendance_date) = %s
                GROUP BY a.attendance_date
                ORDER BY a.attendance_date
            """
            cursor.execute(query, (class_subject_id, month, year))
            records = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return records
            
        except Exception as e:
            print(f"Error getting monthly attendance: {e}")
            raise