
from datetime import datetime, timedelta
from database.db import Database

class UnrecognizedFace:
    def __init__(self):
        self.db = Database()
    
    def add_unrecognized(self, class_subject_id, image_path, original_upload, attendance_date):
        """Add unrecognized face record"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
        
            cursor.execute("""
                INSERT INTO unrecognized_faces 
                (class_subject_id, image_path, original_upload, attendance_date, detected_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (class_subject_id, image_path, original_upload, attendance_date))
        
            unrec_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
        
            return unrec_id
        
        except Exception as e:
            print(f"Error adding unrecognized face: {e}")
            return None
    def add_unrecognized(self, class_subject_id, image_path, original_upload, attendance_date):
        """
        Add unrecognized face record
        
        Args:
            class_subject_id: Which class/subject this face was detected in
            image_path: Path to saved cropped face image
            original_upload: Path to original uploaded classroom photo
            attendance_date: Date of attendance session
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO unrecognized_faces 
                (class_subject_id, image_path, original_upload, attendance_date)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (class_subject_id, image_path, original_upload, attendance_date))
            
            unrecognized_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Unrecognized face saved: {image_path}")
            return unrecognized_id
            
        except Exception as e:
            print(f"Error adding unrecognized face: {e}")
            raise
    
    def get_unrecognized_faces(self, class_subject_id=None, resolved=False, 
                               start_date=None, end_date=None, limit=100):
        """
        Get unrecognized faces with filters
        
        Args:
            class_subject_id: Filter by specific class/subject
            resolved: Show only resolved (True) or unresolved (False/None)
            start_date: Filter from date
            end_date: Filter to date
            limit: Max results
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    uf.*,
                    s.subject_name,
                    s.subject_code,
                    b.branch_name,
                    cs.year,
                    cs.section,
                    st.name as resolved_student_name,
                    st.roll_number as resolved_roll_number
                FROM unrecognized_faces uf
                JOIN class_subjects cs ON uf.class_subject_id = cs.id
                JOIN subjects s ON cs.subject_id = s.id
                JOIN branches b ON cs.branch_id = b.id
                LEFT JOIN students st ON uf.resolved_student_id = st.id
                WHERE 1=1
            """
            params = []
            
            if class_subject_id:
                query += " AND uf.class_subject_id = %s"
                params.append(class_subject_id)
            
            if resolved is not None:
                query += " AND uf.resolved = %s"
                params.append(resolved)
            
            if start_date:
                query += " AND uf.attendance_date >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND uf.attendance_date <= %s"
                params.append(end_date)
            
            query += " ORDER BY uf.detected_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            faces = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return faces
            
        except Exception as e:
            print(f"Error getting unrecognized faces: {e}")
            raise
    
    def get_unresolved_count(self, class_subject_id=None):
        """Get count of unresolved faces"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM unrecognized_faces WHERE resolved = FALSE"
            params = []
            
            if class_subject_id:
                query += " AND class_subject_id = %s"
                params.append(class_subject_id)
            
            cursor.execute(query, tuple(params) if params else None)
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return count
            
        except Exception as e:
            print(f"Error getting unresolved count: {e}")
            raise
    
    def resolve_face(self, unrecognized_id, student_id, resolved_by):
        """
        Mark unrecognized face as resolved and link to student
        
        Args:
            unrecognized_id: ID of unrecognized face record
            student_id: Student this face belongs to
            resolved_by: Teacher/admin ID who resolved it
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE unrecognized_faces 
                SET resolved = TRUE,
                    resolved_student_id = %s,
                    resolved_by = %s,
                    resolved_at = NOW()
                WHERE id = %s
            """
            cursor.execute(query, (student_id, resolved_by, unrecognized_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Unrecognized face {unrecognized_id} resolved for student {student_id}")
            
        except Exception as e:
            print(f"Error resolving face: {e}")
            raise
    
    def bulk_resolve_faces(self, unrecognized_ids, student_id, resolved_by):
        """Resolve multiple faces at once (same student)"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE unrecognized_faces 
                SET resolved = TRUE,
                    resolved_student_id = %s,
                    resolved_by = %s,
                    resolved_at = NOW()
                WHERE id IN ({})
            """.format(','.join(['%s'] * len(unrecognized_ids)))
            
            cursor.execute(query, [student_id, resolved_by] + unrecognized_ids)
            
            resolved_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Resolved {resolved_count} faces for student {student_id}")
            return resolved_count
            
        except Exception as e:
            print(f"Error bulk resolving faces: {e}")
            raise
    
    def delete_unrecognized(self, unrecognized_id):
        """Delete unrecognized face record and file"""
        try:
            import os
            
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get image path before deleting
            query = "SELECT image_path FROM unrecognized_faces WHERE id = %s"
            cursor.execute(query, (unrecognized_id,))
            result = cursor.fetchone()
            
            if result and result['image_path']:
                # Delete image file
                if os.path.exists(result['image_path']):
                    os.remove(result['image_path'])
            
            # Delete record
            delete_query = "DELETE FROM unrecognized_faces WHERE id = %s"
            cursor.execute(delete_query, (unrecognized_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Deleted unrecognized face {unrecognized_id}")
            
        except Exception as e:
            print(f"Error deleting unrecognized face: {e}")
            raise
    
    def get_unrecognized_by_date(self, attendance_date, class_subject_id=None):
        """Get all unrecognized faces for a specific date"""
        return self.get_unrecognized_faces(
            class_subject_id=class_subject_id,
            start_date=attendance_date,
            end_date=attendance_date,
            resolved=False
        )
    
    def get_recent_unresolved(self, days=7, limit=50):
        """Get recent unresolved faces"""
        start_date = datetime.now().date() - timedelta(days=days)
        return self.get_unrecognized_faces(
            resolved=False,
            start_date=start_date,
            limit=limit
        )
    
  
        
    def cleanup_old_resolved(self, days=90):
        """Delete old resolved faces to save space"""
        try:
            import os
            
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cutoff_date = datetime.now().date() - timedelta(days=days)
            
            # Get image paths before deleting
            query = """
                SELECT image_path FROM unrecognized_faces 
                WHERE resolved = TRUE AND attendance_date < %s
            """
            cursor.execute(query, (cutoff_date,))
            records = cursor.fetchall()
            
            # Delete files
            deleted_files = 0
            for record in records:
                if record['image_path'] and os.path.exists(record['image_path']):
                    os.remove(record['image_path'])
                    deleted_files += 1
            
            # Delete records
            delete_query = """
                DELETE FROM unrecognized_faces 
                WHERE resolved = TRUE AND attendance_date < %s
            """
            cursor.execute(delete_query, (cutoff_date,))
            deleted_records = cursor.rowcount
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Cleaned up {deleted_records} old resolved faces ({deleted_files} files)")
            return deleted_records
            
        except Exception as e:
            print(f"Error cleaning up old faces: {e}")
            raise
        