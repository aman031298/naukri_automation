#!/usr/bin/env python3
"""
Debug runner - helps identify login issues
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.browser.browser_manager import BrowserManager
from src.config.settings import Config
import time

def debug_login():
    """Test login step by step"""
    print("=" * 60)
    print("🐛 Debug Mode - Testing Login")
    print("=" * 60)
    
    browser = BrowserManager(headless=False)
    if not browser.start():
        print("❌ Browser failed to start")
        return
    
    page = browser.page
    
    try:
        # Go to Naukri
        print("\n1. Navigating to Naukri...")
        page.goto("https://www.naukri.com/")
        time.sleep(3)
        page.screenshot(path="debug_1_homepage.png")
        print("   ✅ Screenshot: debug_1_homepage.png")
        
        # Click login
        print("\n2. Looking for login button...")
        login_btn = page.locator("a:has-text('Login')").first
        if login_btn.count():
            login_btn.click()
            print("   ✅ Clicked login button")
        else:
            print("   ⚠️ Login button not found, trying direct login...")
            page.goto("https://www.naukri.com/nlogin/login")
        
        time.sleep(3)
        page.screenshot(path="debug_2_login_page.png")
        print("   ✅ Screenshot: debug_2_login_page.png")
        
        # Find username field
        print(f"\n3. Looking for username field...")
        username_fields = [
            "input#usernameField",
            "input[name='username']",
            "input[type='text']"
        ]
        
        username_found = False
        for selector in username_fields:
            field = page.locator(selector).first
            if field.count() and field.is_visible():
                print(f"   ✅ Found username field with: {selector}")
                field.fill(Config.NAUKRI_EMAIL)
                username_found = True
                break
        
        if not username_found:
            print("   ❌ Could not find username field")
            page.screenshot(path="debug_error.png")
            browser.close()
            return
        
        # Find password field
        print(f"\n4. Looking for password field...")
        password_fields = [
            "input#passwordField",
            "input[name='password']",
            "input[type='password']"
        ]
        
        password_found = False
        for selector in password_fields:
            field = page.locator(selector).first
            if field.count() and field.is_visible():
                print(f"   ✅ Found password field with: {selector}")
                field.fill(Config.NAUKRI_PASSWORD)
                password_found = True
                break
        
        if not password_found:
            print("   ❌ Could not find password field")
            browser.close()
            return
        
        # Click submit
        print("\n5. Submitting login form...")
        submit_btn = page.locator("button[type='submit']").first
        if submit_btn.count():
            submit_btn.click()
            print("   ✅ Clicked submit")
        else:
            print("   ⚠️ Submit button not found, pressing Enter...")
            page.keyboard.press("Enter")
        
        time.sleep(5)
        page.screenshot(path="debug_3_after_login.png")
        print("   ✅ Screenshot: debug_3_after_login.png")
        
        # Check if login succeeded - FIXED: Use page.text_content() correctly
        print("\n6. Checking login status...")
        
        # Method 1: Check URL
        current_url = page.url
        print(f"   Current URL: {current_url}")
        
        # Method 2: Look for welcome message
        welcome_text = page.locator("text='Welcome'").first
        if welcome_text.count():
            print("   ✅ Found 'Welcome' text")
        else:
            print("   ⚠️ No 'Welcome' text found")
        
        # Method 3: Look for profile/user menu
        user_menu = page.locator(".userMenu, .profile-icon, .user-name, .my-profile").first
        if user_menu.count() and user_menu.is_visible():
            print("   ✅ Found user menu - Login successful!")
        else:
            print("   ⚠️ User menu not found")
        
        # Method 4: Check for error messages
        error_selectors = [
            ".error",
            ".alert",
            ".error-message",
            "text='Invalid'",
            "text='incorrect'"
        ]
        
        error_found = False
        for selector in error_selectors:
            error_elem = page.locator(selector).first
            if error_elem.count() and error_elem.is_visible():
                error_text = error_elem.text_content()
                print(f"   ❌ Found error: {error_text}")
                error_found = True
        
        if not error_found and not user_menu.count():
            # Check page text for common login indicators
            page_text = page.content()  # Get full HTML
            if "dashboard" in page_text.lower() or "profile" in page_text.lower():
                print("   ✅ Login successful (found dashboard/profile in page)")
            else:
                print("   ⚠️ Login status unclear. Check screenshots.")
        
        print("\n📸 Screenshots saved:")
        print("   - debug_1_homepage.png")
        print("   - debug_2_login_page.png")
        print("   - debug_3_after_login.png")
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="debug_error.png")
    
    browser.close()

if __name__ == "__main__":
    debug_login()