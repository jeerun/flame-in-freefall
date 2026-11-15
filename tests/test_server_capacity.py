import io
import json
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from server import serve


class OllamaTransportTests(unittest.TestCase):
    def test_status_and_generation_use_direct_loopback_transport(self):
        with patch.object(serve.urllib.request, "build_opener") as build:
            opener = build.return_value
            opener.open.side_effect = [
                io.BytesIO(b'{"models":[{"name":"ember"}]}'),
                io.BytesIO(b'{"message":{"content":"Ready"},"done":true}\n'),
            ]
            self.assertEqual(serve.local_models(), ["ember"])
            self.assertEqual(list(serve.ask_model("ember", "Answer briefly", "Ready?")), ["Ready"])
        self.assertEqual(build.call_count, 2)
        for call in build.call_args_list:
            proxy, redirect = call.args
            self.assertEqual(proxy.proxies, {})
            self.assertIsInstance(redirect, serve.NoRedirect)
        status, generation = opener.open.call_args_list
        self.assertEqual(status.args[0], serve.OLLAMA + "/api/tags")
        self.assertEqual(generation.args[0].full_url, serve.OLLAMA + "/api/chat")


class CapacityTests(unittest.TestCase):
    def setUp(self):
        # Exercise admission without a listener, worker threads, or an Ollama service.
        with patch.object(serve.ThreadingHTTPServer, "__init__", return_value=None):
            self.server = serve.Server(("localhost", 0), serve.Handler)
        self.server.handler_slots = threading.BoundedSemaphore(1)
        self.server.shutdown_request = Mock()
        self.sock = Mock()
        self.address = ("127.0.0.1", 8000)

    def test_full_server_does_not_start_another_worker(self):
        self.server.handler_slots.acquire()
        with patch.object(serve.ThreadingHTTPServer, "process_request") as start:
            self.server.process_request(self.sock, self.address)
        start.assert_not_called()
        self.sock.setblocking.assert_called_once_with(False)
        self.assertIn(b"503 Service Unavailable", self.sock.sendall.call_args.args[0])
        self.server.shutdown_request.assert_called_once_with(self.sock)
        self.assertFalse(self.server.handler_slots.acquire(blocking=False))

    def test_start_failure_returns_the_slot(self):
        with patch.object(serve.ThreadingHTTPServer, "process_request", side_effect=RuntimeError("no worker")):
            with self.assertRaises(RuntimeError):
                self.server.process_request(self.sock, self.address)
        self.assertTrue(self.server.handler_slots.acquire(blocking=False))

    def test_worker_releases_admission_after_disconnect(self):
        with patch.object(serve.ThreadingHTTPServer, "process_request"):
            self.server.process_request(self.sock, self.address)
        self.assertFalse(self.server.handler_slots.acquire(blocking=False))
        with patch.object(serve.ThreadingHTTPServer, "process_request_thread", side_effect=OSError("closed")):
            with self.assertRaises(OSError):
                self.server.process_request_thread(self.sock, self.address)
        self.assertTrue(self.server.handler_slots.acquire(blocking=False))

    def test_each_handler_sets_a_finite_socket_timeout(self):
        handler = object.__new__(serve.Handler)
        handler.request = self.sock
        handler.setup()
        self.assertGreater(serve.Handler.timeout, 0)
        self.sock.settimeout.assert_called_once_with(serve.Handler.timeout)


class LocalAnswerTests(unittest.TestCase):
    def setUp(self):
        self.question = "Fixture question for the local model"
        self.brain = {"id": "local:fixture", "label": "Fixture label", "model": "fixture", "up": True}
        self.handler = object.__new__(serve.Handler)
        self.handler.path = "/ask"
        body = json.dumps({"page": "console", "question": self.question, "reading": "fixture reading"}).encode()
        self.handler.headers = {"Content-Length": str(len(body)), "Content-Type": "application/json"}
        self.handler.rfile = io.BytesIO(body)
        self.handler.wfile = io.BytesIO()
        self.handler.note_visitor = Mock()
        self.handler.send_error = Mock()
        self.handler.start_answer = Mock()
        self.gate = threading.Lock()
        self.handler.server = SimpleNamespace(one_at_a_time=self.gate, records=[
            {"id": "PSI-69", "title": "FLEX", "objectives": "fixture", "approach": "fixture"}
        ])
        self.enterContext(patch.object(serve, "brains", return_value=[self.brain]))
        self.model = self.enterContext(patch.object(serve, "ask_model", return_value=["First ", "answer."]))

    def test_busy_request_gets_503_before_stream_headers(self):
        with self.gate:
            self.handler.do_POST()
        self.assertEqual(self.handler.send_error.call_args.args[0], 503)
        self.handler.start_answer.assert_not_called()
        self.model.assert_not_called()

    def test_local_slot_released_when_writing_headers_fails(self):
        self.handler.start_answer.side_effect = BrokenPipeError("client closed")
        with self.assertRaises(BrokenPipeError):
            self.handler.do_POST()
        self.assertFalse(self.gate.locked())
        self.model.assert_not_called()

    def test_accepted_answer_streams_and_logs_only_counts(self):
        self.handler.start_answer.side_effect = lambda *_: self.assertTrue(self.gate.locked())
        with patch("builtins.print") as log:
            self.handler.do_POST()
        self.assertFalse(self.gate.locked())
        self.assertEqual(self.handler.wfile.getvalue(), b"First answer.")
        messages = "\n".join(" ".join(map(str, call.args)) for call in log.call_args_list)
        self.assertIn("13 chars", messages)
        self.assertNotIn(self.question, messages)
        self.assertNotIn("fixture", messages.lower())

    def test_access_log_omits_query_and_unknown_path_text(self):
        self.handler.log_message = Mock()
        self.handler.command = "POST"
        for path, expected in (("/ask?private-query", "/ask"), ("/private-path", "(unknown route)")):
            self.handler.path = path
            self.handler.log_request(200)
            self.handler.log_message.assert_called_with("%s %s %s", "POST", expected, 200)
