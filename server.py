#!/usr/bin/env python3
"""
Minimal HTTP wrapper so the automation can run as a Render Web Service
instead of a paid Cron Job. Render's free web-service tier requires no
payment info; a paid Cron Job does.

GET  /          - health check (also what keeps/wakes a free instance)
POST /run-job   - starts one automation pass in a background thread and
                   returns immediately. The job itself takes minutes
                   (real browser automation), far longer than it's safe
                   to hold a free-tier HTTP request open, so the result
                   is emailed via EmailSender rather than returned in
                   the response. Trigger this daily with any external
                   scheduler (cron-job.org, GitHub Actions schedule,
                   UptimeRobot, etc).
"""
import os
import threading
import logging
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

logger = logging.getLogger(__name__)

_job_lock = threading.Lock()
_job_running = False


def _run_job():
    global _job_running
    from run import run_automation_once
    from src.utils.email_sender import EmailSender

    started = datetime.now(timezone.utc)
    to_emails = [e.strip() for e in os.getenv("REPORT_EMAIL_TO", "").split(",") if e.strip()]

    try:
        result = run_automation_once()
        status = "OK" if result == 0 else "FAILED"
        body = f"Naukri automation run finished with status {status}.\nStarted: {started.isoformat()}\n"
    except Exception as e:
        status = "ERROR"
        body = f"Naukri automation run raised an exception.\nStarted: {started.isoformat()}\nError: {e}\n"
        logger.exception("Automation run failed")
    finally:
        with _job_lock:
            _job_running = False

    if to_emails:
        try:
            EmailSender().send_report(to_emails, f"Naukri automation - {status}", body)
        except Exception:
            logger.exception("Failed to send report email")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        if self.path == "/":
            self._send(200, "ok")
        else:
            self._send(404, "not found")

    def do_POST(self):
        global _job_running
        if self.path != "/run-job":
            self._send(404, "not found")
            return

        expected_token = os.getenv("TRIGGER_TOKEN", "")
        if expected_token and self.headers.get("X-Trigger-Token") != expected_token:
            self._send(401, "unauthorized")
            return

        with _job_lock:
            if _job_running:
                self._send(409, "job already running")
                return
            _job_running = True

        threading.Thread(target=_run_job, daemon=True).start()
        self._send(202, "job started")

    def log_message(self, fmt, *args):
        logger.info("%s - %s", self.address_string(), fmt % args)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    port = int(os.getenv("PORT", 10000))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    logger.info(f"Listening on 0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
