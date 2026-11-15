import json
import threading
import unittest
import urllib.request
from unittest.mock import patch

from server import evidence_lab, serve


class LabServerTests(unittest.TestCase):
    def setUp(self):
        server = serve.Server(("127.0.0.1", 0), serve.Handler)
        server.seen, server.peer, server.model = {}, "", "test"
        server.one_at_a_time = threading.Lock()
        self.server = server
        self.url = f"http://127.0.0.1:{server.server_port}"
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .02})
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(thread.join)
        self.addCleanup(server.shutdown)

    def post(self, route, obj):
        req = urllib.request.Request(self.url + route, json.dumps(obj).encode(),
                                     {"Content-Type": "application/json", "Origin": self.url})
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.load(response)

    def test_player_seeks_to_bytes_in_bundled_movie(self):
        for path in sorted((serve.CONSOLE / "lab-media").glob("*.webm")):
            with self.subTest(film=path.name):
                request = urllib.request.Request(f"{self.url}/lab-media/{path.name}",
                                                 headers={"Range": "bytes=256-511"})
                with urllib.request.urlopen(request) as response, path.open("rb") as film:
                    film.seek(256)
                    self.assertEqual(response.status, 206)
                    self.assertEqual(response.headers["Content-Type"], "video/webm")
                    self.assertEqual(response.headers["Content-Range"], f"bytes 256-511/{path.stat().st_size}")
                    self.assertEqual(response.read(), film.read(256))

    def test_static_resources_and_sample_without_ollama(self):
        for asset in evidence_lab.ASSETS:
            with self.subTest(asset=asset), urllib.request.urlopen(self.url + "/" + asset) as response:
                self.assertTrue(response.read(1))
        with urllib.request.urlopen(self.url + "/lab/status") as response:
            self.assertEqual(json.load(response), {"table": True, "film": True})
        result = self.post("/lab/table", {"question": "Show all readings for test B1."})
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["rows"][0]["co"], ["0", "6"])

    def test_handheld_runs_peer_plan_against_its_copy_of_the_table(self):
        self.server.peer = "http://configured-pc"
        question = "Where did carbon monoxide rise?"
        plan = {"supported": True, "test_id": None, "filters": [{"gas": "co", "change": "up"}]}
        with patch.object(evidence_lab, "post_json", return_value={"plan": plan}) as relay:
            result = self.post("/lab/table", {"question": question})
        relay.assert_called_once_with("http://configured-pc/lab/table-plan", {"question": question}, timeout=45)
        self.assertEqual(result["status"], "ok")
        self.assertIn("B1", [row["id"] for row in result["rows"]])

    def test_local_film_route_does_not_forward_to_another_peer(self):
        self.server.peer = "http://configured-pc"
        frames = {"before": 8, "after": 9}
        with patch.object(evidence_lab.film_review, "review_clip", return_value=frames) as review:
            result = self.post("/lab/film-local", {})
        review.assert_called_once()
        self.assertEqual(result, frames)
