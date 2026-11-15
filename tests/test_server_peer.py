import io
import json
import threading
import unittest
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from server import serve


class PeerTests(unittest.TestCase):
    def setUp(self):
        self.server = SimpleNamespace(
            peer="http://station.test:8000", model="ember", where="the base", host="base",
            records=[{"id": "PSI-69", "title": "FLEX", "objectives": "fixture", "approach": "fixture"}],
            one_at_a_time=threading.Lock(), export_lock=threading.Lock(), exports=Path("exports"), lan=False,
        )
        self.local_models = self.enterContext(patch.object(serve, "local_models", return_value=["ember"]))
        self.enterContext(patch("builtins.print"))

    def handler(self, path, body=b""):
        handler = object.__new__(serve.Handler)
        handler.server, handler.path = self.server, path
        handler.headers = {"Content-Length": str(len(body))}
        handler.rfile, handler.wfile = io.BytesIO(body), io.BytesIO()
        handler.note_visitor, handler.send_json, handler.send_error = Mock(), Mock(), Mock()
        return handler

    @staticmethod
    def response(body, media):
        response = io.BytesIO(body)
        response.headers = Message()
        response.headers["Content-Type"] = media
        return response

    def test_peer_status_reports_only_local_models_even_with_a_configured_peer(self):
        handler = self.handler("/peer/ai")
        with patch.object(serve, "open_peer") as onward:
            handler.do_GET()
        onward.assert_not_called()
        status = handler.send_json.call_args.args[0]
        self.assertEqual(status["default"], "local:ember")
        self.assertEqual([b["id"] for b in status["brains"]], ["local:ember"])

    def test_peer_answer_falls_back_only_to_a_local_model(self):
        body = json.dumps({"question": "Explain this reading", "page": "console", "brain": "local:previous"}).encode()
        handler = self.handler("/peer/ask", body)
        handler.start_answer = Mock()
        with patch.object(serve, "open_peer") as onward, patch.object(serve, "ask_model", return_value=["Answer"]) as model:
            handler.do_POST()
        onward.assert_not_called()
        self.assertEqual(model.call_args.args[0], "ember")
        handler.start_answer.assert_called_once_with("ember on the base", ["PSI-69"], True)
        self.assertEqual(handler.wfile.getvalue(), b"Answer")
        self.local_models.return_value = []
        handler = self.handler("/peer/ask", body)
        with patch.object(serve, "open_peer") as onward:
            handler.do_POST()
        onward.assert_not_called()
        self.assertEqual(handler.send_error.call_args.args[0], 503)

    def test_peer_export_stores_once_and_does_not_forward(self):
        body = b"dashboard fixture"
        handler = self.handler("/peer/export", body)
        with patch.object(serve, "is_dashboard_export", return_value=True), \
             patch.object(serve, "store_export") as store, patch.object(serve, "open_peer") as onward:
            handler.do_POST()
        store.assert_called_once_with(self.server.exports, body)
        onward.assert_not_called()
        self.assertEqual(handler.send_json.call_args.args[0]["saved"], ["base"])

    def test_export_receipt_uses_configured_peer_and_preserves_local_success(self):
        body = b"dashboard fixture"
        cases = [
            ({"saved": ["other"], "link": "http://another.test/tests.csv"}, ["other", "base"], False),
            ({"saved": "other"}, ["base"], True),
        ]
        for remote, expected, missed in cases:
            with self.subTest(remote=remote):
                handler = self.handler("/export", body)
                with patch.object(serve, "is_dashboard_export", return_value=True), \
                     patch.object(serve, "store_export") as store, patch.object(serve, "peer_json", return_value=remote) as forward:
                    handler.do_POST()
                store.assert_called_once_with(self.server.exports, body)
                forward.assert_called_once_with(self.server, "/peer/export", 5, body, "text/csv")
                receipt = handler.send_json.call_args.args[0]
                self.assertEqual(receipt["saved"], expected)
                self.assertEqual(receipt["peer_missed"], missed)
                self.assertEqual(receipt["link"], None if missed else self.server.peer + "/tests.csv")

    def test_discovery_ignores_unusable_and_nested_models_and_normalizes_labels(self):
        remote = {"brains": [
            {}, {"id": "peer:local:ember", "up": True, "model": "ember"},
            {"id": "local:ember", "model": "ember", "up": True, "label": "Computer\nroom"},
        ]}
        with patch.object(serve, "peer_json", return_value=remote) as metadata:
            models = serve.brains(self.server)
        metadata.assert_called_once_with(self.server, "/peer/ai", 2)
        self.assertEqual([b["id"] for b in models], ["peer:local:ember", "local:ember"])
        self.assertEqual(models[0]["label"], "Computer room")
        with patch.object(serve, "peer_json", return_value={"brains": None}):
            self.assertEqual(serve.ai_status(self.server)["default"], "local:ember")

    def test_peer_metadata_requires_a_bounded_json_object(self):
        for body, media in ((b"[]", "application/json"), (b"{}", "text/plain"), (b'{"note":"too long"}', "application/json")):
            with self.subTest(body=body, media=media), patch.object(serve, "MAX_PEER_METADATA", 8), \
                 patch.object(serve, "open_peer", return_value=self.response(body, media)), self.assertRaises(ValueError):
                serve.peer_json(self.server, "/peer/ai", 2)

    def test_browser_answer_relays_only_expected_fields_and_known_record_ids(self):
        request = {"page": "console", "question": "Explain this reading", "reading": "sample", "extra": "unused"}
        handler = self.handler("/ask", json.dumps(request).encode())
        handler.send_header, handler.send_response, handler.end_headers = Mock(), Mock(), Mock()
        response = self.response(b"Answer", "text/plain")
        response.headers["X-Records-Used"] = "PSI-69,PSI-12345,PSI-69"
        response.headers["X-Brain-Label"] = "Model   label"
        response.headers["X-Brain-Fallback"] = "1"
        remote = {"id": "peer:local:ember", "label": "base", "up": True}
        with patch.object(serve, "brains", return_value=[remote]), patch.object(serve, "open_peer", return_value=response) as forward:
            handler.do_POST()
        server, path, _timeout, body, media = forward.call_args.args
        self.assertEqual((server, path, media), (self.server, "/peer/ask", "application/json"))
        self.assertEqual(json.loads(body), {"page": "console", "question": request["question"], "reading": "sample", "brain": "local:ember"})
        headers = dict(call.args for call in handler.send_header.call_args_list)
        self.assertEqual(headers["X-Records-Used"], "PSI-69")
        self.assertEqual(headers["X-Brain-Label"], "Model label")
        self.assertEqual(headers["X-Brain-Fallback"], "1")
        self.assertEqual(handler.wfile.getvalue(), b"Answer")

    def test_peer_answer_size_limit_closes_the_stream_without_a_second_answer(self):
        handler = self.handler("/ask", b'{"question":"Explain this reading","page":"console"}')
        handler.start_answer = Mock()
        response = self.response(b"Sample answer", "text/plain")
        remote = {"id": "peer:local:ember", "label": "base", "up": True}
        with patch.object(serve, "brains", return_value=[remote]), patch.object(serve, "MAX_PEER_ANSWER", 6), \
             patch.object(serve, "open_peer", return_value=response), patch.object(serve, "ask_model") as local:
            handler.do_POST()
        local.assert_not_called()
        self.assertTrue(response.closed)
        self.assertEqual(handler.wfile.getvalue(), b"Sample\n[The other machine's answer exceeded the size limit.]")

    def test_incompatible_peer_answer_falls_back_before_streaming(self):
        handler = self.handler("/ask", b'{"question":"Explain this reading","page":"console"}')
        handler.start_answer = Mock()
        response = self.response(b"{}", "application/json")
        remote = {"id": "peer:local:ember", "label": "base", "up": True}
        local = {"id": "local:ember", "model": "ember", "label": "handheld", "up": True}
        with patch.object(serve, "brains", return_value=[remote, local]), patch.object(serve, "open_peer", return_value=response), \
             patch.object(serve, "ask_model", return_value=["Local answer"]):
            handler.do_POST()
        self.assertTrue(response.closed)
        handler.start_answer.assert_called_once_with("handheld", ["PSI-69"], True)
        self.assertEqual(handler.wfile.getvalue(), b"Local answer")
