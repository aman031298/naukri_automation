# Playwright's official image ships matching browser binaries + all
# system deps Chromium needs (fonts, libnss3, etc.) so we don't have
# to hand-roll an apt-get list that will drift from the pinned version.
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Data/log/report dirs must exist before the app writes into them on
# a fresh container — Render's disk (if attached) mounts empty.
RUN mkdir -p data logs reports db

# Belt-and-suspenders: Render has no display, so force headless
# regardless of what HEADLESS is set to in the dashboard.
ENV HEADLESS=true
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
