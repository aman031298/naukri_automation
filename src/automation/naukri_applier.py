"""
Naukri.com Applier - Main orchestrator
Combines login, search, and apply components
"""
import logging
from datetime import datetime
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
        
        # Step 2: Search jobs — first batch comes from whichever method
        # search_jobs() succeeds with (recommended feed, then keyword
        # search fallbacks).
        jobs = self.search_component.search_jobs()
        self.jobs_found = jobs
        if not jobs:
            logger.warning("No jobs found")
            return self.generate_report()

        seen_links = {j.get('link') for j in jobs if j.get('link')}

        # Step 3: Apply, then keep fetching additional search-result pages
        # and applying again until max_applications *confirmed* applies
        # are reached. Capped at max_search_batches so a run doesn't loop
        # indefinitely if Naukri genuinely has no more matching jobs left
        # to page through.
        self.apply_component.process_jobs(jobs)

        max_search_batches = 8
        next_page = 2  # page 1 was already covered by the initial search
        batches_fetched = 0
        while (
            self.apply_component.total_applied < self.max_applications
            and batches_fetched < max_search_batches
        ):
            more_jobs = self.search_component.search_more_jobs(next_page, exclude_links=seen_links)
            batches_fetched += 1
            next_page += 1

            if not more_jobs:
                logger.info("No more candidate jobs available — stopping search")
                break

            seen_links.update(j.get('link') for j in more_jobs if j.get('link'))
            self.jobs_found.extend(more_jobs)
            self.apply_component.process_jobs(more_jobs)

        if self.apply_component.total_applied < self.max_applications:
            logger.warning(
                f"⚠️ Stopped with {self.apply_component.total_applied}/{self.max_applications} "
                f"confirmed applications — ran out of matching jobs"
            )

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