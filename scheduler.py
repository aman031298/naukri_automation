#!/usr/bin/env python3
"""
Scheduler for automated daily job applications
"""
import schedule
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_automation():
    """Run the automation script"""
    logger.info("🚀 Running scheduled automation...")
    try:
        result = subprocess.run(
            [sys.executable, "run.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        logger.info(f"Automation completed: {result.returncode}")
        if result.stdout:
            logger.info(result.stdout[-500:])  # Last 500 chars
        if result.stderr:
            logger.error(result.stderr[-500:])
    except Exception as e:
        logger.error(f"Automation failed: {str(e)}")

def main():
    """Main scheduler"""
    # Schedule daily at 9:00 AM
    schedule.every().day.at("09:00").do(run_automation)
    schedule.every().day.at("18:00").do(run_automation)  # Evening run
    
    logger.info("=" * 60)
    logger.info("🕐 Job Automation Scheduler")
    logger.info("=" * 60)
    logger.info("Schedule:")
    logger.info("   Daily at 09:00 AM")
    logger.info("   Daily at 06:00 PM")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    main()