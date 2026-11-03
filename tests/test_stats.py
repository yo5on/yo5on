"""Offline tests for the stat generator and the Vercel function. Mock data only."""
import contextlib
import io
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from http.client import HTTPConnection
from http.server import HTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import generate_stats as g  # noqa: E402
from api import contributions as api  # noqa: E402

FAKE_TOKEN = "test-token-not-real"


def user(counts, start="2025-11-04", langs=None):
    """A GraphQL `user` payload whose calendar holds `counts`, one per day."""
    d0 = date.fromisoformat(start)
    days = [dict(date=(d0 + timedelta(i)).isoformat(), contributionCount=c,
                 weekday=(d0 + timedelta(i)).isoweekday() % 7)
            for i, c in enumerate(counts)]
    weeks, week = [], []
    for d in days:              # calendar weeks start on Sunday (weekday 0)
        if week and d["weekday"] == 0:
            weeks.append(dict(contributionDays=week))
            week = []
        week.append(d)
    if week:
        weeks.append(dict(contributionDays=week))
    repos = [dict(languages=dict(edges=[dict(size=s, node=dict(name=n))
                                        for n, s in r]))
             for r in (langs or [])]
    return dict(
        contributionsCollection=dict(contributionCalendar=dict(
            totalContributions=sum(counts), weeks=weeks)),
        repositories=dict(nodes=repos))


def days(counts, start="2026-01-01"):
    return [d for w in user(counts, start)["contributionsCollection"]
            ["contributionCalendar"]["weeks"] for d in w["contributionDays"]]


class Streaks(unittest.TestCase):
    def test_empty_calendar(self):
        cur, best = g.streaks([])
        self.assertEqual((cur["length"], best["length"]), (0, 0))

    def test_all_zero(self):
        cur, best = g.streaks(days([0] * 10))
        self.assertEqual((cur["length"], best["length"]), (0, 0))
        self.assertIsNone(cur["start"])

    def test_zero_today_keeps_current_streak(self):
        cur, _ = g.streaks(days([0, 1, 2, 3, 0]))
        self.assertEqual(cur, dict(length=3, start="2026-01-02",
                                   end="2026-01-04"))

    def test_zero_yesterday_breaks_current_streak(self):
        cur, best = g.streaks(days([1, 1, 0, 0]))
        self.assertEqual(cur["length"], 0)
        self.assertEqual(best["length"], 2)

    def test_active_today(self):
        cur, _ = g.streaks(days([0, 5, 1]))
        self.assertEqual((cur["length"], cur["end"]), (2, "2026-01-03"))

    def test_longest_keeps_first_of_equal_runs(self):
        _, best = g.streaks(days([1, 1, 0, 1, 1, 0]))
        self.assertEqual((best["length"], best["start"]), (2, "2026-01-01"))

    def test_longest_spans_week_boundaries(self):
        _, best = g.streaks(days([1] * 20 + [0] + [1] * 3))
        self.assertEqual(best, dict(length=20, start="2026-01-01",
                                    end="2026-01-20"))


class Summary(unittest.TestCase):
    def test_counts_from_calendar(self):
        counts = [0] * 365
        counts[10:17] = [1, 2, 3, 4, 5, 6, 7]    # one heavy stretch
        counts[-1] = 2
        s = g.summarise(user(counts))
        self.assertEqual(s["total"], 30)
        self.assertEqual(s["active"], 8)
        self.assertEqual(sum(s["weekly"]), 30)
        self.assertEqual(s["best_week"], max(s["weekly"]))
        self.assertLessEqual(s["best_week"], 28)

    def test_empty_calendar_and_no_repos(self):
        u = user([])
        u["contributionsCollection"]["contributionCalendar"]["weeks"] = []
        s = g.summarise(u)
        self.assertEqual((s["total"], s["active"], s["best_week"]), (0, 0, 0))
        self.assertEqual((s["by_size"], s["by_repo"]), ([], []))
        for svg in (g.draw_stats(s), g.draw_streak(s), g.draw_langs(s)):
            ET.fromstring(svg)


