"""
Live view of the automation's browser via Chrome DevTools Protocol
screencasting. Streams JPEG frames as the bot navigates/clicks/types,
so the run can be watched in real time from server.py's /live page
instead of only being visible after the fact in logs.

Uses Playwright's sync CDP session (Page.startScreencast) rather than
a full VNC/remote-desktop setup — CDP already emits rendered frames of
exactly what the headless page is doing, no extra display server needed.
"""
import base64
import logging
import threading

logger = logging.getLogger(__name__)

# Frame subscribers: each is a callable(bytes) invoked with raw JPEG
# bytes for every frame. server.py's websocket handler registers one
# per connected viewer.
_subscribers = []
_subscribers_lock = threading.Lock()
_latest_frame = None


def subscribe(callback):
    with _subscribers_lock:
        _subscribers.append(callback)


def unsubscribe(callback):
    with _subscribers_lock:
        if callback in _subscribers:
            _subscribers.remove(callback)


def get_latest_frame():
    return _latest_frame


def start(page, quality=60, max_width=960, max_height=540):
    """Start screencasting the given Playwright Page. Returns the CDP
    session so callers can stop() it when the run finishes."""
    global _latest_frame
    _latest_frame = None

    cdp = page.context.new_cdp_session(page)

    def on_frame(params):
        global _latest_frame
        try:
            frame_bytes = base64.b64decode(params["data"])
            _latest_frame = frame_bytes
            with _subscribers_lock:
                subs = list(_subscribers)
            for cb in subs:
                try:
                    cb(frame_bytes)
                except Exception:
                    logger.exception("Screencast subscriber failed")
        finally:
            # Screencast pauses after each frame until acknowledged.
            cdp.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]})

    cdp.on("Page.screencastFrame", on_frame)
    cdp.send("Page.startScreencast", {
        "format": "jpeg",
        "quality": quality,
        "maxWidth": max_width,
        "maxHeight": max_height,
        "everyNthFrame": 1,
    })
    logger.info("🎥 Screencast started")
    return cdp


def stop(cdp):
    global _latest_frame
    try:
        cdp.send("Page.stopScreencast")
    except Exception:
        logger.exception("Failed to stop screencast cleanly")
    _latest_frame = None
    logger.info("🎥 Screencast stopped")
