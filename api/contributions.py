"""Serve the existing contribution SVG designs with freshly fetched data."""

from http.server import BaseHTTPRequestHandler
import os
from pathlib import Path
from threading import Lock
from time import monotonic
from urllib.parse import parse_qs, urlparse

from scripts import generate_stats


ROOT = Path(__file__).resolve().parents[1]
FRESH_FOR = 5 * 60
# A refetch only happens once the cache is older than FRESH_FOR, so the stale
# window must be longer for _fallback to ever use it. A day matches how often
# the workflow refreshes the checked-in snapshot, so memory is never staler.
STALE_FOR = 24 * 60 * 60
_lock = Lock()
_cached_svgs = None
_cached_at = 0.0


def _generate():
    """Fetch once for both graphics, using the generator's existing semantics."""
    global _cached_svgs, _cached_at
    now = monotonic()
    with _lock:
        if _cached_svgs is not None and now - _cached_at < FRESH_FOR:
            return _cached_svgs, "memory"

        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            raise RuntimeError("source unavailable")
        login = os.environ.get("GH_LOGIN", "yo5on")
        summary = generate_stats.summarise(generate_stats.fetch(login, token))
        _cached_svgs = {
            "stats": generate_stats.draw_stats(summary),
            "streak": generate_stats.draw_streak(summary),
        }
        _cached_at = monotonic()
        return _cached_svgs, "github"


def _fallback(graphic):
    """Prefer recent in-process data, then the checked-in snapshot."""
    if _cached_svgs is not None and monotonic() - _cached_at <= STALE_FOR:
        return _cached_svgs[graphic]
    return (ROOT / f"{graphic}.svg").read_text(encoding="utf-8")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        graphic = parse_qs(urlparse(self.path).query).get("graphic", [""])[0]
        if graphic not in ("stats", "streak"):
            self.send_error(404)
            return

        try:
            svgs, source = _generate()
            body = svgs[graphic]
            # Keep the short-lived cache only inside this function instance.\n            # GitHub image proxy and CDN layers should revalidate every request.\n            cache = "no-cache, no-store, max-age=0, must-revalidate"
        except (Exception, SystemExit):
            # GraphQL errors, missing secrets, timeouts, and runtime failures never
            # reach the public response. The static SVGs remain safe fallbacks.
            body = _fallback(graphic)
            source = "fallback"
            cache = "no-store"

        payload = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Stats-Source", source)
        self.end_headers()
        self.wfile.write(payload)
