"""Tests for Idea Forge. Stdlib unittest and Flask's test client."""

import os
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.request
from urllib.error import URLError

from flask import render_template

from idea_forge import catalog, generator, storage, viz, web

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def free_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def wait_until(predicate, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.1)
    return False


def listening_ips(port):
    found = []
    hex_port = "%04X" % port
    with open("/proc/net/tcp", "r", encoding="ascii") as handle:
        next(handle)
        for line in handle:
            fields = line.split()
            ip_hex, port_hex = fields[1].split(":")
            state = fields[3]
            if port_hex.upper() == hex_port and state == "0A":
                found.append(ip_hex.upper())
    return found


class RunningServer(object):
    def __init__(self, db_path, port, generator_flag, interval):
        self.port = port
        self.log_path = db_path + ".log"
        env = dict(os.environ)
        env["IDEA_FORGE_DB"] = db_path
        env["IDEA_FORGE_PORT"] = str(port)
        env["IDEA_FORGE_GENERATOR"] = generator_flag
        env["IDEA_FORGE_INTERVAL"] = str(interval)
        env["IDEA_FORGE_SECRET_KEY"] = "test-secret"
        env["PYTHONUNBUFFERED"] = "1"
        self.log = open(self.log_path, "w", encoding="utf-8")
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "idea_forge.web"],
            cwd=REPO,
            env=env,
            stdout=self.log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    def close(self):
        if self.proc.poll() is None:
            os.killpg(self.proc.pid, signal.SIGTERM)
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL)
                self.proc.wait(timeout=5)
        self.log.close()

    def log_text(self):
        self.log.flush()
        with open(self.log_path, "r", encoding="utf-8") as handle:
            return handle.read()


class ForgeTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "idea_forge.sqlite")
        self._old = {}
        for key in (
            "IDEA_FORGE_DB",
            "IDEA_FORGE_SECRET_KEY",
            "IDEA_FORGE_GENERATOR",
            "IDEA_FORGE_PORT",
            "IDEA_FORGE_INTERVAL",
        ):
            self._old[key] = os.environ.get(key)
        os.environ["IDEA_FORGE_DB"] = self.db
        os.environ["IDEA_FORGE_SECRET_KEY"] = "test-secret"
        os.environ["IDEA_FORGE_GENERATOR"] = "0"
        self.app = web.create_app()
        self.client = self.app.test_client()

    def tearDown(self):
        for key, value in self._old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def add(self, problem_id, pattern_id, twist_id="paper"):
        spec = generator.compose(
            catalog.get_problem(problem_id),
            catalog.get_pattern(pattern_id),
            catalog.get_twist(twist_id),
        )
        return storage.insert_idea(self.db, spec)

    def token_from(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        marker = 'name="csrf_token" value="'
        start = text.find(marker)
        self.assertGreaterEqual(start, 0)
        start += len(marker)
        end = text.find('"', start)
        return text[start:end]


class FeedAndStaticTests(ForgeTestCase):
    def test_feed_renders_css_link(self):
        self.add("chart", "queue")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("/static/forge.css", html)
        self.assertIn("/static/forge.js", html)
        self.assertIn("Chart queue", html)
        self.assertIn("Estimate:", html)
        self.assertIn("Difficulty:", html)

    def test_static_css_and_js(self):
        css = self.client.get("/static/forge.css")
        js = self.client.get("/static/forge.js")
        self.assertEqual(css.status_code, 200)
        self.assertGreater(len(css.data), 0)
        self.assertEqual(js.status_code, 200)
        stylesheet = css.get_data(as_text=True)
        self.assertNotIn("http://", stylesheet)
        self.assertNotIn("https://", stylesheet)
        self.assertNotIn("conic-gradient", stylesheet)
        self.assertIn("translateY(-2px)", stylesheet)
        self.assertIn(".score-ring", stylesheet)
        self.assertGreater(len(js.data), 0)

    def test_templates_have_no_inline_styles_or_urls(self):
        template_dir = os.path.join(os.path.dirname(web.__file__), "templates")
        for name in os.listdir(template_dir):
            if not name.endswith(".html"):
                continue
            with open(os.path.join(template_dir, name), encoding="utf-8") as handle:
                text = handle.read()
            self.assertNotIn("style=", text)
            self.assertNotIn("http://", text)
            self.assertNotIn("https://", text)

    def test_empty_feed_is_one_sentence(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("No ideas match these filters.", html)


class RankingTests(ForgeTestCase):
    def test_ranking_formula(self):
        self.assertEqual(generator.rank_score(80, 60, 50, (45, 25, 30)), 66)
        self.assertEqual(generator.rank_score(100, 0, 0, (45, 25, 30)), 45)
        self.assertEqual(generator.rank_score(0, 100, 0, (45, 25, 30)), 25)
        self.assertEqual(generator.rank_score(0, 0, 100, (45, 25, 30)), 30)
        self.assertEqual(generator.rank_score(1, 0, 0, (1, 1, 0)), 1)
        idea_id = self.add("chart", "queue", "paper")
        idea = generator.assemble(storage.get_idea(self.db, idea_id), (45, 25, 30))
        expected = generator.rank_score(idea["impact"], idea["portfolio"], idea["feasibility"], (45, 25, 30))
        self.assertEqual(idea["score"], expected)
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn(">%d<" % expected, html)

    def test_dismissed_absent_from_ranked_feed(self):
        self.add("tools", "list")
        gone = self.add("chart", "board")
        self.assertTrue(storage.set_status(self.db, gone, "dismissed"))
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Tool list", html)
        self.assertNotIn("Chart board", html)

    def test_filter_by_area(self):
        self.add("chart", "queue")
        self.add("tools", "list")
        html = self.client.get("/?area=Clinics").get_data(as_text=True)
        self.assertIn("Chart queue", html)
        self.assertNotIn("Tool list", html)

    def test_settings_change_reranks_on_next_get(self):
        self.add("chart", "board", "paper")
        self.add("tools", "list", "paper")
        before = self.client.get("/").get_data(as_text=True)
        self.assertLess(before.index("Chart board"), before.index("Tool list"))
        denied = self.client.post(
            "/settings",
            data={
                "weight_impact": "0",
                "weight_portfolio": "0",
                "weight_feasibility": "100",
            },
        )
        self.assertEqual(denied.status_code, 400)
        still = self.client.get("/").get_data(as_text=True)
        self.assertLess(still.index("Chart board"), still.index("Tool list"))
        token = self.token_from("/settings")
        saved = self.client.post(
            "/settings",
            data={
                "csrf_token": token,
                "weight_impact": "0",
                "weight_portfolio": "0",
                "weight_feasibility": "100",
            },
        )
        self.assertEqual(saved.status_code, 302)
        after = self.client.get("/").get_data(as_text=True)
        self.assertLess(after.index("Tool list"), after.index("Chart board"))


class StatusAndExportTests(ForgeTestCase):
    def test_status_post_requires_csrf_and_persists(self):
        idea_id = self.add("chart", "board")
        missing = self.client.post("/ideas/%d/status" % idea_id, data={"status": "dismissed"})
        self.assertEqual(missing.status_code, 400)
        self.assertEqual(storage.get_idea(self.db, idea_id)["status"], "new")
        bad = self.client.post(
            "/ideas/%d/status" % idea_id,
            data={"status": "dismissed", "csrf_token": "not-the-token"},
        )
        self.assertEqual(bad.status_code, 400)
        self.assertEqual(storage.get_idea(self.db, idea_id)["status"], "new")
        token = self.token_from("/ideas/%d" % idea_id)
        saved = self.client.post(
            "/ideas/%d/status" % idea_id,
            data={"status": "dismissed", "csrf_token": token},
        )
        self.assertEqual(saved.status_code, 302)
        self.assertEqual(storage.get_idea(self.db, idea_id)["status"], "dismissed")
        html = self.client.get("/ideas/%d" % idea_id).get_data(as_text=True)
        self.assertIn("Summary", html)
        self.assertIn("Ranking", html)
        self.assertIn("Time", html)
        self.assertIn("Considerations", html)
        self.assertIn("Status", html)
        self.assertIn("Export", html)
        self.assertIn("author judgments", html)
        self.assertIn("Illustrative example", html)

    def test_markdown_export(self):
        idea_id = self.add("loans", "note")
        response = self.client.get("/ideas/%d.md" % idea_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/markdown")
        text = response.get_data(as_text=True)
        self.assertIn("Loan note", text)
        self.assertIn("Illustrative example", text)


class TemplateGroupTests(ForgeTestCase):
    def test_grouped_list_uses_items_key(self):
        path = os.path.join(os.path.dirname(web.__file__), "templates", "feed.html")
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("group['items']", source)
        self.assertNotIn("group.items", source)
        idea = {
            "id": 7,
            "score": 61,
            "name": "Grouped slip",
            "pitch": "A pitch that only appears inside the group.",
            "weeks": 4,
            "difficulty": "Low",
        }
        with self.app.test_request_context("/"):
            html = render_template(
                "feed.html",
                groups=[{"label": "Schools", "items": [idea]}],
                has_ideas=True,
                top_areas=[{"name": "Schools", "count": 2}],
                areas=["Schools"],
                difficulties=["Low", "Moderate", "High"],
                statuses=(("new", "New"),),
                area="",
                difficulty="",
                status="",
                q="",
                show_dismissed_note=False,
            )
        self.assertIn("Grouped slip", html)
        self.assertIn("Schools", html)
        self.assertIn(">2<", html)


class CatalogTests(ForgeTestCase):
    def test_catalog_is_illustrative_and_names_stay_short(self):
        self.assertGreaterEqual(len(catalog.PROBLEMS), 8)
        self.assertLessEqual(len(catalog.PROBLEMS), 12)
        pitches = set()
        for problem in catalog.PROBLEMS:
            self.assertTrue(problem["illustrative"])
            self.assertNotIn("url", problem)
            self.assertNotIn("http", problem["summary"].lower())
        for problem, pattern, twist in catalog.combinations():
            spec = generator.compose(problem, pattern, twist)
            self.assertLessEqual(len(spec["name"].split()), 3)
            self.assertNotIn("\n", spec["pitch"])
            self.assertNotIn(spec["pitch"], pitches)
            pitches.add(spec["pitch"])
        self.assertEqual(catalog.estimate_weeks({"scope": 3, "difficulty": "Low"}), 4)
        self.assertEqual(catalog.estimate_weeks({"scope": 4, "difficulty": "Moderate"}), 6)
        self.assertEqual(catalog.estimate_weeks({"scope": 5, "difficulty": "High"}), 9)

    def test_next_idea_is_deterministic(self):
        first = generator.next_spec(set())
        self.assertEqual(first, generator.next_spec(set()))
        used = set([(first["problem_id"], first["pattern_id"], first["twist_id"])])
        second = generator.next_spec(used)
        self.assertEqual(second, generator.next_spec(used))
        self.assertNotEqual(
            (first["problem_id"], first["pattern_id"], first["twist_id"]),
            (second["problem_id"], second["pattern_id"], second["twist_id"]),
        )

    def test_ring_svg_has_no_inline_colors(self):
        svg = viz.score_ring_svg(66)
        self.assertNotIn("fill=", svg)
        self.assertNotIn("stroke=", svg)
        self.assertNotIn("style=", svg)
        self.assertIn(">66<", svg)


class GeneratorTests(ForgeTestCase):
    def test_generator_disabled_does_not_start_thread(self):
        os.environ["IDEA_FORGE_GENERATOR"] = "0"
        before = set(thread.name for thread in threading.enumerate())
        started = generator.start_generator(self.db)
        after = set(thread.name for thread in threading.enumerate())
        self.assertIsNone(started)
        self.assertNotIn("idea-forge-generator", after)
        self.assertEqual(before, after)

        port = free_port()
        server = RunningServer(self.db, port, "0", 0.4)
        try:
            def up():
                try:
                    with urllib.request.urlopen("http://127.0.0.1:%d/" % port, timeout=1) as response:
                        return response.status == 200
                except (URLError, TimeoutError, ConnectionError):
                    return False

            self.assertTrue(wait_until(up, 10), server.log_text())
            self.assertEqual(storage.count_ideas(self.db), 1)
            self.assertIn("0100007F", listening_ips(port))
            self.assertNotIn("00000000", listening_ips(port))
            time.sleep(1.3)
            self.assertEqual(storage.count_ideas(self.db), 1)
            self.assertIn("idea-forge-generator: off", server.log_text())
        finally:
            server.close()

    def test_generator_server_inserts_and_shuts_down(self):
        os.environ["IDEA_FORGE_GENERATOR"] = "1"
        os.environ["IDEA_FORGE_INTERVAL"] = "0.3"
        worker = generator.start_generator(self.db)
        try:
            self.assertIsNotNone(worker)
            self.assertTrue(worker.thread.is_alive())
            self.assertEqual(worker.thread.name, "idea-forge-generator")

            def grew():
                return storage.count_ideas(self.db) >= 1

            self.assertTrue(wait_until(grew, 5))
        finally:
            worker.stop()
            self.assertFalse(worker.thread.is_alive())

        port = free_port()
        server = RunningServer(self.db, port, "1", 0.4)
        try:
            def inserted():
                return storage.count_ideas(self.db) >= 2

            self.assertTrue(wait_until(inserted, 15), server.log_text())
            self.assertIn("idea-forge-generator: on", server.log_text())
            with urllib.request.urlopen("http://127.0.0.1:%d/" % port, timeout=2) as response:
                body = response.read().decode("utf-8")
                self.assertEqual(response.status, 200)
                self.assertIn("/static/forge.css", body)
            self.assertIn("0100007F", listening_ips(port))
        finally:
            server.close()
            self.assertIsNotNone(server.proc.poll())


if __name__ == "__main__":
    unittest.main()
