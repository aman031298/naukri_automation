#!/usr/bin/env python3
"""
Test report generation with sample data
"""
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from src.utils.report_generator import ReportGenerator

def test_report():
    """Test report generation with sample data"""
    print("\n" + "="*60)
    print("📊 Testing Report Generator")
    print("="*60)
    
    # Sample data
    sample_report = {
        "platform": "Naukri.com",
        "timestamp": datetime.now().isoformat(),
        "search_keywords": ["Python Developer", "Full Stack", "Data Scientist"],
        "search_location": "Bangalore",
        "summary": {
            "total_found": 25,
            "applied": 5,
            "skipped": 3,
            "failed": 2
        },
        "applied_jobs": [
            {
                "title": "Python Developer",
                "company": "Tech Corp",
                "location": "Bangalore",
                "applied_at": datetime.now().isoformat(),
                "status": "applied"
            },
            {
                "title": "Full Stack Engineer",
                "company": "Startup Inc",
                "location": "Remote",
                "applied_at": datetime.now().isoformat(),
                "status": "applied"
            }
        ],
        "skipped_jobs": [
            {
                "title": "Senior Developer",
                "company": "Big Company",
                "location": "Mumbai",
                "status": "already_applied"
            }
        ],
        "failed_jobs": [
            {
                "title": "Data Scientist",
                "company": "AI Corp",
                "location": "Pune",
                "status": "form_failed",
                "error": "Resume upload failed"
            }
        ]
    }
    
    # Generate report
    generator = ReportGenerator()
    reports = generator.generate_all(sample_report)
    
    print("\n✅ Reports generated:")
    for format_name, path in reports.items():
        if path:
            print(f"   📄 {format_name.upper()}: {path}")
    
    print("\n📁 Reports saved in: reports/daily/")
    print("="*60)

if __name__ == "__main__":
    test_report()