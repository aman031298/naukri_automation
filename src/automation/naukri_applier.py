"""
Naukri.com Applier - Main orchestrator
Combines login, search, and apply components
"""
import logging
from typing import List, Dict, Any

from src.automation.base_applier import BaseApplier
from src.automation.naukri_login import NaukriLogin
from src.automation.naukri_search import NaukriSearch
from src.automation.naukri_apply import NaukriApply
from src.config.settings import Config

logger = logging.getLogger(__name__)

class NaukriApplier(BaseApplier):
    """
    Main Naukri Applier class that orchestrates:
    1. Login
    2. Search
    3. Apply
    """
    
    def __init__(self, browser):
        super().__init__(browser)
        
        # Initialize components
        self.login_component = NaukriLogin(browser)
        self.search_component = NaukriSearch(browser)
        self.apply_component = NaukriApply(browser)
        
        # Set max applications from config
        self.max_applications = Config.MAX_APPLICATIONS
    
    def run(self) -> Dict[str, Any]:
        """Run complete automation workflow"""
        logger.info("=" * 60)
        logger.info("🚀 Starting Naukri.com Job Automation")
        logger.info("=" * 60)
        
        # Step 1: Login
        if not self.login_component.login():
            logger.error("❌ Login failed - stopping automation")
            return self.generate_report()
        
        # Step 2: Search jobs
        jobs = self.search_component.search_jobs()
        if not jobs:
            logger.warning("No jobs found")
            return self.generate_report()
        
        # Step 3: Apply to jobs
        result = self.apply_component.process_jobs(jobs)
        
        # Merge statistics from apply component
        self.applied_jobs = self.apply_component.applied_jobs
        self.skipped_jobs = self.apply_component.skipped_jobs
        self.failed_jobs = self.apply_component.failed_jobs
        self.total_applied = self.apply_component.total_applied
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Override to include all statistics"""
        report = {
            "platform": "Naukri.com",
            "timestamp": datetime.now().isoformat(),
            "duration": "N/A",
            "summary": {
                "total_found": len(self.jobs_found),
                "applied": len(self.applied_jobs),
                "skipped": len(self.skipped_jobs),
                "failed": len(self.failed_jobs),
            },
            "applied_jobs": self.applied_jobs,
            "skipped_jobs": self.skipped_jobs,
            "failed_jobs": self.failed_jobs
        }
        
        logger.info("=" * 60)
        logger.info("📊 Report Summary")
        logger.info(f"   Total Found: {report['summary']['total_found']}")
        logger.info(f"   ✅ Applied: {report['summary']['applied']}")
        logger.info(f"   ⏭️ Skipped: {report['summary']['skipped']}")
        logger.info(f"   ❌ Failed: {report['summary']['failed']}")
        logger.info("=" * 60)
        
        return report