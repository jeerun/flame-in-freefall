import io
import json
import shutil
import subprocess
import tempfile
import threading
import unittest
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import Mock, patch

from server import serve


class ExportTests(unittest.TestCase):
    def test_incomplete_csv_never_reaches_storage_or_peer(self):
        data = b"flex_test,flex_id,fuel,\r\n"
        handler = object.__new__(serve.Handler)
        handler.headers = {"Content-Length": str(len(data))}
        handler.rfile = io.BytesIO(data)
        handler.send_error = Mock()
        with patch.object(serve, "store_export") as store, patch.object(urllib.request, "urlopen") as forward:
            handler.export()
        self.assertEqual(handler.send_error.call_args.args[0], 400)
        store.assert_not_called()
        forward.assert_not_called()

    def test_interrupted_replace_keeps_previous_file(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            target = folder / serve.CSV_NAME
            target.write_bytes(b"previous")
            with patch.object(serve.os, "replace", side_effect=OSError("storage unavailable")):
                with self.assertRaises(OSError):
                    serve.store_export(folder, b"replacement")
            self.assertEqual(target.read_bytes(), b"previous")
            self.assertEqual(list(folder.iterdir()), [target])

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed to run the dashboard's real CSV exporter")
    def test_dashboard_digest_and_loopback_relay(self):
        csv = subprocess.check_output(["node", str(serve.ROOT / "server" / "export_digest.cjs"), "--csv"])
        self.assertEqual(len(csv.splitlines()), 253)
        self.assertTrue(serve.is_dashboard_export(csv), "Review the export and run node server/export_digest.cjs")
        self.assertFalse(serve.is_dashboard_export(csv.replace(b"methanol", b"heptane", 1)))
        with tempfile.TemporaryDirectory() as temp, ExitStack() as stack:
            def start(host, peer=""):
                httpd = serve.Server(("127.0.0.1", 0), serve.Handler)
                httpd.host, httpd.peer, httpd.lan = host, peer, False
                httpd.seen, httpd.exports = {}, Path(temp) / host
                thread = threading.Thread(target=httpd.serve_forever, kwargs={"poll_interval": .05})
                thread.start()
                stack.callback(httpd.server_close)
                stack.callback(thread.join)
                stack.callback(httpd.shutdown)
                return "http://127.0.0.1:" + str(httpd.server_port)

            base = start("base")
            handheld = start("handheld", base)

            def send(_):
                req = urllib.request.Request(handheld + "/export", data=csv, headers={"Content-Type": "text/csv"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    return json.load(resp)

            with ThreadPoolExecutor(max_workers=3) as pool:
                receipts = list(pool.map(send, range(3)))
            for receipt in receipts:
                self.assertEqual(receipt["saved"], ["base", "handheld"])
                self.assertFalse(receipt["peer_missed"])
            for url in (handheld, base):
                with urllib.request.urlopen(url + "/tests.csv", timeout=5) as resp:
                    self.assertEqual(resp.read(), csv)
