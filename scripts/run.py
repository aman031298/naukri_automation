#!/usr/bin/env python3
"""
Run script for Naukri automation
"""
import sys
import subprocess
from pathlib import Path

def run_automation():
    """Run the automation script"""
    main_script = Path(__file__).parent.parent / "src" / "main.py"
    subprocess.run([sys.executable, str(main_script)])

if __name__ == "__main__":
    run_automation()