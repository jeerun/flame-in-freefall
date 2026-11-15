"""Check the offline case pack against its source rows and the two contrasting examples."""
import json
import unittest

from data.clean import build_evidence


class EvidenceDataTests(unittest.TestCase):
    def test_export_matches_source_tables(self):
        script = (build_evidence.ROOT / "console" / "evidence-data.js").read_text(encoding="utf-8")
        payload = script.split("window.FLAME_EVIDENCE_DATA = ", 1)[1].strip().removesuffix(";")
        self.assertEqual(json.loads(payload), build_evidence.build())

    def test_demo_readings_preserve_reported_precision_and_qualifiers(self):
        evidence = build_evidence.build()
        gravity = {row["id"]: row for row in evidence["gravity"]["cases"]}
        sensor = {row["id"]: row for row in evidence["sensors"]["cases"]}
        self.assertEqual((gravity["2-2"]["earth"], gravity["2-2"]["orbit"]), ("7.6 cm", "~ 0"))
        self.assertEqual((gravity["2-5"]["earth"], gravity["2-5"]["orbit"]), ("Complete", "29 cm"))
        self.assertEqual(sensor["B18"]["oxygen"], ["17.4", "17.4"])
        self.assertEqual(sensor["B18"]["co"], ["47", "78"])
        self.assertEqual(sensor["F2"]["co"], ["105", "82"])
