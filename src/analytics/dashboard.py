"""
Analytics dashboard for job applications
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class AnalyticsDashboard:
    """Provides analytics on job applications"""
    
    def __init__(self, db_path="db/jobs_history.db"):
        self.db_path = Path(db_path)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all dashboard data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total applications
            cursor.execute("SELECT COUNT(*) FROM jobs")
            total = cursor.fetchone()[0]
            
            # Today's applications
            today = datetime.now().date().isoformat()
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE date(applied_at) = ?", (today,))
            today_count = cursor.fetchone()[0]
            
            # Weekly applications
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied_at >= ?", (week_ago,))
            weekly = cursor.fetchone()[0]
            
            # Monthly applications
            month_ago = (datetime.now() - timedelta(days=30)).isoformat()
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE applied_at >= ?", (month_ago,))
            monthly = cursor.fetchone()[0]
            
            # Status breakdown
            cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
            status_counts = dict(cursor.fetchall())
            
            # Top companies
            cursor.execute("""
                SELECT company, COUNT(*) as count 
                FROM jobs 
                WHERE company != 'N/A' 
                GROUP BY company 
                ORDER BY count DESC 
                LIMIT 10
            """)
            top_companies = cursor.fetchall()
            
            # Top locations
            cursor.execute("""
                SELECT location, COUNT(*) as count 
                FROM jobs 
                WHERE location != 'N/A' 
                GROUP BY location 
                ORDER BY count DESC 
                LIMIT 10
            """)
            top_locations = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_applications': total,
                'today': today_count,
                'weekly': weekly,
                'monthly': monthly,
                'status_breakdown': status_counts,
                'top_companies': top_companies,
                'top_locations': top_locations,
                'success_rate': self._calculate_success_rate(status_counts)
            }
        except Exception as e:
            logger.error(f"Dashboard data failed: {str(e)}")
            return {}
    
    def _calculate_success_rate(self, status_counts: Dict) -> float:
        """Calculate success rate"""
        total = sum(status_counts.values())
        applied = status_counts.get('applied', 0)
        return round((applied / total * 100) if total > 0 else 0, 2)