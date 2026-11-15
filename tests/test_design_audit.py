"""Tests for the model design audit: its counts come from the table, its readings from the export.

Run from the repo root:  python -m unittest discover -s tests -p test_design_audit.py -v
Needs numpy, pandas and scikit-learn. The slow, fitted part of the audit is not re-run here
(python model/design_audit.py does that, in about a minute): these tests recompute the parts
that need no fitting and compare them with the committed file.
"""
import importlib.util
import json
from pathlib import Path
import unittest

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


audit = load("design_audit", ROOT / "model" / "design_audit.py")


class DesignAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved = json.loads(audit.OUT.read_text(encoding="utf-8"))
        cls.df = pd.read_csv(audit.per_fuel.CLEAN)

    def test_the_counts_are_what_the_table_says(self):
        self.assertEqual(json.loads(json.dumps(audit.data_facts(self.df))), self.saved["data"])

    def test_the_counts_add_up(self):
        data = self.saved["data"]
        self.assertEqual(sum(data["endings_in_scope"].values()), data["tests_in_scope"])
        for fuel, bands in data["endings_by_oxygen"].items():
            total = sum(sum(band.values()) for band in bands.values())
            self.assertEqual(total, int((audit.per_fuel.scope_of(self.df)["fuel"] == fuel).sum()), fuel)
        disrupted = sum(band["Disruption"] for bands in data["endings_by_oxygen"].values() for band in bands.values())
        self.assertEqual(disrupted, data["endings_in_scope"]["Disruption"])

    def test_the_quoted_readings_are_the_exports(self):
        """The readings the documents quote, recomputed from console/model.js by hand."""
        model = audit.read_export()
        for name, (fuel, values) in audit.POINTS.items():
            self.assertEqual(audit.reading(model, fuel, values), self.saved["fitted"]["readings"][name], name)
        start = self.saved["fitted"]["readings"]["heptane at the starting values"]
        lo, hi = start["range_pct"]
        self.assertLess(lo, start["burns_all_its_fuel_among_clear_outcomes_pct"])
        self.assertLess(start["burns_all_its_fuel_among_clear_outcomes_pct"], hi)
        self.assertAlmostEqual(sum(start["all_three_pct"].values()), 100, delta=0.2)

    def test_the_moon_base_reading_is_mostly_disruption(self):
        """The fact that started this audit: near Moon Base air NASA's heptane tests were disrupted, and the model says so."""
        self.assertEqual(self.saved["data"]["heptane_at_29_to_31_pct_oxygen_near_0_7_atm"], {"Completion": 0, "Extinction": 0, "Disruption": 4})
        self.assertGreater(self.saved["fitted"]["readings"]["heptane in Moon Base air"]["disruption_pct"], 90)


if __name__ == "__main__":
    unittest.main()
