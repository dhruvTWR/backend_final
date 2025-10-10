"""
Log Model - System audit logging and monitoring
"""

from datetime import datetime, timedelta
import json
from database.db import Database

class Log:
    def __init__(self):
        self.db = Database()
    
    def add_log(self, log_type, user_type, user_id, action, message, details=None, ip_address=None):
        """
        Add system log entry
        
        Args:
            log_type: 'info', 'warning', 'error', 'attendance', 'admin'
            user_type: 'admin', 'teacher', 'system'
            user_id: User ID (can be None for system logs)
            action: Action performed
            message: Log message
            details: Additional details (dict)
            ip_address: IP address of user
        """
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            details_json = json.dumps(details) if details else None
            
            query = """
                INSERT INTO logs 
                (log_type, user_type, user_id, action, message, details, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (log_type, user_type, user_id, action, message, details_json, ip_address))
            
            log_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            return log_id
            
        except Exception as e:
            print(f"Error adding log: {e}")
            raise
    
    def get_logs(self, log_type=None, user_type=None, user_id=None, 
                 start_date=None, end_date=None, limit=100):
        """Get logs with filters"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM logs WHERE 1=1"
            params = []
            
            if log_type:
                query += " AND log_type = %s"
                params.append(log_type)
            
            if user_type:
                query += " AND user_type = %s"
                params.append(user_type)
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            
            if start_date:
                query += " AND created_at >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND created_at <= %s"
                params.append(end_date)
            
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            logs = cursor.fetchall()
            
            # Parse JSON details
            for log in logs:
                if log['details']:
                    try:
                        log['details'] = json.loads(log['details'])
                    except:
                        pass
            
            cursor.close()
            conn.close()
            
            return logs
            
        except Exception as e:
            print(f"Error getting logs: {e}")
            raise
    
    def get_logs_by_user(self, user_type, user_id, limit=50):
        """Get logs for specific user"""
        return self.get_logs(user_type=user_type, user_id=user_id, limit=limit)
    
    def get_recent_logs(self, limit=100):
        """Get most recent logs"""
        return self.get_logs(limit=limit)
    
    def get_error_logs(self, hours=24, limit=100):
        """Get error logs from last N hours"""
        start_date = datetime.now() - timedelta(hours=hours)
        return self.get_logs(log_type='error', start_date=start_date, limit=limit)
    
    def get_attendance_logs(self, date=None, limit=100):
        """Get attendance-related logs"""
        if date:
            start_date = datetime.combine(date, datetime.min.time())
            end_date = datetime.combine(date, datetime.max.time())
            return self.get_logs(log_type='attendance', start_date=start_date, end_date=end_date, limit=limit)
        else:
            return self.get_logs(log_type='attendance', limit=limit)
    
    def get_admin_actions(self, limit=50):
        """Get admin action logs"""
        return self.get_logs(log_type='admin', limit=limit)
    
    def get_logs_by_action(self, action, limit=50):
        """Get logs by specific action"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT * FROM logs 
                WHERE action = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            cursor.execute(query, (action, limit))
            logs = cursor.fetchall()
            
            for log in logs:
                if log['details']:
                    try:
                        log['details'] = json.loads(log['details'])
                    except:
                        pass
            
            cursor.close()
            conn.close()
            
            return logs
            
        except Exception as e:
            print(f"Error getting logs by action: {e}")
            raise
    
    def get_log_statistics(self, days=7):
        """Get log statistics for dashboard"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            start_date = datetime.now() - timedelta(days=days)
            
            # Count by type
            query = """
                SELECT 
                    log_type,
                    COUNT(*) as count
                FROM logs
                WHERE created_at >= %s
                GROUP BY log_type
            """
            cursor.execute(query, (start_date,))
            type_stats = cursor.fetchall()
            
            # Count by user type
            query = """
                SELECT 
                    user_type,
                    COUNT(*) as count
                FROM logs
                WHERE created_at >= %s
                GROUP BY user_type
            """
            cursor.execute(query, (start_date,))
            user_stats = cursor.fetchall()
            
            # Daily counts
            query = """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM logs
                WHERE created_at >= %s
                GROUP BY DATE(created_at)
                ORDER BY date
            """
            cursor.execute(query, (start_date,))
            daily_stats = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                'by_type': type_stats,
                'by_user': user_stats,
                'daily': daily_stats
            }
            
        except Exception as e:
            print(f"Error getting log statistics: {e}")
            raise
    
    def cleanup_old_logs(self, days=90):
        """Delete logs older than N days"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            query = "DELETE FROM logs WHERE created_at < %s"
            cursor.execute(query, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Cleaned up {deleted_count} old logs")
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up logs: {e}")
            raise
    
    def search_logs(self, search_term, limit=50):
        """Search logs by message or action"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT * FROM logs 
                WHERE message LIKE %s OR action LIKE %s
                ORDER BY created_at DESC 
                LIMIT %s
            """
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, limit))
            logs = cursor.fetchall()
            
            for log in logs:
                if log['details']:
                    try:
                        log['details'] = json.loads(log['details'])
                    except:
                        pass
            
            cursor.close()
            conn.close()
            
            return logs
            
        except Exception as e:
            print(f"Error searching logs: {e}")
            raise
    
    def export_logs_csv(self, filename, start_date=None, end_date=None):
        """Export logs to CSV file"""
        try:
            import csv
            
            logs = self.get_logs(start_date=start_date, end_date=end_date, limit=10000)
            
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = ['id', 'log_type', 'user_type', 'user_id', 'action', 
                            'message', 'ip_address', 'created_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for log in logs:
                    row = {k: log[k] for k in fieldnames if k in log}
                    writer.writerow(row)
            
            print(f"Exported {len(logs)} logs to {filename}")
            return len(logs)
            
        except Exception as e:
            print(f"Error exporting logs: {e}")
            raise
    
    # Convenience logging methods
    def log_info(self, user_type, user_id, action, message, details=None, ip_address=None):
        """Log info message"""
        return self.add_log('info', user_type, user_id, action, message, details, ip_address)
    
    def log_warning(self, user_type, user_id, action, message, details=None, ip_address=None):
        """Log warning message"""
        return self.add_log('warning', user_type, user_id, action, message, details, ip_address)
    
    def log_error(self, user_type, user_id, action, message, details=None, ip_address=None):
        """Log error message"""
        return self.add_log('error', user_type, user_id, action, message, details, ip_address)
    
    def log_attendance(self, user_type, user_id, action, message, details=None, ip_address=None):
        """Log attendance action"""
        return self.add_log('attendance', user_type, user_id, action, message, details, ip_address)
    
    def log_admin_action(self, user_id, action, message, details=None, ip_address=None):
        """Log admin action"""
        return self.add_log('admin', 'admin', user_id, action, message, details, ip_address)