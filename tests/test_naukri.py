"""
Test cases for Naukri automation
"""
import unittest
from pathlib import Path

class TestNaukriAutomation(unittest.TestCase):
    """Test Naukri automation components"""
    
    def test_config_loading(self):
        """Test configuration loading"""
        from src.config.settings import Config
        self.assertIsNotNone(Config.NAUKRI_EMAIL)
    
    def test_profile_loading(self):
        """Test profile loading"""
        from src.utils.file_handler import load_user_profile
        profile = load_user_profile()
        self.assertIsInstance(profile, dict)

if __name__ == "__main__":
    unittest.main()