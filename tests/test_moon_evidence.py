"""Check the Moon atmosphere filter, its limits, and its citations to the raw CSVs."""
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from data.clean import build_moon_evidence as evidence


class MoonEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = evidence.build()

    def test_published_bundle_and_scope(self):
        self.assertEqual(evidence.OUTPUT.read_text(encoding="utf-8"), evidence.render(self.data))
        tables = self.data["tables"]
        self.assertEqual(len(tables), 9)
        self.assertEqual(sum(t["eligible"] for t in tables), self.data["eligible"])
        self.assertEqual(self.data["eligible"], 746)
        self.assertEqual([(t["name"], t["matches"]) for t in tables if t["matches"]],
                         [("CFI-G, normal flames", 20)])
        self.assertEqual(len(self.data["matches"]), 20)
        solid = [t for t in tables if t["material"] == "Solid materials"]
        self.assertEqual(len(solid), 3)
        self.assertTrue(all(t["pressureColumn"] is None and t["eligible"] == 0 for t in solid))
        burner = [t for t in tables if t["oxygenKind"] == "burner"]
        self.assertEqual(len(burner), 2)
        self.assertTrue(all(t["eligible"] == 0 and t["pressureColumn"] for t in burner))

    def test_every_matching_row_links_to_its_reported_readings(self):
        references = set()
        for match in self.data["matches"]:
            table = self.data["tables"][match["table"]]
            self.assertEqual((table["material"], table["pressureColumn"], table["gravityColumn"]),
                             ("Gas flames", "approx p (bar)", None))
            self.assertEqual((table["oxygenUnit"], table["pressureUnit"]), ("fraction", "bar"))
            raw = (evidence.tables.RAW / table["file"]).read_text(encoding="utf-8-sig").splitlines()
            header = [cell.strip() for cell in next(csv.reader(raw[:1]))]
            cited = raw[match["line"] - 1:match["endLine"]]
            row = dict(zip(header, next(csv.reader(cited))))
            self.assertEqual((match["test"], match["fuel"]), (row["Test"].strip(), row["Fuel"].strip()))
            self.assertEqual(match["oxygenRaw"], row["XO2 before test"])
            self.assertEqual(match["pressureRaw"], row["approx p (bar)"])
            self.assertAlmostEqual(match["oxygenPct"], float(match["oxygenRaw"]) * 100)
            self.assertAlmostEqual(match["pressurePsi"], float(match["pressureRaw"]) * 14.696 / 1.01325)
            references.add((table["file"], match["line"]))
        self.assertEqual(len(references), len(self.data["matches"]))

    def test_rounded_near_misses_and_missing_values_stay_out(self):
        source = next(s for s in evidence.tables.SOURCES if s[1] == "CFI")
        name = source[0]
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            with (directory / name).open("w", encoding="utf-8", newline="") as output:
                writer = csv.writer(output)
                writer.writerow(["Flex Number", "Fuel", "Oxygen", "Pressure"])
                writer.writerow(["", "", "", ""])
                writer.writerow(["A", "two\nlines", "0.30", "0.5 atm"])
                writer.writerow(["B", "sample", "0.29999", "0.5 atm"])
                writer.writerow(["C", "sample", "0.30", "0.6941 atm"])
                writer.writerow(["D", "sample", "0.30", "0 atm"])
                writer.writerow(["E", "sample", "0.30", ""])
            (directory / "MANIFEST.json").write_text(
                json.dumps({name: {"doi": "fixture", "investigation": "PSI-39"}}), encoding="utf-8")
            with patch.object(evidence.tables, "RAW", directory), patch.object(evidence.tables, "SOURCES", [source]):
                result = evidence.build()
        self.assertEqual((result["tables"][0]["rows"], result["eligible"]), (5, 3))
        self.assertEqual([(r["test"], r["line"], r["endLine"]) for r in result["matches"]], [("A", 3, 4)])
