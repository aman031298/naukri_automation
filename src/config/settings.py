"""
Configuration settings
"""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    """Configuration class"""
    
    # Naukri credentials
    NAUKRI_EMAIL = os.getenv("NAUKRI_EMAIL", "")
    NAUKRI_PASSWORD = os.getenv("NAUKRI_PASSWORD", "")
    
    # Job preferences
    JOB_KEYWORDS = os.getenv("JOB_KEYWORDS", "Python Developer").split(",")
    JOB_KEYWORDS = [kw.strip() for kw in JOB_KEYWORDS]
    
    JOB_LOCATION = os.getenv("JOB_LOCATION", "India").split(",")
    JOB_LOCATION = [loc.strip() for loc in JOB_LOCATION]
    
    EXCLUDE_KEYWORDS = os.getenv("EXCLUDE_KEYWORDS", "senior,lead,manager").split(",")
    EXCLUDE_KEYWORDS = [kw.strip().lower() for kw in EXCLUDE_KEYWORDS]
    
    MAX_APPLICATIONS = int(os.getenv("MAX_APPLICATIONS", 20))
    
    # Browser settings
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent.parent