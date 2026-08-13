"""
Notification system for automation events
"""
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class Notifier:
    """Handles notifications for automation events"""
    
    def __init__(self):
        self.enabled = os.getenv("NOTIFICATIONS_ENABLED", "true").lower() == "true"
    
    def notify(self, title, message, level="info"):
        """Send notification"""
        if not self.enabled:
            return
        
        try:
            # Desktop notification (Windows)
            if os.name == 'nt':
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    timeout=5
                )
                logger.info(f"📢 Notification sent: {title}")
            
            # Console notification with colors
            self._console_notify(title, message, level)
            
        except Exception as e:
            logger.warning(f"Notification failed: {str(e)}")
    
    def _console_notify(self, title, message, level):
        """Print to console with colors"""
        from colorama import Fore, Style
        
        colors = {
            'info': Fore.CYAN,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED
        }
        
        color = colors.get(level, Fore.WHITE)
        print(f"\n{color}🔔 {title}")
        print(f"   {message}{Style.RESET_ALL}")