"""
Base Applier Class - Common functionality for all job portals
"""
import logging
from typing import List, Dict, Any
from datetime import datetime

from src.browser.browser_manager import BrowserManager

logger = logging.getLogger(__name__)

class BaseApplier:
    """Base class with common applier functionality"""
    
    def __init__(self, browser: BrowserManager):
        self.browser = browser
        self.page = browser.page
        
        # Statistics tracking
        self.applied_jobs = []
        self.skipped_jobs = []
        self.failed_jobs = []
        self.jobs_found = []
        self.total_applied = 0
        self.max_applications = 20
        
        # Common selectors - to be overridden by child classes
        self.selectors = {}
    
    def human_delay(self, min_sec: float = 0.5, max_sec: float = 2.0):
        """Human-like delay"""
        self.browser.human_delay(min_sec, max_sec)
    
    # Disabled: debug screenshots were cluttering the project root with a
    # PNG per step of every run. No-op so existing call sites don't need to
    # change.
    def take_screenshot(self, name: str):
        """Screenshot capture is disabled"""
        return False
    
    def _extract_text(self, element, selectors: List[str]) -> str:
        """Extract text from element using multiple selectors"""
        for selector in selectors:
            try:
                elem = element.locator(selector).first
                if elem.count():
                    text = elem.text_content().strip()
                    if text:
                        return text
            except:
                continue
        return "Unknown"
    
    def is_excluded(self, title: str, exclude_keywords: List[str]) -> bool:
        """Check if job should be excluded based on keywords"""
        for keyword in exclude_keywords:
            if keyword.lower() in title.lower():
                return True
        return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate automation report"""
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