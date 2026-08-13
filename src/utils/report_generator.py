"""
Report Generator - Creates beautiful reports from automation data
"""
import json
import csv
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates reports in multiple formats"""
    
    def __init__(self, report_dir="reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
        (self.report_dir / "daily").mkdir(exist_ok=True)
        (self.report_dir / "weekly").mkdir(exist_ok=True)
    
    def generate_all(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all report formats
        
        Args:
            report_data: Dictionary containing report data
            
        Returns:
            Dictionary with paths to generated reports
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Ensure all required keys exist
            report_data = self._ensure_report_structure(report_data)
            
            reports = {
                "json": self._generate_json(report_data, timestamp),
                "csv": self._generate_csv(report_data, timestamp),
                "html": self._generate_html(report_data, timestamp),
                "txt": self._generate_text(report_data, timestamp),
            }
            
            logger.info(f"✅ Reports generated: {len(reports)} formats")
            return reports
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return {}
    
    def _ensure_report_structure(self, data: Dict) -> Dict:
        """Ensure report has all required fields"""
        default = {
            "platform": "Naukri.com",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_found": 0,
                "applied": 0,
                "skipped": 0,
                "failed": 0,
                "total_processed": 0
            },
            "applied_jobs": [],
            "skipped_jobs": [],
            "failed_jobs": [],
            "search_keywords": [],
            "search_location": "",
            "duration_seconds": 0
        }
        
        # Merge with defaults
        result = default.copy()
        for key, value in data.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    result[key].update(value)
                else:
                    result[key] = value
            else:
                result[key] = value
        
        # Calculate totals
        result["summary"]["total_processed"] = (
            result["summary"]["applied"] + 
            result["summary"]["skipped"] + 
            result["summary"]["failed"]
        )
        
        return result
    
    def _generate_json(self, data: Dict, timestamp: str) -> str:
        """Generate JSON report"""
        try:
            filename = self.report_dir / "daily" / f"report_{timestamp}.json"
            with open(filename, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            logger.info(f"✅ JSON report: {filename}")
            return str(filename)
        except Exception as e:
            logger.error(f"JSON generation failed: {str(e)}")
            return ""
    
    def _generate_csv(self, data: Dict, timestamp: str) -> str:
        """Generate CSV report with all jobs"""
        try:
            filename = self.report_dir / "daily" / f"report_{timestamp}.csv"
            
            # Combine all jobs
            all_jobs = []
            
            for job in data.get('applied_jobs', []):
                job_copy = job.copy()
                job_copy['status'] = 'applied'
                job_copy['applied_at'] = job.get('applied_at', datetime.now().isoformat())
                all_jobs.append(job_copy)
            
            for job in data.get('skipped_jobs', []):
                job_copy = job.copy()
                job_copy['status'] = 'skipped'
                job_copy['applied_at'] = 'N/A'
                all_jobs.append(job_copy)
            
            for job in data.get('failed_jobs', []):
                job_copy = job.copy()
                job_copy['status'] = 'failed'
                job_copy['applied_at'] = 'N/A'
                all_jobs.append(job_copy)
            
            # Write CSV
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                if all_jobs:
                    fieldnames = ['title', 'company', 'location', 'status', 'applied_at']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(all_jobs)
                else:
                    # Write summary only
                    f.write(f"Platform,{data.get('platform', 'Naukri.com')}\n")
                    f.write(f"Timestamp,{data.get('timestamp', datetime.now().isoformat())}\n")
                    f.write(f"Total Found,{data['summary']['total_found']}\n")
                    f.write(f"Applied,{data['summary']['applied']}\n")
                    f.write(f"Skipped,{data['summary']['skipped']}\n")
                    f.write(f"Failed,{data['summary']['failed']}\n")
            
            logger.info(f"✅ CSV report: {filename}")
            return str(filename)
            
        except Exception as e:
            logger.error(f"CSV generation failed: {str(e)}")
            return ""
    
    def _generate_html(self, data: Dict, timestamp: str) -> str:
        """Generate HTML report with styling"""
        try:
            filename = self.report_dir / "daily" / f"report_{timestamp}.html"
            
            # Prepare data
            platform = data.get('platform', 'Naukri.com')
            report_time = data.get('timestamp', datetime.now().isoformat())
            summary = data['summary']
            applied_jobs = data.get('applied_jobs', [])
            skipped_jobs = data.get('skipped_jobs', [])
            failed_jobs = data.get('failed_jobs', [])
            keywords = data.get('search_keywords', [])
            location = data.get('search_location', 'N/A')
            
            # Generate HTML
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Job Application Report - {platform}</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                        background: #f0f2f5;
                        padding: 20px;
                        color: #333;
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 12px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        padding: 30px;
                    }}
                    h1 {{
                        color: #1a237e;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 15px;
                        margin-bottom: 25px;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }}
                    .header-info {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 15px;
                        background: #f8f9fa;
                        padding: 15px 20px;
                        border-radius: 8px;
                        margin-bottom: 25px;
                    }}
                    .header-info .label {{
                        font-size: 12px;
                        color: #6c757d;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }}
                    .header-info .value {{
                        font-size: 14px;
                        font-weight: 600;
                        color: #2c3e50;
                    }}
                    .stats-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                        gap: 15px;
                        margin-bottom: 30px;
                    }}
                    .stat-card {{
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        color: white;
                        transition: transform 0.2s;
                    }}
                    .stat-card:hover {{
                        transform: translateY(-3px);
                    }}
                    .stat-card .number {{
                        font-size: 32px;
                        font-weight: bold;
                        display: block;
                    }}
                    .stat-card .label {{
                        font-size: 13px;
                        opacity: 0.9;
                        margin-top: 5px;
                        display: block;
                    }}
                    .stat-card.total {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
                    .stat-card.applied {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
                    .stat-card.skipped {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
                    .stat-card.failed {{ background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }}
                    
                    .section-title {{
                        margin: 30px 0 15px 0;
                        color: #1a237e;
                        font-size: 20px;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }}
                    .section-title .count {{
                        background: #e9ecef;
                        padding: 2px 10px;
                        border-radius: 20px;
                        font-size: 14px;
                        color: #495057;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 10px;
                        font-size: 14px;
                    }}
                    th, td {{
                        padding: 12px 15px;
                        text-align: left;
                        border-bottom: 1px solid #e9ecef;
                    }}
                    th {{
                        background: #f8f9fa;
                        font-weight: 600;
                        color: #495057;
                        position: sticky;
                        top: 0;
                    }}
                    tr:hover {{
                        background: #f8f9fa;
                    }}
                    .status-badge {{
                        padding: 4px 12px;
                        border-radius: 20px;
                        font-size: 11px;
                        font-weight: 600;
                        display: inline-block;
                    }}
                    .status-badge.applied {{ background: #d4edda; color: #155724; }}
                    .status-badge.skipped {{ background: #fff3cd; color: #856404; }}
                    .status-badge.failed {{ background: #f8d7da; color: #721c24; }}
                    .status-badge.found {{ background: #cce5ff; color: #004085; }}
                    
                    .no-data {{
                        text-align: center;
                        padding: 40px;
                        color: #6c757d;
                        background: #f8f9fa;
                        border-radius: 8px;
                        margin: 10px 0;
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #e9ecef;
                        text-align: center;
                        color: #6c757d;
                        font-size: 12px;
                    }}
                    @media (max-width: 600px) {{
                        .container {{ padding: 15px; }}
                        .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
                        table {{ font-size: 12px; }}
                        th, td {{ padding: 8px 10px; }}
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📊 Job Application Report</h1>
                    
                    <div class="header-info">
                        <div>
                            <div class="label">Platform</div>
                            <div class="value">{platform}</div>
                        </div>
                        <div>
                            <div class="label">Generated</div>
                            <div class="value">{report_time}</div>
                        </div>
                        <div>
                            <div class="label">Keywords</div>
                            <div class="value">{', '.join(keywords) if keywords else 'N/A'}</div>
                        </div>
                        <div>
                            <div class="label">Location</div>
                            <div class="value">{location}</div>
                        </div>
                    </div>
                    
                    <div class="stats-grid">
                        <div class="stat-card total">
                            <span class="number">{summary.get('total_found', 0)}</span>
                            <span class="label">📊 Total Found</span>
                        </div>
                        <div class="stat-card applied">
                            <span class="number">{summary.get('applied', 0)}</span>
                            <span class="label">✅ Applied</span>
                        </div>
                        <div class="stat-card skipped">
                            <span class="number">{summary.get('skipped', 0)}</span>
                            <span class="label">⏭️ Skipped</span>
                        </div>
                        <div class="stat-card failed">
                            <span class="number">{summary.get('failed', 0)}</span>
                            <span class="label">❌ Failed</span>
                        </div>
                    </div>
                    
                    {self._generate_table_section('✅ Applied Jobs', applied_jobs, 'applied')}
                    {self._generate_table_section('⏭️ Skipped Jobs', skipped_jobs, 'skipped')}
                    {self._generate_table_section('❌ Failed Jobs', failed_jobs, 'failed')}
                    
                    <div class="footer">
                        Generated by Job Automation System v1.0.0<br>
                        Report ID: {timestamp}
                    </div>
                </div>
            </body>
            </html>
            """
            
            with open(filename, "w", encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"✅ HTML report: {filename}")
            return str(filename)
            
        except Exception as e:
            logger.error(f"HTML generation failed: {str(e)}")
            return ""
    
    def _generate_table_section(self, title: str, jobs: List[Dict], status: str) -> str:
        """Generate HTML table section for jobs"""
        if not jobs:
            return f"""
            <div class="section-title">{title} <span class="count">0</span></div>
            <div class="no-data">No {status} jobs to display</div>
            """
        
        rows = []
        for i, job in enumerate(jobs, 1):
            title_text = job.get('title', 'N/A')
            company = job.get('company', 'N/A')
            location = job.get('location', 'N/A')
            applied_at = job.get('applied_at', 'N/A')
            job_status = job.get('status', status)
            
            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td><strong>{title_text}</strong></td>
                <td>{company}</td>
                <td>{location}</td>
                <td>{applied_at}</td>
                <td><span class="status-badge {status}">{job_status}</span></td>
            </tr>
            """)
        
        return f"""
        <div class="section-title">{title} <span class="count">{len(jobs)}</span></div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Title</th>
                    <th>Company</th>
                    <th>Location</th>
                    <th>Applied At</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
    
    def _generate_text(self, data: Dict, timestamp: str) -> str:
        """Generate plain text report"""
        try:
            filename = self.report_dir / "daily" / f"report_{timestamp}.txt"
            
            summary = data['summary']
            
            lines = [
                "=" * 60,
                f"JOB APPLICATION REPORT - {data.get('platform', 'Naukri.com')}",
                "=" * 60,
                f"Generated: {data.get('timestamp', datetime.now().isoformat())}",
                f"Keywords: {', '.join(data.get('search_keywords', []))}",
                f"Location: {data.get('search_location', 'N/A')}",
                "",
                "SUMMARY",
                "-" * 40,
                f"Total Jobs Found: {summary.get('total_found', 0)}",
                f"Applied: {summary.get('applied', 0)}",
                f"Skipped: {summary.get('skipped', 0)}",
                f"Failed: {summary.get('failed', 0)}",
                f"Total Processed: {summary.get('total_processed', 0)}",
                "",
            ]
            
            # Add applied jobs
            if data.get('applied_jobs'):
                lines.extend([
                    "APPLIED JOBS",
                    "-" * 40,
                ])
                for i, job in enumerate(data['applied_jobs'], 1):
                    lines.append(
                        f"{i}. {job.get('title', 'N/A')} "
                        f"at {job.get('company', 'N/A')} "
                        f"- {job.get('location', 'N/A')}"
                    )
                lines.append("")
            
            # Add skipped jobs
            if data.get('skipped_jobs'):
                lines.extend([
                    "SKIPPED JOBS",
                    "-" * 40,
                ])
                for i, job in enumerate(data['skipped_jobs'], 1):
                    lines.append(
                        f"{i}. {job.get('title', 'N/A')} "
                        f"at {job.get('company', 'N/A')} "
                        f"- {job.get('location', 'N/A')}"
                    )
                lines.append("")
            
            # Add failed jobs
            if data.get('failed_jobs'):
                lines.extend([
                    "FAILED JOBS",
                    "-" * 40,
                ])
                for i, job in enumerate(data['failed_jobs'], 1):
                    lines.append(
                        f"{i}. {job.get('title', 'N/A')} "
                        f"at {job.get('company', 'N/A')} "
                        f"- {job.get('error', 'Unknown error')}"
                    )
                lines.append("")
            
            lines.append("=" * 60)
            
            with open(filename, "w", encoding='utf-8') as f:
                f.write("\n".join(lines))
            
            logger.info(f"✅ Text report: {filename}")
            return str(filename)
            
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            return ""