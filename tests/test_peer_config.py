"""Offline checks for the peer address and Windows launcher entry points."""
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from server import peer_config, serve


ROOT = Path(__file__).resolve().parents[1]


class PeerOriginTests(unittest.TestCase):
    def test_normalizes_existing_peer_forms_and_default_ports(self):
        forms = {
            "run": "http://run", "RUN:8000": "http://run:8000",
            "HTTP://Run:80/": "http://run", "192.168.1.23:8000": "http://192.168.1.23:8000",
            "HTTPS://pc.example:443/": "https://pc.example",
            "::1": "http://[::1]", "[::1]:8000": "http://[::1]:8000",
            "https://[2001:db8::42]/": "https://[2001:db8::42]",
        }
        for value, expected in forms.items():
            with self.subTest(value=value):
                self.assertEqual(peer_config.normalize_origin(value), expected)
        self.assertEqual(peer_config.normalize_origin("http://run/", require_scheme=True), "http://run")
        with self.assertRaises(ValueError):
            peer_config.normalize_origin("run", require_scheme=True)

    def test_requires_origin_only(self):
        invalid = ("", "ftp://pc", "//pc", "http://name:password@pc", "http://pc/a",
                   "pc?", "pc#", "pc:0", "pc:65536", "pc:wrong", "pc:", "http://pc\t",
                   "one\ntwo", "two hosts", "-bad.local", "256.1.1.1", "[::1]extra")
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                peer_config.normalize_origin(value)

    def test_saves_only_valid_addresses_and_reuses_legacy_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "pc-address.txt"
            with patch("builtins.input", return_value="pc/path"), self.assertRaises(ValueError):
                peer_config.handheld_peer(path)
            with patch("builtins.input", return_value=""):
                self.assertEqual(peer_config.handheld_peer(path), "")
            self.assertFalse(path.exists())
            with patch("builtins.input", return_value="PC:8000"):
                self.assertEqual(peer_config.handheld_peer(path), "http://pc:8000")
            self.assertEqual(path.read_text().strip(), "http://pc:8000")
            path.write_bytes(b"run:8080\r\n")
            with patch("builtins.input", side_effect=AssertionError("unexpected prompt")):
                self.assertEqual(peer_config.handheld_peer(path), "http://run:8080")
                path.write_text("pc\nsecond-host")
                with self.assertRaisesRegex(ValueError, "pc-address.txt"):
                    peer_config.handheld_peer(path)
                self.assertEqual(path.read_text(), "pc\nsecond-host")

    def test_direct_cli_rejects_bad_peer_before_startup(self):
        with patch.object(sys, "argv", ["serve.py", "--peer", "http://run/not-an-origin"]), \
             patch.object(sys, "stderr", new_callable=io.StringIO), patch.object(serve, "gpu_name") as hardware:
            with self.assertRaises(SystemExit) as error:
                serve.main()
            self.assertEqual(error.exception.code, 2)
            hardware.assert_not_called()

    def test_cancel_handheld_prompt_before_startup(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(serve, "ROOT", Path(folder)), \
             patch.object(sys, "argv", ["serve.py", "--handheld-peer"]), \
             patch.object(sys, "stdout", new_callable=io.StringIO), patch.object(serve, "gpu_name") as hardware:
            for cancelled in (EOFError, KeyboardInterrupt):
                with self.subTest(cancelled=cancelled), patch("builtins.input", side_effect=cancelled):
                    serve.main()
                    hardware.assert_not_called()
                    self.assertFalse((Path(folder) / "pc-address.txt").exists())


@unittest.skipUnless(os.name == "nt", "Windows batch launchers")
class WindowsLaunchTests(unittest.TestCase):
    def test_launchers_pass_fixed_arguments_and_restore_working_directory(self):
        # The copied batch files run a stand-in that captures arguments without starting a service.
        cases = {
            "Start dashboard.bat": ["--open"],
            "Start on Legion Go.bat": ["--open", "--model", "gemma4:e2b", "--name", "the Legion Go itself", "--handheld-peer"],
        }
        with tempfile.TemporaryDirectory() as folder:
            caller = Path(folder)
            repo = caller / "repo with spaces"
            (repo / "server").mkdir(parents=True)
            (repo / "pc-address.txt").write_text("run:8000")
            (repo / "server" / "serve.py").write_text("import sys\nprint(repr(sys.argv[1:]))\n")
            for name, expected in cases.items():
                with self.subTest(name=name):
                    launcher = repo / name
                    shutil.copyfile(ROOT / name, launcher)
                    data = launcher.read_bytes()
                    self.assertEqual(data.count(b"\r\n"), data.count(b"\n"))
                    run = subprocess.run(
                        ["cmd.exe", "/d", "/q"], cwd=caller, text=True, capture_output=True, timeout=15,
                        env={**os.environ, "FLAME_LAUNCHER_TEST": str(launcher)},
                        input='@echo off\ncall "%FLAME_LAUNCHER_TEST%" <nul\ncd\nexit\n',
                    )
                    self.assertEqual(run.returncode, 0, run.stderr)
                    self.assertIn(repr(expected), run.stdout)
                    self.assertIn(str(caller), run.stdout.splitlines())


if __name__ == "__main__":
    unittest.main()
