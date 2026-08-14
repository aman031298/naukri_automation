#!/usr/bin/env python3
"""
HTTP + WebSocket server so the automation can run as a Render Web
Service instead of a paid Cron Job, with a live view of the browser
while a job is running. Render's free web-service tier requires no
payment info; a paid Cron Job does.

GET  /            - health check (also what keeps/wakes a free instance)
GET  /live         - live-view page (renders the CDP screencast as it streams)
GET  /ws/live      - websocket: JPEG frames of the running browser, pushed
                     live via src/browser/screencast.py (Chrome DevTools
                     Protocol Page.startScreencast). Idle (no job running)
                     until POST /run-job starts one.
POST /run-job      - starts one automation pass in a background thread and
                     returns immediately. The job itself takes minutes
                     (real browser automation), far longer than it's safe
                     to hold a free-tier HTTP request open, so the result
                     is emailed via EmailSender rather than returned in
                     the response. Trigger this daily with any external
                     scheduler (cron-job.org, GitHub Actions schedule,
                     UptimeRobot, etc).

All routes except GET / require the same shared secret (TRIGGER_TOKEN)
the run trigger uses, since /live exposes the bot's live session
(effectively the logged-in Naukri account) to anyone with the URL.
"""
import asyncio
import base64
import os
import threading
import logging
from datetime import datetime, timezone

from aiohttp import web, WSMsgType

logger = logging.getLogger(__name__)

_job_lock = threading.Lock()
_job_running = False


def _check_token(request) -> bool:
    expected = os.getenv("TRIGGER_TOKEN", "")
    if not expected:
        return True
    supplied = request.headers.get("X-Trigger-Token") or request.query.get("token")
    return supplied == expected


def _run_job(loop):
    """Runs in a background thread (Playwright's sync API is blocking)."""
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


async def handle_health(request):
    return web.Response(text="ok")


async def handle_run_job(request):
    global _job_running
    if not _check_token(request):
        return web.Response(status=401, text="unauthorized")

    with _job_lock:
        if _job_running:
            return web.Response(status=409, text="job already running")
        _job_running = True

    loop = asyncio.get_running_loop()
    threading.Thread(target=_run_job, args=(loop,), daemon=True).start()
    return web.Response(status=202, text="job started")


LIVE_PAGE = """<!doctype html>
<html><head><title>Naukri automation - live view</title>
<style>
  body { background:#111; color:#eee; font-family:system-ui,sans-serif; margin:0; padding:1rem; }
  #frame { max-width:100%; border:1px solid #333; display:block; }
  #status { margin-bottom:0.75rem; }
</style></head>
<body>
  <div id="status">Connecting...</div>
  <img id="frame" alt="waiting for a job to run..." />
  <script>
    const params = new URLSearchParams(location.search);
    const token = params.get('token') || '';
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(proto + '://' + location.host + '/ws/live?token=' + encodeURIComponent(token));
    const status = document.getElementById('status');
    const img = document.getElementById('frame');
    ws.onopen = () => status.textContent = 'Connected. Waiting for a job to run...';
    ws.onclose = () => status.textContent = 'Disconnected.';
    ws.onerror = () => status.textContent = 'Connection error.';
    ws.onmessage = (ev) => {
      status.textContent = 'Live - ' + new Date().toLocaleTimeString();
      img.src = 'data:image/jpeg;base64,' + ev.data;
    };
  </script>
</body></html>"""


async def handle_live_page(request):
    if not _check_token(request):
        return web.Response(status=401, text="unauthorized")
    return web.Response(text=LIVE_PAGE, content_type="text/html")


async def handle_live_ws(request):
    if not _check_token(request):
        return web.Response(status=401, text="unauthorized")

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    loop = asyncio.get_running_loop()
    from src.browser import screencast

    def on_frame(frame_bytes):
        # Called from Playwright's driver thread; hop back to the
        # server's event loop to send over the websocket.
        asyncio.run_coroutine_threadsafe(
            _safe_send(ws, base64.b64encode(frame_bytes).decode()), loop
        )

    latest = screencast.get_latest_frame()
    if latest:
        await ws.send_str(base64.b64encode(latest).decode())

    screencast.subscribe(on_frame)
    try:
        async for msg in ws:
            if msg.type in (WSMsgType.ERROR, WSMsgType.CLOSE):
                break
    finally:
        screencast.unsubscribe(on_frame)

    return ws


async def _safe_send(ws, data):
    try:
        if not ws.closed:
            await ws.send_str(data)
    except Exception:
        logger.debug("Dropped frame to closed websocket")


def build_app():
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/live", handle_live_page)
    app.router.add_get("/ws/live", handle_live_ws)
    app.router.add_post("/run-job", handle_run_job)
    return app


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    port = int(os.getenv("PORT", 10000))
    web.run_app(build_app(), host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
