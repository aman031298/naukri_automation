#!/usr/bin/env python3
"""
Main entry point for Naukri automation
"""
import sys
from src.browser.browser_manager import BrowserManager
from src.automation.naukri_applier import NaukriApplier
from src.utils.logger import setup_logger
from src.utils.report_generator import ReportGenerator
from src.config.settings import Config
from colorama import init, Fore, Style

init(autoreset=True)

def main():
    """Main execution function"""
    logger = setup_logger()
    
    print(Fore.CYAN + "=" * 60)
    print(Fore.CYAN + Style.BRIGHT + "🤖 Naukri.com Job Application Automation")
    print(Fore.CYAN + "=" * 60)
    
    try:
        browser = BrowserManager(headless=Config.HEADLESS)
        
        if not browser.start():
            logger.error("Failed to start browser")
            return 1
        
        applier = NaukriApplier(browser)
        report = applier.run()
        
        report_gen = ReportGenerator()
        report_files = report_gen.generate_all(report)
        
        print("\n" + Fore.GREEN + "=" * 60)
        print(Fore.GREEN + Style.BRIGHT + "✅ Automation Complete!")
        print(Fore.GREEN + "=" * 60)
        print(Fore.YELLOW + f"📊 Total Jobs Found: {report['summary']['total_found']}")
        print(Fore.GREEN + f"✅ Applied: {report['summary']['applied']}")
        print(Fore.YELLOW + f"⏭️  Skipped: {report['summary']['skipped']}")
        print(Fore.RED + f"❌ Failed: {report['summary']['failed']}")
        print(Fore.CYAN + f"📁 Reports saved to: {report_files}")
        print(Fore.GREEN + "=" * 60)
        
        browser.close()
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n⚠️  User interrupted")
        if 'browser' in locals():
            browser.close()
    except Exception as e:
        logger.error(f"Automation failed: {str(e)}")
        print(Fore.RED + f"❌ Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())