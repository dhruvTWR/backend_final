"""
Class Subject Model - Handles subject-to-class mapping operations
Maps subjects to specific Year-Branch-Section combinations
"""

from database.db import Database
from datetime import datetime

class ClassSubject:
    def __init__(self):
        self.db = Database()
    
    def assign_subject_to_class(self, subject_id, branch_id, year, section, semester, academic_year):
        """
        Assign a subject to a specific class (Admin only)
        
        Args:
            subject_id: ID of the subject to assign
            branch_id: ID of the branch
            year: Year (1-4)
            section: Section (A, B, C, etc.)
            semester: Semester (1-8)
            academic_year: Academic year (e.g., "2024-25")
        
        Returns:
            class_subject_id: ID of the created mapping
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            year=int(year)
            semester=int(semester)
            
            # Validate year
            if not (1 <= year <= 4):
                raise ValueError("Year must be between 1 and 4")
            
            # Validate semester
            if not (1 <= semester <= 8):
                raise ValueError("Semester must be between 1 and 8")
            
            # Check if mapping already exists
            cursor.execute("""
                SELECT id, is_active FROM class_subjects 
                WHERE subject_id = %s AND branch_id = %s AND year = %s 
                AND section = %s AND semester = %s AND academic_year = %s
            """, (subject_id, branch_id, year, section, semester, academic_year))
            
            existing = cursor.fetchone()
            
            if existing:
                if existing[1]:  # is_active = True
                    cursor.close()
                    conn.close()
                    print("⚠️  This subject is already assigned to this class")
                    return existing[0]
                else:
                    # Reactivate the existing mapping
                    cursor.execute("""
                        UPDATE class_subjects SET is_active = TRUE 
                        WHERE id = %s
                    """, (existing[0],))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    print("✅ Subject assignment reactivated")
                    return existing[0]
            
            # Insert new mapping
            query = """
                INSERT INTO class_subjects 
                (subject_id, branch_id, year, section, semester, academic_year, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            """
            cursor.execute(query, (subject_id, branch_id, year, section, semester, academic_year))
            
            class_subject_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Subject assigned to class successfully (ID: {class_subject_id})")
            return class_subject_id
            
        except Exception as e:
            print(f"❌ Error assigning subject to class: {e}")
            raise
        
    def get_class_subject_by_id(self, class_subject_id):
        """
        Get complete class subject info including branch, year, section
        This is CRITICAL for face recognition
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    cs.id,
                    cs.subject_id,
                    cs.branch_id,
                    cs.year,
                    cs.section,
                    cs.semester,
                    cs.academic_year,
                    cs.is_active,
                    s.subject_code,
                    s.subject_name,
                    b.branch_code,
                    b.branch_name
                FROM class_subjects cs
                JOIN subjects s ON cs.subject_id = s.id
                JOIN branches b ON cs.branch_id = b.id
                WHERE cs.id = %s
            """, (class_subject_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                print(f"Found class subject: {result}")
            else:
                print(f"No class subject found with ID: {class_subject_id}")
            
            return result
            
        except Exception as e:
            print(f"Error getting class subject: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    
    def get_subjects_for_class(self, branch_id, year, section, academic_year, active_only=True):
        """
        Get all subjects for a specific class (Used by Teacher) 
        
        Args:
            branch_id: Branch ID
            year: Year (1-4)
            section: Section
            academic_year: Academic year (optional, defaults to current)
            active_only: Get only active subjects
        
        Returns:
            List of subjects with class_subject mapping info
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # If academic year not provided, use current year
            if not academic_year:
                current_month = datetime.now().month
                current_year = datetime.now().year
                if current_month >= 7:  # July onwards = new academic year
                    academic_year = f"{current_year}-{str(current_year + 1)[2:]}"
                else:
                    academic_year = f"{current_year - 1}-{str(current_year)[2:]}"
            
            query = """
                SELECT 
                    cs.id as class_subject_id,
                    cs.subject_id,
                    cs.semester,
                    cs.academic_year,
                    s.subject_code,
                    s.subject_name,
                    b.branch_code,
                    b.branch_name
                FROM class_subjects cs
                INNER JOIN subjects s ON cs.subject_id = s.id
                INNER JOIN branches b ON cs.branch_id = b.id
                WHERE cs.branch_id = %s 
                AND cs.year = %s 
                AND cs.section = %s 
                AND cs.academic_year = %s
            """
            
            params = [branch_id, year, section, academic_year]
            
            query += " ORDER BY s.subject_code"
            
            cursor.execute(query, params)
            subjects = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return subjects
            
        except Exception as e:
            print(f"❌ Error getting subjects for class: {e}")
            raise
    
    def get_all_mappings(self, academic_year=None, branch_id=None, active_only=True):
        """
        Get all class-subject mappings with filters
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    cs.id,
                    cs.subject_id,  -- ADD THIS LINE
                    cs.year,
                    cs.section,
                    cs.semester,
                    cs.academic_year,
                    cs.is_active,
                    cs.branch_id,
                    s.subject_code,
                    s.subject_name,
                    b.branch_code,
                    b.branch_name,
                    cs.created_at
                FROM class_subjects cs
                INNER JOIN subjects s ON cs.subject_id = s.id
                INNER JOIN branches b ON cs.branch_id = b.id
                WHERE 1=1
            """
            
            params = []
            
            if academic_year:
                query += " AND cs.academic_year = %s"
                params.append(academic_year)
            
            if branch_id:
                query += " AND cs.branch_id = %s"
                params.append(branch_id)
            
            if active_only:
                query += " AND cs.is_active = TRUE"
            
            query += " ORDER BY b.branch_code, cs.year, cs.section, s.subject_code"
            
            cursor.execute(query, params)
            mappings = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return mappings
            
        except Exception as e:
            print(f"❌ Error getting all mappings: {e}")
            raise
        
    def update_class_subject(self, class_subject_id, semester=None, academic_year=None):
        """
        Update class-subject mapping details
        
        Args:
            class_subject_id: ID of the mapping to update
            semester: New semester (optional)
            academic_year: New academic year (optional)
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if semester is not None:
                if not (1 <= semester <= 8):
                    raise ValueError("Semester must be between 1 and 8")
                updates.append("semester = %s")
                params.append(semester)
            
            if academic_year:
                updates.append("academic_year = %s")
                params.append(academic_year)
            
            if not updates:
                print("❌ Nothing to update")
                return
            
            params.append(class_subject_id)
            query = f"UPDATE class_subjects SET {', '.join(updates)} WHERE id = %s"
            
            cursor.execute(query, tuple(params))
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Class subject mapping updated (ID: {class_subject_id})")
            
        except Exception as e:
            print(f"❌ Error updating class subject: {e}")
            raise
    
   
    def delete_class_subject(self, class_subject_id):
        """
        Permanently delete a class-subject mapping
        WARNING: This will cascade delete attendance records!
        Use deactivate_class_subject() instead unless you're sure
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get details before deleting
            cursor.execute("""
                SELECT cs.id, s.subject_name, b.branch_code, cs.year, cs.section
                FROM class_subjects cs
                INNER JOIN subjects s ON cs.subject_id = s.id
                INNER JOIN branches b ON cs.branch_id = b.id
                WHERE cs.id = %s
            """, (class_subject_id,))
            
            result = cursor.fetchone()
            
            if not result:
                print("❌ Class subject mapping not found")
                cursor.close()
                conn.close()
                return
            
            _, subject_name, branch_code, year, section = result
            
            # Delete the mapping
            query = "DELETE FROM class_subjects WHERE id = %s"
            cursor.execute(query, (class_subject_id,))
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Deleted: {subject_name} for {year}-{branch_code}-{section}")
            
        except Exception as e:
            print(f"❌ Error deleting class subject: {e}")
            raise
    
  
    
    def check_subject_assigned(self, subject_id, branch_id, year, section, semester, academic_year):
        """Check if a subject is already assigned to a class"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT COUNT(*) FROM class_subjects 
                WHERE subject_id = %s AND branch_id = %s AND year = %s 
                AND section = %s AND semester = %s AND academic_year = %s
                AND is_active = TRUE
            """
            cursor.execute(query, (subject_id, branch_id, year, section, semester, academic_year))
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return count > 0
            
        except Exception as e:
            print(f"❌ Error checking subject assignment: {e}")
            raise
    
   
    
    
    def bulk_assign_subjects(self, subject_ids, branch_id, year, section, semester, academic_year):
        """
        Assign multiple subjects to a class at once
        Useful for setting up a new semester/section
        
        Args:
            subject_ids: List of subject IDs to assign
            branch_id, year, section, semester, academic_year: Class details
        
        Returns:
            Number of subjects successfully assigned
        """
        try:
            success_count = 0
            for subject_id in subject_ids:
                try:
                    self.assign_subject_to_class(
                        subject_id, branch_id, year, section, semester, academic_year
                    )
                    success_count += 1
                except Exception as e:
                    print(f"⚠️  Failed to assign subject {subject_id}: {e}")
                    continue
            
            print(f"\n✅ Successfully assigned {success_count}/{len(subject_ids)} subjects")
            return success_count
            
        except Exception as e:
            print(f"❌ Error in bulk assignment: {e}")
            raise




