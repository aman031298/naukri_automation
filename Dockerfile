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

# Belt-and-suspenders: cloud hosts have no display, so force headless
# regardless of what HEADLESS is set to in the dashboard.
ENV HEADLESS=true
ENV PYTHONUNBUFFERED=1

# One-shot entrypoint: run.py executes a single application pass and
# exits. Render Cron Jobs start a fresh container per schedule tick
# and require the process to exit on its own — a resident scheduler
# loop (scheduler.py) never returns control, so Render would run it
# until the 12h hard timeout on every trigger. Timing is owned by
# render.yaml's `schedule` field instead of an in-process loop.
# scheduler.py is kept in the repo for non-Render/self-hosted use.
CMD ["python", "run.py"]
