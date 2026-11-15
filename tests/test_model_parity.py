"""Regression tests, including deliberate Console faults to prove detection."""

import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location(
    "parity", ROOT / "model/check_parity.py"
)
parity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parity)


class ParityTests(unittest.TestCase):
    def test_current_export_and_console(self):
        report = parity.check()
        self.assertTrue(report["passed"])
        self.assertGreater(report["negative_raw_K_cases"], 0)

    def mutated_report(self, old, new):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)

            for p in [
                "model/train.py",
                "model/train_per_fuel.py",
                "console/model.js",
                "console/index.html",
                "data/clean/flex_clean.csv",
                "tests/console_prediction_runner.cjs",
            ]:
                dest = root / p
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / p, dest)

            html = root / "console/index.html"
            content = html.read_text(encoding="utf-8")
            self.assertIn(old, content)
            html.write_text(
                content.replace(old, new, 1),
                encoding="utf-8",
            )

            return parity.check(root)

    def test_reversed_probability_is_detected(self):
        report = self.mutated_report(
            "pKeep: 1 - pOut",
            "pKeep: pOut",
        )
        self.assertFalse(report["passed"])
        self.assertGreater(
            report["max_absolute_errors"]["completion_complement"],
            0.1,
        )

    def test_missing_clamp_is_detected(self):
        report = self.mutated_report(
            "Math.max(0, linear(M.burn_rate, fuel, values))",
            "linear(M.burn_rate, fuel, values)",
        )
        self.assertFalse(report["passed"])
        self.assertGreater(
            report["max_absolute_errors"]["zero_clamp"],
            0,
        )


if __name__ == "__main__":
    unittest.main()