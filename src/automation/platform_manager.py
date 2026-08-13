"""
Multi-platform support for different job portals
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PlatformManager:
    """Manages different job platforms"""
    
    def __init__(self):
        self.platforms = {
            'naukri': {
                'name': 'Naukri.com',
                'enabled': True,
                'priority': 1
            },
            'linkedin': {
                'name': 'LinkedIn',
                'enabled': False,
                'priority': 2
            },
            'indeed': {
                'name': 'Indeed',
                'enabled': False,
                'priority': 3
            },
            'monster': {
                'name': 'Monster',
                'enabled': False,
                'priority': 4
            }
        }
    
    def get_enabled_platforms(self) -> list:
        """Get list of enabled platforms"""
        return [p for p in self.platforms.values() if p['enabled']]
    
    def add_platform(self, name: str, config: Dict):
        """Add a new platform"""
        self.platforms[name] = config
        logger.info(f"✅ Added platform: {name}")