#!/usr/bin/env python3
"""
Cleanup script for removing old reports and logs
"""
import os
from pathlib import Path
from datetime import datetime, timedelta
import shutil

def cleanup_old_files(days=30):
    """Delete files older than specified days"""
    cutoff = datetime.now() - timedelta(days=days)
    
    # Clean reports
    report_dirs = ["reports/daily", "reports/weekly"]
    for dir_path in report_dirs:
        path = Path(dir_path)
        if path.exists():
            for file in path.glob("*"):
                if file.is_file():
                    file_time = datetime.fromtimestamp(file.stat().st_mtime)
                    if file_time < cutoff:
                        file.unlink()
                        print(f"🗑️ Deleted: {file}")
    
    # Clean logs
    log_dir = Path("logs")
    if log_dir.exists():
        for file in log_dir.glob("*.log"):
            file_time = datetime.fromtimestamp(file.stat().st_mtime)
            if file_time < cutoff:
                file.unlink()
                print(f"🗑️ Deleted: {file}")
    
    print("✅ Cleanup completed!")

if __name__ == "__main__":
    cleanup_old_files()