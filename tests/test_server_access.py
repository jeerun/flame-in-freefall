import base64
import http.client
import io
import ipaddress
import json
import threading
import unittest
from unittest.mock import patch

from server import serve


class NetworkOptionsTests(unittest.TestCase):
    def test_lan_requires_the_device_address_before_startup(self):
        for flags in (["--lan"], ["--allow-device", "192.0.2.2"]):
            with self.subTest(flags=flags), patch("sys.argv", ["serve.py", *flags]), \
                    patch("sys.stderr", new_callable=io.StringIO) as stderr, patch.object(serve, "gpu_name") as gpu:
                with self.assertRaises(SystemExit) as stop:
                    serve.main()
                self.assertEqual(stop.exception.code, 2)
                self.assertIn("--lan together with --allow-device", stderr.getvalue())
                gpu.assert_not_called()


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.server = serve.Server(("127.0.0.1", 0), serve.Handler)
        self.server.seen = {}
        self.server.host = "crew-test"
        self.server.public_origin = "https://crew.test"
        self.port = self.server.server_port
        self.host = f"127.0.0.1:{self.port}"
        worker = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01})
        worker.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(worker.join)
        self.addCleanup(self.server.shutdown)

    def request(self, path, *, method="GET", headers=None, body=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        try:
            connection.request(method, path, body=body, headers=headers or {})
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def test_lan_devices_are_explicit(self):
        self.assertTrue(self.server.verify_request(None, ("127.0.0.1", 1)))
        self.assertFalse(self.server.verify_request(None, ("192.0.2.2", 1)))
        self.server.allowed_devices = {ipaddress.IPv4Address("192.0.2.2")}
        self.assertTrue(self.server.verify_request(None, ("192.0.2.2", 1)))
        self.assertFalse(self.server.verify_request(None, ("192.0.2.3", 1)))

    def test_admin_log_requires_password_even_through_loopback(self):
        self.assertEqual(self.request("/who")[0], 401)
        credential = "crew:" + self.server.admin_password
        headers = {"Authorization": "Basic " + base64.b64encode(credential.encode()).decode()}
        code, body = self.request("/who", headers=headers)
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)["this_machine"], "crew-test")
        self.assertEqual(self.request("/who", headers={**headers, "Host": "crew.test"})[0], 404)
        self.assertEqual(self.request("/who", headers={**headers, "X-Forwarded-For": "192.0.2.2"})[0], 404)

    def test_host_and_origin_are_checked_separately_from_the_request_body(self):
        self.assertEqual(self.request("/", headers={"Host": "other.test"})[0], 403)
        self.assertEqual(self.request("/", headers={"Host": "crew.test"})[0], 200)
        media = {"Content-Type": "application/json"}
        with patch.object(serve, "brains", return_value=[]):
            def ask(headers):
                return self.request("/ask", method="POST", headers=headers, body=b'{"question":"Ready?"}')[0]
            self.assertEqual(ask({**media, "Origin": "https://other.test"}), 403)
            self.assertEqual(ask({"Content-Type": "text/plain"}), 415)
            # An allowed browser and a native client both reach normal model discovery.
            self.assertEqual(ask({**media, "Origin": "https://crew.test"}), 503)
            self.assertEqual(ask({**media, "Origin": "http://" + self.host}), 503)
            self.assertEqual(ask(media), 503)
