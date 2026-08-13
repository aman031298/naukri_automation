"""
Database handler for tracking job applications
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DatabaseHandler:
    """Handles database operations for job tracking"""
    
    def __init__(self, db_path="data/jobs_history.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    link TEXT,
                    status TEXT,
                    applied_at DATETIME,
                    platform TEXT,
                    search_keywords TEXT,
                    error_message TEXT
                )
            """)
            
            # Logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS automation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    action TEXT,
                    details TEXT,
                    status TEXT
                )
            """)
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at DATETIME
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Database initialized")
            
        except Exception as e:
            logger.error(f"Database init failed: {str(e)}")
    
    def save_job(self, job_data):
        """Save job application record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO jobs (
                    title, company, location, link, status, 
                    applied_at, platform, search_keywords, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_data.get('title', ''),
                job_data.get('company', ''),
                job_data.get('location', ''),
                job_data.get('link', ''),
                job_data.get('status', ''),
                job_data.get('applied_at', datetime.now().isoformat()),
                job_data.get('platform', 'Naukri.com'),
                job_data.get('search_keywords', ''),
                job_data.get('error_message', '')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Save job failed: {str(e)}")
            return False
    
    def get_stats(self):
        """Get statistics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM jobs")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
            status_counts = dict(cursor.fetchall())
            
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied_at >= date('now', '-7 days')")
            weekly = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total': total,
                'status_counts': status_counts,
                'weekly': weekly
            }
            
        except Exception as e:
            logger.error(f"Get stats failed: {str(e)}")
            return {}