"""
Naukri Resume Upload Handler - Direct approach
"""
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

class ResumeUploader:
    """Handles resume upload for Naukri.com"""
    
    def __init__(self, browser):
        self.browser = browser
        self.page = browser.page
        self.resume_uploaded = False
        self.resume_skipped = False
        
        # Resume file paths
        self.resume_paths = [
            r"D:\Sachin Chakrawarti\Learn\myprojets\projects\naukri_automation\mydata\resume\Sachin Chakrawarti - Resume.pdf",
            "./data/resume/Sachin Chakrawarti - Resume.pdf",
            "./data/resume/resume.pdf",
            "./resume.pdf",
            "./resume.docx",
        ]
    
    def upload_resume(self) -> bool:
        """Main method to upload resume"""
        try:
            logger.info("📄 Attempting resume upload...")
            
            # Check if resume upload is visible
            if not self._is_upload_visible():
                logger.info("ℹ️ No resume upload required, skipping")
                self.resume_skipped = True
                return True
            
            # Find resume file
            resume_path = self._find_resume()
            if not resume_path:
                logger.warning("⚠️ Resume file not found")
                return self._click_skip()
            
            # Try direct upload
            if self._direct_upload(resume_path):
                self.resume_uploaded = True
                logger.info("✅ Resume uploaded successfully!")
                return True
            
            # Try alternative upload method
            if self._alternative_upload(resume_path):
                self.resume_uploaded = True
                logger.info("✅ Resume uploaded via alternative method!")
                return True
            
            # If all fails, skip
            logger.warning("⚠️ Upload failed, skipping...")
            return self._click_skip()
            
        except Exception as e:
            logger.error(f"Resume upload error: {str(e)}")
            return self._click_skip()
    
    def _is_upload_visible(self) -> bool:
        """Check if upload section is visible"""
        try:
            # Check for upload prompt text
            page_text = self.page.content().lower()
            upload_keywords = [
                "upload your resume",
                "upload resume",
                "please upload",
                "resume required"
            ]
            
            for keyword in upload_keywords:
                if keyword in page_text:
                    logger.info(f"✅ Found upload prompt: {keyword}")
                    return True
            
            # Check for file input
            file_input = self.page.locator("input[type='file']")
            if file_input.count():
                logger.info("✅ Found file input")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking upload visibility: {str(e)}")
            return False
    
    def _find_resume(self) -> str:
        """Find resume file"""
        for path in self.resume_paths:
            if os.path.exists(path):
                logger.info(f"✅ Found resume: {path}")
                return path
        
        # Search in data/resume
        resume_dir = Path("./data/resume")
        if resume_dir.exists():
            for ext in ['.pdf', '.docx', '.doc']:
                for file in resume_dir.glob(f"*{ext}"):
                    if file.exists():
                        logger.info(f"✅ Found resume: {file}")
                        return str(file)
        
        return None
    
    def _direct_upload(self, resume_path: str) -> bool:
        """Direct upload using file input"""
        try:
            logger.info("📤 Direct upload attempt...")
            
            # Wait a bit for the page to be ready
            self.browser.human_delay(1, 2)
            
            # Find file input
            file_input = self.page.locator("input[type='file']").first
            
            if not file_input.count():
                logger.warning("File input not found")
                return False
            
            # Check if file input is visible
            if not file_input.is_visible():
                logger.warning("File input not visible")
                return False
            
            # Upload file
            file_input.set_input_files(resume_path)
            self.browser.human_delay(2, 3)
            
            # Verify upload
            return self._verify_upload()
            
        except Exception as e:
            logger.warning(f"Direct upload failed: {str(e)}")
            return False
    
    def _alternative_upload(self, resume_path: str) -> bool:
        """Alternative upload method"""
        try:
            logger.info("📤 Alternative upload attempt...")
            
            # Try to find upload button
            upload_btn = self.page.locator(
                "button:has-text('Upload Resume'), "
                ".upload-btn, "
                ".resume-upload-btn, "
                "a:has-text('Upload')"
            ).first
            
            if upload_btn.count() and upload_btn.is_visible():
                upload_btn.click()
                self.browser.human_delay(1, 2)
                
                # Now find file input
                file_input = self.page.locator("input[type='file']").first
                if file_input.count():
                    file_input.set_input_files(resume_path)
                    self.browser.human_delay(2, 3)
                    return self._verify_upload()
            
            # Try clicking on the upload area
            upload_area = self.page.locator(".upload-area, .drop-zone, .file-upload-area").first
            if upload_area.count() and upload_area.is_visible():
                upload_area.click()
                self.browser.human_delay(1, 2)
                
                file_input = self.page.locator("input[type='file']").first
                if file_input.count():
                    file_input.set_input_files(resume_path)
                    self.browser.human_delay(2, 3)
                    return self._verify_upload()
            
            return False
            
        except Exception as e:
            logger.warning(f"Alternative upload failed: {str(e)}")
            return False
    
    def _verify_upload(self) -> bool:
        """Verify if upload was successful"""
        try:
            self.browser.human_delay(2, 3)
            
            # Check for success indicators
            success_indicators = [
                ".upload-success",
                ".file-uploaded",
                ".resume-uploaded",
                ".success-message",
                "text='Uploaded'",
                "text='Success'"
            ]
            
            for selector in success_indicators:
                elem = self.page.locator(selector).first
                if elem.count() and elem.is_visible():
                    logger.info("✅ Upload success indicator found")
                    return True
            
            # Check if file name appears
            file_name = self.page.locator(".file-name, .uploaded-file, .resume-name").first
            if file_name.count() and file_name.is_visible():
                logger.info(f"✅ File name found: {file_name.text_content()}")
                return True
            
            # Check if upload prompt disappeared
            upload_prompt = self.page.locator("text='Upload Resume'")
            if not upload_prompt.count() or not upload_prompt.is_visible():
                logger.info("✅ Upload prompt disappeared")
                return True
            
            # Check for any error messages
            error_msg = self.page.locator(".error, .alert-danger, .error-message").first
            if error_msg.count() and error_msg.is_visible():
                logger.warning(f"❌ Upload error: {error_msg.text_content()}")
                return False
            
            return False
            
        except Exception as e:
            logger.warning(f"Verification failed: {str(e)}")
            return False
    
    def _click_skip(self) -> bool:
        """Click skip/I'll do it later button"""
        try:
            logger.info("📄 Looking for skip option...")
            
            skip_selectors = [
                "button:has-text('I\\'ll do it later')",
                "button:has-text('Skip for now')",
                "button:has-text('Skip')",
                "button:has-text('Later')",
                "a:has-text('I\\'ll do it later')",
                "button:has-text('Cancel')",
                ".skip-btn",
                ".close-btn",
                ".crossIcon"
            ]
            
            for selector in skip_selectors:
                try:
                    skip_btn = self.page.locator(selector).first
                    if skip_btn.count() and skip_btn.is_visible():
                        skip_btn.click()
                        self.browser.human_delay(1, 2)
                        self.resume_skipped = True
                        logger.info("✅ Skipped resume upload")
                        return True
                except:
                    continue
            
            # Try pressing Escape
            self.page.keyboard.press("Escape")
            self.browser.human_delay(1, 2)
            self.resume_skipped = True
            logger.info("✅ Pressed Escape to skip")
            return True
            
        except Exception as e:
            logger.warning(f"Skip failed: {str(e)}")
            return False
    
    def is_resume_uploaded(self) -> bool:
        return self.resume_uploaded
    
    def is_resume_skipped(self) -> bool:
        return self.resume_skipped