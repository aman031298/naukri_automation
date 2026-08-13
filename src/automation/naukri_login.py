"""
Naukri.com Login Component
"""
import logging
from typing import List

from src.automation.base_applier import BaseApplier
from src.config.settings import Config

logger = logging.getLogger(__name__)

class NaukriLogin(BaseApplier):
    """Handles Naukri.com login functionality"""
    
    def __init__(self, browser):
        super().__init__(browser)
        
        # Login specific selectors
        self.login_selectors = {
            'login_btn': "a:has-text('Login'), .loginButton, .login-link, button:has-text('Login')",
            'username': "input#usernameField, input[name='username'], input[type='text'][placeholder*='Email']",
            'password': "input#passwordField, input[name='password'], input[type='password']",
            'submit_btn': "button[type='submit'], button:has-text('Login'), button:has-text('Sign in')",
        }
    
    def login(self) -> bool:
        """Login to Naukri.com with multiple selector fallbacks"""
        try:
            logger.info("🔐 Logging into Naukri.com...")
            
            # Navigate to Naukri
            self.page.goto("https://www.naukri.com/", wait_until="domcontentloaded")
            self.human_delay(3, 5)
            
            # Take screenshot for debugging
            self.take_screenshot("login_page_1")
            
            # Click login button
            if not self._click_login_button():
                logger.warning("Could not find login button, trying direct login page...")
                self.page.goto("https://www.naukri.com/nlogin/login", wait_until="domcontentloaded")
                self.human_delay(2, 3)
            
            self.take_screenshot("login_page_2")
            
            # Fill username
            if not self._fill_username():
                logger.error("❌ Username field not found")
                self.take_screenshot("login_error")
                return False
            
            # Fill password
            if not self._fill_password():
                logger.error("❌ Password field not found")
                self.take_screenshot("login_error")
                return False
            
            # Submit login
            if not self._submit_login():
                logger.error("❌ Submit failed")
                return False
            
            # Verify login
            return self._verify_login()
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            self.take_screenshot("login_exception")
            return False
    
    def _click_login_button(self) -> bool:
        """Click the login button"""
        login_selectors = [
            "a:has-text('Login')",
            ".loginButton",
            ".login-link",
            "button:has-text('Login')",
            "a[href*='login']",
            ".header-login"
        ]
        
        for selector in login_selectors:
            try:
                login_btn = self.page.locator(selector).first
                if login_btn.count():
                    login_btn.click()
                    self.human_delay(2, 3)
                    logger.info(f"✅ Clicked login using: {selector}")
                    return True
            except:
                continue
        return False
    
    def _fill_username(self) -> bool:
        """Fill username with multiple selector fallbacks"""
        username_selectors = [
            "input#usernameField",
            "input[name='username']",
            "input[type='text'][placeholder*='Email']",
            "input[type='text'][placeholder*='Username']",
            "input[placeholder*='email']",
            "input[placeholder*='Username']",
            "input[class*='username']"
        ]
        
        for selector in username_selectors:
            try:
                username_field = self.page.locator(selector).first
                if username_field.count() and username_field.is_visible():
                    username_field.fill(Config.NAUKRI_EMAIL)
                    self.human_delay(1, 2)
                    logger.info(f"✅ Filled username using: {selector}")
                    return True
            except:
                continue
        
        # Fallback: Try to find any visible text input
        all_inputs = self.page.locator("input[type='text'], input:not([type])").all()
        for inp in all_inputs[:3]:
            if inp.is_visible():
                placeholder = inp.get_attribute("placeholder") or ""
                if "email" in placeholder.lower() or "username" in placeholder.lower() or "user" in placeholder.lower():
                    inp.fill(Config.NAUKRI_EMAIL)
                    logger.info("✅ Filled username using fallback")
                    return True
        
        return False
    
    def _fill_password(self) -> bool:
        """Fill password with multiple selector fallbacks"""
        password_selectors = [
            "input#passwordField",
            "input[name='password']",
            "input[type='password']",
            "input[placeholder*='password']",
            "input[class*='password']"
        ]
        
        for selector in password_selectors:
            try:
                password_field = self.page.locator(selector).first
                if password_field.count() and password_field.is_visible():
                    password_field.fill(Config.NAUKRI_PASSWORD)
                    self.human_delay(1, 2)
                    logger.info(f"✅ Filled password using: {selector}")
                    return True
            except:
                continue
        return False
    
    def _submit_login(self) -> bool:
        """Submit login form"""
        submit_selectors = [
            "button[type='submit']",
            "button:has-text('Login')",
            "button:has-text('Sign in')",
            "input[type='submit']",
            ".login-btn",
            ".submit-btn"
        ]
        
        for selector in submit_selectors:
            try:
                submit_btn = self.page.locator(selector).first
                if submit_btn.count() and submit_btn.is_visible():
                    submit_btn.click()
                    self.human_delay(3, 5)
                    logger.info(f"✅ Clicked submit using: {selector}")
                    return True
            except:
                continue
        
        # Fallback: Press Enter
        logger.info("Pressing Enter to submit...")
        self.page.keyboard.press("Enter")
        self.human_delay(3, 5)
        return True
    
    def _verify_login(self) -> bool:
        """Verify if login was successful"""
        self.take_screenshot("login_after")
        
        # Check page content
        page_content = self.page.content().lower()
        if "welcome" in page_content or "dashboard" in page_content or "profile" in page_content:
            logger.info("✅ Login successful!")
            return True
        
        # Check for user menu
        user_menu = self.page.locator(".userMenu, .profile-icon, .user-name, .my-profile").first
        if user_menu.count() and user_menu.is_visible():
            logger.info("✅ Login successful (user menu found)!")
            return True
        
        # Check for error messages
        error_elem = self.page.locator(".error, .alert, .error-message").first
        if error_elem.count() and error_elem.is_visible():
            error_text = error_elem.text_content()
            logger.error(f"❌ Login error: {error_text}")
            return False
        
        logger.warning("⚠️ Login may have failed - check screenshot")
        return False