class Languages(unittest.TestCase):
    def test_bytes_and_primary_repo_counts(self):
        by_size, by_repo = g.languages(user([], langs=[
            [("Python", 100), ("C", 50)],
            [("C", 300)],
            [("Python", 10)],
            [],                                  # repo with no code
        ])["repositories"]["nodes"])
        self.assertEqual(by_size, [("C", 350), ("Python", 110)])
        self.assertEqual(by_repo, [("Python", 2), ("C", 1)])

    def test_null_languages_and_stable_ties(self):
        nodes = [dict(languages=None)] + user([], langs=[
            [("Zig", 5)], [("Ada", 5)]])["repositories"]["nodes"]
        by_size, by_repo = g.languages(nodes)
        self.assertEqual(by_size, [("Ada", 5), ("Zig", 5)])
        self.assertEqual(by_repo, [("Ada", 1), ("Zig", 1)])

    def test_top_five_only(self):
        by_size, _ = g.languages(user([], langs=[
            [(f"L{i}", i + 1) for i in range(9)]])["repositories"]["nodes"])
        self.assertEqual([n for n, _ in by_size], ["L8", "L7", "L6", "L5", "L4"])


class Window(unittest.TestCase):
    def test_whole_utc_days_365(self):
        # 23:30 in Bangalore is still the previous UTC day
        now = datetime(2026, 11, 3, 18, 0, tzinfo=timezone.utc)
        with mock.patch.object(g, "datetime", wraps=datetime) as dt:
            dt.now.return_value = now
            since, until = g.window()
        self.assertEqual((since, until),
                         ("2025-11-04T00:00:00Z", "2026-11-03T23:59:59Z"))
        span = (date.fromisoformat(until[:10]) - date.fromisoformat(since[:10]))
        self.assertEqual(span.days + 1, 365)


class Fetch(unittest.TestCase):
    def respond(self, payload):
        r = mock.MagicMock()
        r.__enter__.return_value = io.BytesIO(json.dumps(payload).encode())
        return mock.patch.object(g.urllib.request, "urlopen", return_value=r)

    def test_sends_window_and_timeout(self):
        with self.respond({"data": {"user": user([1])}}) as urlopen:
            g.fetch("someone", FAKE_TOKEN)
        req = urlopen.call_args.args[0]
        sent = json.loads(req.data)["variables"]
        self.assertEqual((sent["from"], sent["to"]), g.window())
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 7)

    def test_graphql_errors_abort(self):
        with self.respond({"errors": [{"message": "rate limited"}],
                           "data": {"user": user([1])}}):
            with self.assertRaises(SystemExit):
                g.fetch("someone", FAKE_TOKEN)

    def test_missing_user_aborts(self):
        with self.respond({"data": {"user": None}}):
            with self.assertRaises(SystemExit):
                g.fetch("ghost", FAKE_TOKEN)

    def test_timeout_propagates(self):
        with mock.patch.object(g.urllib.request, "urlopen",
                               side_effect=TimeoutError):
            with self.assertRaises(TimeoutError):
                g.fetch("someone", FAKE_TOKEN)


class Svg(unittest.TestCase):
    def sample(self):
        counts = [(i * 7) % 5 for i in range(365)]
        return g.summarise(user(counts, langs=[
            [("C++", 900), ("C#", 50)], [("Weird & <Lang>", 10)]]))

    def test_every_graphic_is_well_formed(self):
        s = self.sample()
        svgs = [g.draw_stats(s), g.draw_streak(s), g.draw_langs(s),
                g.draw_heading("about this page")]
        for svg in svgs:
            root = ET.fromstring(svg)
            self.assertEqual(root.attrib["width"], str(g.WIDTH))
            self.assertIn("@font-face", svg)
            self.assertIn("prefers-color-scheme:dark", svg)
            self.assertNotIn(FAKE_TOKEN, svg)

    def test_language_names_are_escaped(self):
        svg = g.draw_langs(self.sample())
        ET.fromstring(svg)
        self.assertIn("weird &amp; &lt;", svg)

    def test_committed_svgs_are_well_formed(self):
        for p in ROOT.glob("*.svg"):
            ET.parse(p)


