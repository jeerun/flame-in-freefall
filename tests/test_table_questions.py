import csv
import json
import unittest
from decimal import Decimal
from unittest.mock import Mock

from server import table_questions as table


def plan(*conditions, test_id=None):
    return {"supported": True, "test_id": test_id,
            "filters": [{"gas": gas, "change": change} for gas, change in conditions]}


class TestTableQuestions(unittest.TestCase):
    def test_offline_samples_match_fresh_execution_and_raw_csv(self):
        asset = (table.ROOT / "console/lab-table-examples.js").read_text(encoding="utf-8")
        actual = json.loads(asset.split("window.LAB_TABLE_EXAMPLES = ", 1)[1].removesuffix(";\n"))
        self.assertEqual(actual, json.loads(json.dumps(table.build_examples())))
        with table.CSV_PATH.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.reader(source)
            headers = next(reader)
            self.assertEqual(len(headers), 17)
            csv_rows = {reader.line_num: cells for cells in reader}
        for example in actual:
            result = example["result"]
            self.assertEqual(result["total"], len(csv_rows))
            self.assertEqual(result["matched"], len(result["rows"]))
            for row in result["rows"]:
                self.assertEqual(row["source"], list(map(list, zip(headers, csv_rows[row["line"]]))))
                self.assertEqual(row["id"], dict(row["source"])["Test #"])
        b1 = actual[0]["result"]["rows"][0]
        self.assertEqual((b1["id"], b1["line"], b1["o2"], b1["co"]),
                         ("B1", 2, ["22.2", "22.2"], ["0", "6"]))

    def test_model_only_selects_predicates(self):
        interpret = Mock(return_value=plan(("co", "down"), ("o2", "same")))
        result = table.answer_question("Where did CO fall while oxygen held steady?", interpret)
        messages, schema = interpret.call_args.args
        self.assertEqual(schema, table.PLAN_SCHEMA)
        self.assertEqual(messages[1]["content"], "Where did CO fall while oxygen held steady?")
        expected = []
        excluded = 0
        for row in table.source_rows():
            pairs = [table.decimal_pair(row[g]) for g in ("co", "o2")]
            if None in pairs:
                excluded += 1
            elif pairs[0][1] < pairs[0][0] and pairs[1][1] == pairs[1][0]:
                expected.append(row["line"])
        self.assertEqual([r["line"] for r in result["rows"]], expected)
        self.assertEqual(result["excluded"], excluded)

    def test_missing_and_censored_measurements_are_preserved(self):
        for test_id, raw in (("B2", ""), ("M5", ">500"), ("O4", "OR")):
            lookup = table.answer_question("Readings for " + test_id, lambda *_: plan(test_id=test_id))
            self.assertEqual(lookup["rows"][0]["co"][1], raw)
            queried = table.answer_question(f"Did CO rise in test {test_id}?",
                                            lambda *_: plan(("co", "up"), test_id=test_id))
            self.assertEqual((queried["status"], queried["matched"], queried["excluded"]), ("ok", 0, 1))
        self.assertEqual(table.decimal_pair(["-1", "0"]), (Decimal(-1), Decimal(0)))

    def test_explicit_test_o2_distinguished_from_oxygen_and_unknown_test(self):
        for test_id in ("O2", "O3a", "B999"):
            result = table.answer_question(f"Show test {test_id}", lambda *_: plan(test_id=test_id))
            self.assertEqual(result["status"], "ok")
            ids = [r["id"] for r in result["rows"]]
            self.assertEqual(ids, [] if test_id == "B999" else [test_id])
        self.assertEqual(table.answer_question("Which tests had rising O₂?")["status"], "unavailable")

    def test_partial_or_invalid_plans_decline_without_applying_filters(self):
        bad = [
            plan(("co", "up")), plan(("co", "down"), ("o2", "up")),
            plan(("co", "up"), ("o2", "down"), test_id="B1"),
            plan(("co", "up"), ("co", "up"), ("o2", "down")),
            plan(("co", ["up"]), ("o2", "down")),
            {"supported": True, "test_id": None, "filters": [], "answer": "fabricated"},
            None, [], "plain text", {"supported": False},
        ]
        for response in bad:
            with self.subTest(response=response):
                result = table.answer_question("Where did CO rise and oxygen fall?", lambda *_: response)
                self.assertEqual(result, {"status": "unsupported"})

    def test_unsupported_queries_and_network_failure(self):
        unavailable = Mock(side_effect=TimeoutError("local model busy"))
        for text in ("Was oxygen above 21?", "Which tests had rising CO or falling oxygen?",
                     "Which test had the largest rise in CO?", "Why did oxygen fall?",
                     "Show B1 and B2", "Did CO exceed 100 in B1?", "Which trials didn't show a CO rise?",
                     "Which cotton tests had rising CO?", "What material was used for B1?",
                     "Which PMMA tests had declining oxygen?", "Write a poem about the Moon", "a" * 321):
            with self.subTest(text=text):
                self.assertEqual(table.answer_question(text, unavailable), {"status": "unsupported"})
        unavailable.assert_not_called()
        with self.assertRaises(TimeoutError):
            table.answer_question("Which runs had falling oxygen?", unavailable)
