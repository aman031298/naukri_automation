# 🤖 Naukri Job Automation - Project Flow

## 📋 Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Detailed Flow](#detailed-flow)
4. [Component Breakdown](#component-breakdown)
5. [Data Flow](#data-flow)
6. [Error Handling](#error-handling)
7. [Sequence Diagrams](#sequence-diagrams)
8. [Configuration Guide](#configuration-guide)

---

## 📌 Overview

This document describes the complete workflow of the Naukri Job Application Automation system. The system automates the process of:
- 🔐 Logging into Naukri.com
- 🔍 Searching for relevant jobs
- 📝 Applying to jobs automatically
- 📊 Generating detailed reports

---

## 🏗️ System Architecture


┌─────────────────────────────────────────────────────────────────┐
│ USER INTERFACE LAYER │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│ │ run.py │ │ scheduler.py│ │ test_components.py │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ APPLICATION LAYER (src/) │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ main.py (Entry Point) │ │
│ └──────────────────────────────────────────────────────────┘ │
│ │ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│ │ Automation │ │ Browser │ │ Config │ │
│ │ Layer │ │ Layer │ │ Layer │ │
│ │ │ │ │ │ │ │
│ │ • Login │ │ • Browser │ │ • Settings │ │
│ │ • Search │ │ Manager │ │ • Selectors │ │
│ │ • Apply │ │ • Anti- │ │ • Validator │ │
│ │ • Questions │ │ Detection │ │ • Sites.yaml │ │
│ │ • Resume │ │ │ │ │ │
│ └──────────────┘ └──────────────┘ └──────────────────────┘ │
│ │ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│ │ Utils │ │ Data │ │ AI Layer │ │
│ │ Layer │ │ Layer │ │ │ │
│ │ │ │ │ │ • Job Matcher │ │
│ │ • Logger │ │ • Database │ │ • Skill Extraction │ │
│ │ • Reports │ │ • File │ │ • Score Calculator │ │
│ │ • Notifier │ │ Handler │ │ │ │
│ │ • Exporter │ │ • Q&A DB │ │ │ │
│ └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ DATA STORAGE LAYER │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│ │ SQLite │ │ Reports │ │ Profiles │ │
│ │ Database │ │ (CSV/ │ │ (YAML/JSON) │ │
│ │ │ │ HTML/ │ │ │ │
│ │ • Jobs │ │ JSON) │ │ • User Profile │ │
│ │ • Runs │ │ │ │ • Application Data │ │
│ │ • Settings │ │ • Daily │ │ • Company Prefs │ │
│ │ │ │ • Weekly │ │ • Q&A Database │ │
│ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ EXTERNAL SERVICES │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Naukri.com Website │ │
│ └──────────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ Email Service (SMTP) │ │
│ └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

text

---

## 🔄 Detailed Flow

### Phase 1: Initialization & Configuration
┌─────────────────────────────────────────────────────────────────┐
│ START │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Load .env file │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Load User │ │
│ │ Profile (YAML) │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Validate │ │
│ │ Configuration │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Initialize │ │
│ │ Database │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Setup Logger │ │
│ │ & Notifications │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
└─────────────────────────────────────────────────────────────────┘

text

### Phase 2: Browser Setup
┌─────────────────────────────────────────────────────────────────┐
│ │
│ ┌──────────────────┐ │
│ │ Start Browser │ │
│ │ (Playwright) │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Apply Anti- │ │
│ │ Detection │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Create Context │ │
│ │ & Page │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Add Init Script │ │
│ │ (Hide Automation)│ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
└─────────────────────────────────────────────────────────────────┘

text

### Phase 3: Login Process
┌─────────────────────────────────────────────────────────────────┐
│ │
│ ┌──────────────────┐ │
│ │ Navigate to │ │
│ │ Naukri.com │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Click Login │ │
│ │ Button │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Enter Email │ │
│ │ (from .env) │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Enter Password │ │
│ │ (from .env) │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Click Submit │ │
│ │ Button │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Verify Login │ │
│ │ Success │ │
│ └──────────────────┘ │
│ │ │
│ ┌────┴────┐ │
│ │ │ │
│ Yes No │
│ │ │ │
│ ▼ ▼ │
│ ┌────────┐ ┌────────┐ │
│ │ Proceed │ │ Retry │ │
│ └────────┘ └────────┘ │
│ │
└─────────────────────────────────────────────────────────────────┘

text

### Phase 4: Job Search Process
┌─────────────────────────────────────────────────────────────────┐
│ │
│ ┌──────────────────┐ │
│ │ Navigate to │ │
│ │ Home Page │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Find Search │ │
│ │ Input Field │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Enter Keywords │ │
│ │ (from config) │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Enter Location │ │
│ │ (from config) │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Click Search │ │
│ │ Button │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Wait for │ │
│ │ Results Load │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Extract Job │ │
│ │ Listings │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Filter Jobs │ │
│ │ (Exclude │ │
│ │ keywords) │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Store Job │ │
│ │ Data │ │
│ └──────────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────┘

text

### Phase 5: Application Process
┌─────────────────────────────────────────────────────────────────┐
│ │
│ ┌──────────────────┐ │
│ │ For Each Job │ │
│ │ (Limited by │ │
│ │ MAX_APPLICATIONS)│ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Navigate to │ │
│ │ Job URL │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Check Already │ │
│ │ Applied │ │
│ └──────────────────┘ │
│ │ │
│ ┌────┴────┐ │
│ │ │ │
│ Yes No │
│ │ │ │
│ ▼ ▼ │
│ ┌────────┐ ┌────────┐ │
│ │ Skip │ │ Click │ │
│ │ Job │ │ Apply │ │
│ └────────┘ └────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Handle Resume │ │
│ │ Upload │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Handle │ │
│ │ Questions │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Fill Form │ │
│ │ Fields │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Submit │ │
│ │ Application │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Verify │ │
│ │ Submission │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Save to │ │
│ │ Database │ │
│ └──────────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────┘

text

### Phase 6: Question Handling Process


┌─────────────────────────────────────────────────────────────────┐
│ │
│ ┌──────────────────┐ │
│ │ Detect │ │
│ │ Questions │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ For Each │ │
│ │ Question │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Detect Type │ │
│ │ (MCQ/Text/ │ │
│ │ Number/YesNo) │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Search in │ │
│ │ Q&A Database │ │
│ └──────────────────┘ │
│ │ │
│ ┌────┴────┐ │
│ │ │ │
│ Found Not Found │
│ │ │ │
│ ▼ ▼ │
│ ┌────────┐ ┌────────┐ │
│ │ Get │ │ Get │ │
│ │ Answer │ │ from │ │
│ │ from DB│ │ Profile│ │
│ └────────┘ └────────┘ │
│ │ │ │
│ └────┬────┘ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Fill Answer │ │
│ │ Based on Type │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Mark Answered │ │
│ │ & Track │ │
│ └──────────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────┘

text

### Phase 7: Report Generation
┌─────────────────────────────────────────────────────────────────┐
│ │
│ ┌──────────────────┐ │
│ │ Collect All │ │
│ │ Application │ │
│ │ Data │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Generate │ │
│ │ HTML Report │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Generate │ │
│ │ CSV Report │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Generate │ │
│ │ JSON Report │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Generate │ │
│ │ TXT Report │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Save to │ │
│ │ Reports Folder │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Send Email │ │
│ │ (if configured) │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Send Desktop │ │
│ │ Notification │ │
│ └──────────────────┘ │
│ │
└─────────────────────────────────────────────────────────────────┘

text

---

## 🔧 Component Breakdown

### 1. **Browser Manager (`src/browser/browser_manager.py`)**

**Purpose**: Manage browser lifecycle and anti-detection

**Key Features**:
- Launch browser with anti-detection flags
- Create isolated contexts
- Human-like delays
- Screenshot capability
- Element waiting utilities

**Flow**:
Initialize → Start Browser → Create Context → Create Page → Apply Anti-Detection → Ready

text

### 2. **Login Component (`src/automation/naukri_login.py`)**

**Purpose**: Handle Naukri.com login

**Key Features**:
- Multiple selector fallbacks
- Error handling with screenshots
- Login verification
- Session persistence

**Flow**:
Navigate → Click Login → Enter Credentials → Submit → Verify → Return Status

text

### 3. **Search Component (`src/automation/naukri_search.py`)**

**Purpose**: Search and extract job listings

**Key Features**:
- Multiple search methods (homepage, direct URL)
- JavaScript-based filling
- Smart selector detection
- Job extraction with fallbacks

**Flow**:
Navigate → Fill Keywords → Fill Location → Search → Wait → Extract Jobs → Filter → Return

text

### 4. **Apply Component (`src/automation/naukri_apply.py`)**

**Purpose**: Apply to individual jobs

**Key Features**:
- Check already applied
- Handle resume upload
- Handle recruiter questions
- Form filling automation
- Submission verification

**Flow**:
Navigate → Check Status → Click Apply → Handle Resume → Handle Questions → Fill Form → Submit → Verify

text

### 5. **Question Handler (`src/automation/question_handler.py`)**

**Purpose**: Answer recruiter questions

**Key Features**:
- 1000+ Q&A database
- Multiple question types (MCQ, Text, Number, Yes/No, Dropdown)
- Profile-based answers
- Smart matching
- Skip functionality

**Flow**:
Detect Questions → Identify Type → Find Answer → Fill Answer → Track → Next

text

### 6. **Resume Uploader (`src/automation/resume_uploader.py`)**

**Purpose**: Handle resume upload

**Key Features**:
- Multiple file locations
- Smart detection
- Multiple upload methods
- Verification
- Skip fallback

**Flow**:
Detect Upload → Find Resume → Choose Method → Upload → Verify → Success/Fallback

text

### 7. **Report Generator (`src/utils/report_generator.py`)**

**Purpose**: Generate comprehensive reports

**Key Features**:
- Multiple formats (HTML, CSV, JSON, TXT)
- Beautiful styling
- Statistics and charts
- Job details

**Flow**:
Collect Data → Generate HTML → Generate CSV → Generate JSON → Generate TXT → Save Files

text

### 8. **Database Handler (`src/data/database.py`)**

**Purpose**: Store and retrieve application data

**Key Features**:
- SQLite database
- Job tracking
- Run history
- Statistics

**Flow**:
Initialize → Create Tables → Save Jobs → Save Runs → Query Data → Return Stats

text

---

## 📊 Data Flow Diagram
┌─────────────────────────────────────────────────────────────────────┐
│ DATA FLOW │
├─────────────────────────────────────────────────────────────────────┤
│ │
│ .env ────────────────────► Config ──────────────► Settings │
│ │
│ Profiles ────────────────► User Data ──────────► Personal Info │
│ │
│ Q&A Database ────────────► Questions ──────────► Answers │
│ │
│ Naukri.com ──────────────► Browser ───────────► Page Actions │
│ │
│ Browser ─────────────────► Login ─────────────► Session │
│ │
│ Session ─────────────────► Search ────────────► Job Listings │
│ │
│ Job Listings ────────────► Apply ─────────────► Applications │
│ │
│ Applications ────────────► Database ──────────► Stored Jobs │
│ │
│ Stored Jobs ─────────────► Reports ───────────► Reports Files │
│ │
│ Reports ─────────────────► Notifications ────► Email/Desktop │
│ │
└─────────────────────────────────────────────────────────────────────┘

text

---

## 🛡️ Error Handling Flow
┌─────────────────────────────────────────────────────────────────────┐
│ ERROR HANDLING │
├─────────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────────┐ │
│ │ Error Occurred │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Log Error │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Take Screenshot │ │
│ └──────────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────┐ │
│ │ Is Retryable? │ │
│ └──────────────────┘ │
│ │ │
│ ┌────┴────┐ │
│ │ │ │
│ Yes No │
│ │ │ │
│ ▼ ▼ │
│ ┌────────┐ ┌──────────┐ │
│ │ Retry │ │ Report │ │
│ │ │ │ Error │ │
│ └────────┘ └──────────┘ │
│ │ │ │
│ ▼ ▼ │
│ ┌────────┐ ┌──────────┐ │
│ │ Success│ │ Continue │ │
│ └────────┘ └──────────┘ │
│ │
└─────────────────────────────────────────────────────────────────────┘

text

---

## 📈 Sequence Diagrams

### Login Sequence
User → run.py → main.py → NaukriLogin → BrowserManager → Naukri.com
│ │ │ │ │ │
│ │ │ │ │ │
│───▶ │ │ │ │ │
│ │───▶ │ │ │ │
│ │ │───▶ │ │ │
│ │ │ │───▶ │ │
│ │ │ │ │───▶ │
│ │ │ │ │ │───▶ Load
│ │ │ │ │ │◀─── Loaded
│ │ │ │ │◀─── │
│ │ │ │◀─── │ │
│ │ │◀─── │ │ │
│ │◀─── │ │ │ │
│◀─── │ │ │ │ │
│ │ │ │ │ │
│ │ │ │ │ │
│───▶ │ │ │ │ │
│ │───▶ │ │ │ │
│ │ │───▶ │ │ │
│ │ │ │───▶ │ │
│ │ │ │ │───▶ Click │
│ │ │ │ │ │───▶ Login
│ │ │ │ │ │◀─── Result
│ │ │ │ │◀─── │
│ │ │ │◀─── │ │
│ │ │◀─── │ │ │
│ │◀─── │ │ │ │
│◀─── │ │ │ │ │

text

### Application Sequence
User → run.py → main.py → NaukriApplier → NaukriApply → Naukri.com
│ │ │ │ │ │
│ │ │ │ │ │
│───▶ │ │ │ │ │
│ │───▶ │ │ │ │
│ │ │───▶ │ │ │
│ │ │ │───▶ │ │
│ │ │ │ │───▶ │
│ │ │ │ │ │───▶ Apply
│ │ │ │ │ │◀─── Form
│ │ │ │ │◀─── │
│ │ │ │◀─── │ │
│ │ │◀─── │ │ │
│ │◀─── │ │ │ │
│◀─── │ │ │ │ │
│ │ │ │ │ │
│ │ │ │ │ │
│───▶ │ │ │ │ │
│ │───▶ │ │ │ │
│ │ │───▶ │ │ │
│ │ │ │───▶ │ │
│ │ │ │ │───▶ Resume │
│ │ │ │ │ │───▶ Upload
│ │ │ │ │ │◀─── Done
│ │ │ │ │ │
│ │ │ │ │───▶ Questions│
│ │ │ │ │ │───▶ Answer
│ │ │ │ │ │◀─── Done
│ │ │ │ │ │
│ │ │ │ │───▶ Submit │
│ │ │ │ │ │───▶ Submit
│ │ │ │ │ │◀─── Done
│ │ │ │ │◀─── │
│ │ │ │◀─── │ │
│ │ │◀─── │ │ │
│ │◀─── │ │ │ │
│◀─── │ │ │ │ │

text

---

## ⚙️ Configuration Guide

### Environment Variables (.env)

```env
# Required - Naukri Credentials
NAUKRI_EMAIL=your_email@example.com
NAUKRI_PASSWORD=your_password

# Optional - Job Preferences
JOB_KEYWORDS="Python Developer,Full Stack Developer"
JOB_LOCATION="Bangalore"
EXCLUDE_KEYWORDS="senior,lead,manager"
MAX_APPLICATIONS=10

# Optional - Browser Settings
HEADLESS=false
USER_DATA_DIR=./browser_data

# Optional - Notifications
NOTIFICATIONS_ENABLED=true

# Optional - Email Reports
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
REPORT_EMAILS=recipient@example.com
User Profile (profiles/user_profile.yaml)
yaml
personal_info:
  first_name: "Sachin"
  last_name: "Chakrawarti"
  email: "chakrawartisachin012@gmail.com"
  phone: "7879393032"
  city: "Bangalore"
  gender: "Male"
  date_of_birth: "2001-03-20"

resume:
  path: "./mydata/resume/Sachin Chakrawarti - Resume.pdf"

preferences:
  job_types:
    - "Full-time"
    - "Internship"
  locations:
    - "Bangalore"
    - "Remote"
  salary_expectation: "15-20 LPA"
  notice_period: "30 days"
🚀 Quick Start
bash
# 1. Clone and setup
git clone <repo>
cd naukri_automation

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Configure
cp .env.example .env
# Edit .env with your credentials

# 5. Run
python run.py
📝 Summary
The Naukri Job Automation system provides a complete, automated solution for job applications with:

✅ Robust Login - Multiple fallback methods

✅ Smart Search - Multiple search strategies

✅ Automated Application - Full form filling

✅ Question Handling - 1000+ Q&A database

✅ Resume Upload - Multiple methods

✅ Comprehensive Reports - Multiple formats

✅ Error Handling - Retry and fallback

✅ Notifications - Desktop and email

✅ Database Storage - Track all applications

✅ Analytics - Track performance

Document Version: 1.0.0
Last Updated: 2026-07-21

text
