"""
Naukri.com Application Component
"""
import logging
from datetime import datetime
from typing import Dict, List

from src.automation.base_applier import BaseApplier
from src.automation.form_filler import FormFiller

logger = logging.getLogger(__name__)

class NaukriApply(BaseApplier):
    """Handles Naukri.com job application functionality"""
    
    def __init__(self, browser):
        super().__init__(browser)
        self.form_filler = FormFiller(browser)
        
        # Application specific selectors
        self.apply_selectors = {
            'apply_btn': "button:has-text('Apply'), .apply-button, .apply-btn, button[class*='apply']",
            'view_btn': "button:has-text('View & Apply'), .view-apply-btn",
        }
    
    def apply_to_job(self, job: Dict) -> bool:
        """Apply to a single job"""
        try:
            logger.info(f"📝 Applying: {job['title']} at {job['company']}")
            
            # Navigate to job
            if not self._navigate_to_job(job):
                return False
            
            # Check if already applied
            if self._check_already_applied():
                logger.info(f"⏭️ Already applied to {job['title']}")
                job['status'] = 'already_applied'
                self.skipped_jobs.append(job)
                return False
            
            # Find and click apply button
            if not self._click_apply_button(job):
                return False
            
            # Fill and submit form
            if self.form_filler.fill_and_submit():
                job['status'] = 'applied'
                job['applied_at'] = datetime.now().isoformat()
                self.applied_jobs.append(job)
                self.total_applied += 1
                logger.info(f"✅ Applied: {job['title']}")
                return True
            else:
                job['status'] = 'form_failed'
                self.failed_jobs.append(job)
                return False
            
        except Exception as e:
            logger.error(f"Application failed: {str(e)}")
            job['status'] = 'error'
            job['error'] = str(e)
            self.failed_jobs.append(job)
            self.take_screenshot("apply_error")
            return False
    
    def _navigate_to_job(self, job: Dict) -> bool:
        """Navigate to job URL"""
        if job.get('link'):
            self.page.goto(job['link'], wait_until="domcontentloaded")
            self.human_delay(2, 4)
            return True
        else:
            logger.warning("No link available for job")
            job['status'] = 'no_link'
            self.skipped_jobs.append(job)
            return False
    
    def _check_already_applied(self) -> bool:
        """Check if already applied to this job"""
        page_content = self.page.content().lower()
        return "already applied" in page_content or "application submitted" in page_content
    
    def _click_apply_button(self, job: Dict) -> bool:
        """Find and click the apply button"""
        apply_btn = self.page.locator(self.apply_selectors['apply_btn']).first
        if not apply_btn.count():
            apply_btn = self.page.locator(self.apply_selectors['view_btn']).first
        
        if not apply_btn.count():
            logger.warning(f"No apply button for {job['title']}")
            job['status'] = 'no_apply_button'
            self.skipped_jobs.append(job)
            return False
        
        # Check if external site
        btn_text = apply_btn.text_content().lower() if apply_btn.count() else ""
        if "company site" in btn_text or "external" in btn_text:
            logger.info(f"⏭️ External application: {job['title']}")
            job['status'] = 'external_site'
            self.skipped_jobs.append(job)
            return False
        
        # Click apply
        apply_btn.click()
        self.human_delay(2, 4)
        return True
    
    def process_jobs(self, jobs: List[Dict]) -> Dict:
        """Process multiple jobs"""
        applied_count = 0
        
        for job in jobs:
            if applied_count >= self.max_applications:
                logger.info(f"📊 Reached daily limit: {self.max_applications}")
                break
            
            self.apply_to_job(job)
            applied_count += 1
            self.human_delay(3, 6)
        
        return self.generate_report()