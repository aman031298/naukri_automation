"""
Configuration validator
"""
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigValidator:
    """Validates configuration settings"""
    
    @staticmethod
    def validate_all():
        """Validate all configuration"""
        errors = []
        warnings = []
        
        # Check .env file
        env_file = Path(".env")
        if not env_file.exists():
            errors.append(".env file not found")
        
        # Check credentials
        if not os.getenv("NAUKRI_EMAIL"):
            errors.append("NAUKRI_EMAIL not set in .env")
        
        if not os.getenv("NAUKRI_PASSWORD"):
            errors.append("NAUKRI_PASSWORD not set in .env")
        
        # Check keywords
        keywords = os.getenv("JOB_KEYWORDS", "")
        if not keywords:
            warnings.append("JOB_KEYWORDS not set, using default")
        
        # Check resume
        resume_paths = [
            "data/resume/Sachin Chakrawarti - Resume.pdf",
            "resume.pdf",
            "profiles/resume.pdf"
        ]
        resume_found = False
        for path in resume_paths:
            if Path(path).exists():
                resume_found = True
                break
        
        if not resume_found:
            warnings.append("Resume file not found in expected locations")
        
        # Print results
        if errors:
            logger.error("❌ Configuration errors:")
            for error in errors:
                logger.error(f"   - {error}")
            return False
        
        if warnings:
            logger.warning("⚠️ Configuration warnings:")
            for warning in warnings:
                logger.warning(f"   - {warning}")
        
        logger.info("✅ Configuration validated")
        return True