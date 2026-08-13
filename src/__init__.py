"""
Naukri.com Job Application Automation System
"""
__version__ = "1.0.0"
__author__ = "Your Name"

from src.browser.browser_manager import BrowserManager
from src.automation.naukri_applier import NaukriApplier
from src.utils.logger import setup_logger

__all__ = [
    'BrowserManager',
    'NaukriApplier',
    'setup_logger'
]