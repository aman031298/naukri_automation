#!/usr/bin/env python3
"""
Runner script for Naukri automation with better error handling
"""
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def check_playwright():
    """Check if playwright is installed and working"""
    try:
        import playwright
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            browser.close()
        print("✅ Playwright is working")
        return True
    except ImportError as e:
        print(f"❌ Playwright not installed: {e}")
        print("\nPlease install playwright with:")
        print("    pip install playwright")
        print("    playwright install chromium")
        return False
    except Exception as e:
        print(f"❌ Playwright error: {e}")
        print("\nPlease install playwright browsers with:")
        print("    playwright install chromium")
        return False

def check_env_file():
    """Check if .env file exists"""
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️ .env file not found")
        print("Creating from .env.example...")
        if (project_root / ".env.example").exists():
            import shutil
            shutil.copy(project_root / ".env.example", env_file)
            print("✅ Created .env file. Please update with your credentials.")
            return False
        return True
    return True

def check_requirements():
    """Check if all requirements are installed"""
    required = ['playwright', 'pandas', 'dotenv', 'jinja2', 'yaml']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("\nPlease install them with:")
        print("    pip install -r requirements.txt")
        return False
    return True

def main():
    """Main entry point"""
    print("="*60)
    print("🚀 Naukri Job Automation")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check environment
    print("\n📋 Checking environment...")
    
    if not check_requirements():
        return 1
    
    if not check_playwright():
        return 1
    
    if not check_env_file():
        print("\nPlease update .env file with your credentials and try again.")
        return 1
    
    print("\n✅ All checks passed!")
    
    try:
        from src.automation.naukri_applier import NaukriApplier
        from src.browser.browser_manager import BrowserManager
        from src.utils.logger import setup_logger
        from src.utils.report_generator import ReportGenerator
        from src.config.settings import Config
        
        logger = setup_logger()
        
        # Initialize browser
        logger.info("Starting browser...")
        browser = BrowserManager(headless=Config.HEADLESS)
        
        if not browser.start():
            logger.error("Failed to start browser")
            return 1
        
        # Run automation
        applier = NaukriApplier(browser)
        report = applier.run()
        
        # Generate reports
        report_gen = ReportGenerator()
        report_files = report_gen.generate_all(report)
        
        # Print summary
        print("\n" + "="*60)
        print("✅ Automation Complete!")
        print("="*60)
        print(f"📊 Total Found: {report['summary']['total_found']}")
        print(f"✅ Applied: {report['summary']['applied']}")
        print(f"⏭️ Skipped: {report['summary']['skipped']}")
        print(f"❌ Failed: {report['summary']['failed']}")
        print(f"📁 Reports: {report_files}")
        print("="*60)
        
        # Close browser
        browser.close()
        logger.info("Browser closed")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ User interrupted")
        return 1
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())