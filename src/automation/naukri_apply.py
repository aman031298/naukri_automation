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
        
        # Application specific selectors.
        # Naukri renders two distinct buttons that both contain the word
        # "Apply": #apply-button (native, one-click) and
        # #company-site-button ("Apply on company site", redirects off
        # Naukri). Matching by id keeps these separate — a text-only
        # selector like "button:has-text('Apply')" matches whichever one
        # is visible first regardless of which flow it actually is.
        self.apply_selectors = {
            'native_apply_btn': "#apply-button, button.apply-button",
            'company_site_btn': "#company-site-button, button.company-site-button",
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
            click_result = self._click_apply_button(job)
            if not click_result:
                return False

            if click_result == 'company_site':
                # External application: Naukri redirects to the employer's
                # own careers page, which the bot can't fill out generically.
                # Skip without clicking through — the goal is applying to
                # jobs Naukri can submit natively, not collecting redirects.
                job['status'] = 'external_site'
                self.skipped_jobs.append(job)
                logger.info(f"⏭️ Skipped company-site apply for: {job['title']}")
                return False

            # Fill and submit form (native Naukri apply flow)
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
    
    def _click_apply_button(self, job: Dict):
        """Find and click the apply button.

        Returns 'native' if the one-click Naukri apply flow was used,
        'company_site' if it redirected to the employer's own site,
        or False if no usable button was found.
        """
        native_btn = self.page.locator(self.apply_selectors['native_apply_btn']).first
        if native_btn.count() and native_btn.is_visible():
            native_btn.click()
            self.human_delay(2, 4)
            return 'native'

        company_btn = self.page.locator(self.apply_selectors['company_site_btn']).first
        if company_btn.count() and company_btn.is_visible():
            # Don't click it — this button redirects off Naukri to the
            # employer's own site, which has no generic form the bot can
            # fill. Report it as company_site without interacting further.
            logger.info(f"⏭️ Company-site apply button for: {job['title']} (not clicking)")
            return 'company_site'

        view_btn = self.page.locator(self.apply_selectors['view_btn']).first
        if view_btn.count() and view_btn.is_visible():
            view_btn.click()
            self.human_delay(2, 4)
            return 'native'

        logger.warning(f"No apply button for {job['title']}")
        job['status'] = 'no_apply_button'
        self.skipped_jobs.append(job)
        return False
    
    def process_jobs(self, jobs: List[Dict]) -> Dict:
        """Process a batch of candidate jobs, applying to each in turn.

        Stops early once max_applications *confirmed* applies have been
        reached — self.total_applied only increments on a verified
        success (see apply_to_job/form_filler), so a batch that's mostly
        company-site skips or failed applies won't falsely count toward
        the limit and cut the run short.
        """
        for job in jobs:
            if self.total_applied >= self.max_applications:
                logger.info(f"📊 Reached target of {self.max_applications} confirmed applications")
                break

            self.apply_to_job(job)
            self.human_delay(3, 6)

        return self.generate_report()