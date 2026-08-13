#!/usr/bin/env python3
"""
Test individual components of the automation
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.browser.browser_manager import BrowserManager
from src.automation.naukri_login import NaukriLogin
from src.automation.naukri_search import NaukriSearch
from src.automation.naukri_apply import NaukriApply
from src.automation.naukri_applier import NaukriApplier
from src.config.settings import Config

def test_login():
    """Test login component"""
    print("\n" + "="*60)
    print("🔐 Testing Login Component")
    print("="*60)
    
    browser = BrowserManager(headless=False)
    if not browser.start():
        print("❌ Browser failed to start")
        return False
    
    login = NaukriLogin(browser)
    result = login.login()
    
    if result:
        print("✅ Login successful!")
    else:
        print("❌ Login failed")
    
    input("\nPress Enter to continue...")
    browser.close()
    return result

def test_search():
    """Test search component"""
    print("\n" + "="*60)
    print("🔍 Testing Search Component")
    print("="*60)
    
    browser = BrowserManager(headless=False)
    if not browser.start():
        print("❌ Browser failed to start")
        return False
    
    # Login first
    login = NaukriLogin(browser)
    if not login.login():
        print("❌ Login failed")
        browser.close()
        return False
    
    # Search
    search = NaukriSearch(browser)
    jobs = search.search_jobs()
    
    print(f"\n✅ Found {len(jobs)} jobs")
    for i, job in enumerate(jobs[:5]):
        print(f"   {i+1}. {job['title']} at {job['company']} - {job['location']}")
    
    input("\nPress Enter to continue...")
    browser.close()
    return True

def test_full_automation():
    """Test full automation"""
    print("\n" + "="*60)
    print("🚀 Testing Full Automation")
    print("="*60)
    
    browser = BrowserManager(headless=False)
    if not browser.start():
        print("❌ Browser failed to start")
        return False
    
    applier = NaukriApplier(browser)
    report = applier.run()
    
    print(f"\n📊 Results:")
    print(f"   Total Found: {report['summary']['total_found']}")
    print(f"   ✅ Applied: {report['summary']['applied']}")
    print(f"   ⏭️ Skipped: {report['summary']['skipped']}")
    print(f"   ❌ Failed: {report['summary']['failed']}")
    
    input("\nPress Enter to continue...")
    browser.close()
    return True

if __name__ == "__main__":
    print("="*60)
    print("🧪 Testing Naukri Automation Components")
    print("="*60)
    
    while True:
        print("\nSelect test to run:")
        print("1. Test Login Only")
        print("2. Test Search Only (requires login)")
        print("3. Test Full Automation")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ")
        
        if choice == "1":
            test_login()
        elif choice == "2":
            test_search()
        elif choice == "3":
            test_full_automation()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")