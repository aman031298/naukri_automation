#!/bin/bash
# Setup script for Naukri automation

echo "🔧 Setting up Naukri Job Automation..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright
echo "Installing Playwright browsers..."
playwright install chromium

# Create directories
echo "Creating directories..."
mkdir -p logs
mkdir -p reports/daily
mkdir -p reports/weekly
mkdir -p reports/templates
mkdir -p profiles
mkdir -p browser_data

# Create sample profile
if [ ! -f "profiles/user_profile.yaml" ]; then
    echo "Creating sample user profile..."
    cat > profiles/user_profile.yaml << EOL
personal_info:
  first_name: "Your"
  last_name: "Name"
  email: "your.email@example.com"
  phone: "+91-XXXXXXXXXX"

preferences:
  job_types:
    - "Full-time"
  locations:
    - "Bangalore"
    - "Remote"
  salary_expectation: "10-15 LPA"
  notice_period: "30 days"
EOL
fi

# Create .env from example
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo ""
echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Update .env with your Naukri credentials"
echo "2. Update profiles/user_profile.yaml with your details"
echo "3. Run: python src/main.py"