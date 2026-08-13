"""
File handling utilities
"""
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_user_profile(profile_path="profiles/user_profile.yaml"):
    """Load user profile from YAML file"""
    try:
        profile_file = Path(profile_path)
        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            logger.warning(f"Profile not found: {profile_path}")
            return {}
    except Exception as e:
        logger.error(f"Failed to load profile: {str(e)}")
        return {}

def save_user_profile(data, profile_path="profiles/user_profile.yaml"):
    """Save user profile to YAML file"""
    try:
        Path(profile_path).parent.mkdir(exist_ok=True)
        with open(profile_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)
        logger.info(f"Profile saved: {profile_path}")
    except Exception as e:
        logger.error(f"Failed to save profile: {str(e)}")