class Main(unittest.TestCase):
    def run_main(self, out):
        env = {"GITHUB_TOKEN": FAKE_TOKEN, "GH_LOGIN": "someone", "OUT_DIR": out}
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env), \
                mock.patch.object(g, "fetch",
                                  return_value=user([1, 0, 2] * 100)), \
                contextlib.redirect_stdout(buf):
            g.main()
        return buf.getvalue()

    def test_second_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as out:
            first = self.run_main(out)
            names = sorted(os.listdir(out))
            snapshot = {n: Path(out, n).read_bytes() for n in names}
            second = self.run_main(out)
            self.assertIn("stats.svg", first)
            self.assertIn("updated: nothing", second)
            self.assertEqual(snapshot,
                             {n: Path(out, n).read_bytes() for n in names})
        self.assertEqual(names, sorted(
            ["stats.svg", "streak.svg", "langs.svg", "hd-about.svg",
             "hd-stack.svg", "hd-projects.svg", "hd-stats.svg",
             "hd-about-this-page.svg"]))

    def test_failed_fetch_leaves_files_untouched(self):
        with tempfile.TemporaryDirectory() as out:
            Path(out, "stats.svg").write_text("valid", encoding="utf-8")
            with mock.patch.dict(os.environ, {"GITHUB_TOKEN": FAKE_TOKEN,
                                              "OUT_DIR": out}), \
                    mock.patch.object(g.urllib.request, "urlopen",
                                      side_effect=urllib.error.URLError("down")):
                with self.assertRaises(urllib.error.URLError):
                    g.main()
            self.assertEqual(os.listdir(out), ["stats.svg"])
            self.assertEqual(Path(out, "stats.svg").read_text(), "valid")

    def test_missing_token_exits(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit):
                g.main()


class Endpoint(unittest.TestCase):
    def setUp(self):
        api._cached_svgs, api._cached_at = None, 0.0
        self.server = HTTPServer(("127.0.0.1", 0), api.handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def get(self, path):
        c = HTTPConnection(*self.server.server_address, timeout=5)
        c.request("GET", path)
        r = c.getresponse()
        body = r.read().decode()
        c.close()
        return r, body

    def env(self, token=FAKE_TOKEN):
        e = {"GITHUB_TOKEN": token} if token else {}
        return mock.patch.dict(os.environ, e, clear=True)

    def test_github_then_memory_with_consistent_data(self):
        fetch = mock.patch.object(api.generate_stats, "fetch",
                                  return_value=user([1, 1, 0, 3]))
        with self.env(), fetch as f:
            r1, stats = self.get("/api/contributions?graphic=stats")
            r2, streak = self.get("/api/contributions?graphic=streak")
        self.assertEqual(f.call_count, 1)        # one fetch feeds both graphics
        self.assertEqual(r1.status, 200)
        self.assertEqual(r1.getheader("Content-Type"),
                         "image/svg+xml; charset=utf-8")
        self.assertIn("no-store", r1.getheader("Cache-Control"))
        self.assertEqual(r1.getheader("X-Stats-Source"), "github")
        self.assertEqual(r2.getheader("X-Stats-Source"), "memory")
        self.assertEqual(int(r1.getheader("Content-Length")),
                         len(stats.encode()))
        ET.fromstring(stats)
        ET.fromstring(streak)

    def test_failure_without_cache_serves_committed_file(self):
        fetch = mock.patch.object(api.generate_stats, "fetch",
                                  side_effect=SystemExit("GraphQL errors: x"))
        with self.env(), fetch:
            r, body = self.get("/api/contributions?graphic=streak")
        self.assertEqual(r.status, 200)
        self.assertEqual(r.getheader("X-Stats-Source"), "fallback")
        self.assertEqual(r.getheader("Cache-Control"), "no-store")
        self.assertEqual(body, (ROOT / "streak.svg").read_text(encoding="utf-8"))
        self.assertNotIn("GraphQL", body)

    def test_missing_token_serves_fallback(self):
        with self.env(token=None):
            r, _ = self.get("/api/contributions?graphic=stats")
        self.assertEqual(r.getheader("X-Stats-Source"), "fallback")

    def test_failure_with_stale_cache_reports_memory(self):
        # regression: stale in-memory data used to be labelled "fallback"
        api._cached_svgs = {"stats": "<svg>cached</svg>", "streak": "<svg/>"}
        api._cached_at = api.monotonic() - api.FRESH_FOR - 1
        fetch = mock.patch.object(api.generate_stats, "fetch",
                                  side_effect=TimeoutError)
        with self.env(), fetch:
            r, body = self.get("/api/contributions?graphic=stats")
        self.assertEqual(body, "<svg>cached</svg>")
        self.assertEqual(r.getheader("X-Stats-Source"), "memory")
        self.assertEqual(r.getheader("Cache-Control"), "no-store")

    def test_unknown_graphic_is_404(self):
        r, _ = self.get("/api/contributions?graphic=../../etc/passwd")
        self.assertEqual(r.status, 404)


if __name__ == "__main__":
    unittest.main()
