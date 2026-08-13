# 🤖 Naukri.com Job Application Automation

Automated job application system for Naukri.com using Playwright.

## ✨ Features

- ✅ **Automated Login** - Secure login with session persistence
- 🔍 **Smart Job Search** - Multiple search methods with fallbacks
- 📝 **Auto Form Filling** - Smart form detection and filling
- 📄 **Resume Upload** - Handles resume uploads intelligently
- ❓ **Question Handler** - Answers recruiter questions automatically
- 📊 **Detailed Reports** - HTML, CSV, JSON, and TXT formats
- 💾 **Database Tracking** - SQLite database for job history
- 🔔 **Notifications** - Desktop notifications for events
- ⏰ **Scheduler** - Daily automated runs
- 🛡️ **Anti-Detection** - Human-like behavior patterns

## 📁 Project Structure



naukri_automation/
├── data/ # Data storage
│ └── resume/ # Resume files
├── logs/ # Application logs
├── profiles/ # User profiles
├── reports/ # Generated reports
│ ├── daily/ # Daily reports
│ └── weekly/ # Weekly reports
├── scripts/ # Utility scripts
├── src/ # Source code
│ ├── automation/ # Automation components
│ ├── browser/ # Browser management
│ ├── config/ # Configuration
│ ├── data/ # Database handlers
│ └── utils/ # Utilities
├── tests/ # Test cases
└── venv/ # Virtual environment