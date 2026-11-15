"""Tests for the per-fuel model: the export reproduces, the page computes the same numbers, nothing else changes.

Run from the repo root:  python -m unittest discover -s tests -p test_per_fuel_model.py -v
Needs numpy, pandas and scikit-learn. The two page tests also need Node.js on PATH and are
skipped without it. Everything runs in temporary folders: no file in the repo is written.
"""
import contextlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HAVE_NODE = bool(shutil.which("node"))



def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


per_fuel = load("per_fuel", ROOT / "model" / "train_per_fuel.py")
patch_console = load("patch_console", ROOT / "model" / "per_fuel" / "patch_console.py")
train = per_fuel.train


def read_export(path):
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(text[text.index("{"):text.rindex("}") + 1])


def cases_for(model, scope):
    """Every in-scope test, plus seeded random settings across the whole slider range for each fuel."""
    cases = [{"fuel": row.fuel, "values": {train.KEYS[k]: float(getattr(row, k)) for k in train.NUM}}
             for row in scope.itertuples()]
    rng = np.random.default_rng(train.SEED)
    for fuel, _ in train.FUELS:
        for _ in range(200):
            cases.append({"fuel": fuel, "values": {f["key"]: float(rng.uniform(f["min"], f["max"])) for f in model["features"]}})
    return cases


def page_predictions(page_html, model_js, cases, patched):
    """Run the page's own prediction code in Node, from a temporary copy, optionally patched by patch_console.py."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "console").mkdir()
        (root / "tests").mkdir()
        text = Path(page_html).read_text(encoding="utf-8")
        (root / "console" / "index.html").write_text(patch_console.patched(text) if patched else text, encoding="utf-8")
        shutil.copyfile(model_js, root / "console" / "model.js")
        shutil.copyfile(ROOT / "tests" / "console_prediction_runner.cjs", root / "tests" / "console_prediction_runner.cjs")
        proc = subprocess.run(["node", str(root / "tests" / "console_prediction_runner.cjs")], input=json.dumps(cases),
                              text=True, capture_output=True, check=True, timeout=60)
        return json.loads(proc.stdout)["predictions"]


class PerFuelModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        df = pd.read_csv(per_fuel.CLEAN)
        cls.scope = per_fuel.scope_of(df)
        cls.export = read_export(per_fuel.OUT_JS)
        cls.current = read_export(ROOT / "console" / "model.js")

    def test_rerun_reproduces_the_committed_files(self):
        """main() again, with its outputs pointed at a temporary folder: same export, same metrics."""
        saved = per_fuel.ROOT, per_fuel.OUT_DIR, per_fuel.OUT_JS, per_fuel.OUT_METRICS
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            per_fuel.ROOT, per_fuel.OUT_DIR = folder, folder   # ROOT is only used to print the output path
            per_fuel.OUT_JS, per_fuel.OUT_METRICS = folder / "model.js", folder / "metrics.json"
            try:
                with open(folder / "log.txt", "w", encoding="utf-8") as log, contextlib.redirect_stdout(log):
                    per_fuel.main()
                self.assertEqual(read_export(folder / "model.js"), self.export)
                self.assertEqual(json.loads((folder / "metrics.json").read_text(encoding="utf-8")),
                                 json.loads(saved[3].read_text(encoding="utf-8")))
            finally:
                per_fuel.ROOT, per_fuel.OUT_DIR, per_fuel.OUT_JS, per_fuel.OUT_METRICS = saved

    def test_only_the_two_formulas_and_their_accuracy_differ_from_the_current_export(self):
        new, old = self.export, self.current
        for key in ("fuels", "features", "tests"):
            self.assertEqual(new[key], old[key], key)
        changed = {k for k in set(new["meta"]) | set(old["meta"]) if new["meta"].get(k) != old["meta"].get(k)}
        self.assertLessEqual(changed, {"auc", "burn_rate_mae", "watch"})
        for part in ("extinction", "burn_rate"):
            self.assertEqual(set(new[part]), {"intercept", "fuel", "coef", "fuel_coef"})
            self.assertEqual(set(new[part]["fuel_coef"]), {k for k, _ in train.FUELS})

    def test_exported_coefficients_give_the_fitted_predictions(self):
        scope = self.scope
        ext = scope[scope["test_end"].isin(["Extinction", "Completion"])]
        rate = scope[scope["burn_rate_mm2_s"].notna()]
        clf = per_fuel.classifier().fit(per_fuel.design(ext), (ext["test_end"] == "Extinction").to_numpy(int))
        reg = per_fuel.regressor().fit(per_fuel.design(rate), rate["burn_rate_mm2_s"].to_numpy(float))
        self.assertEqual(per_fuel.as_parts(*train.raw_coefficients(clf)), self.export["extinction"])
        self.assertEqual(per_fuel.as_parts(*train.raw_coefficients(reg)), self.export["burn_rate"])

        def by_hand(part, frame):
            z = np.full(len(frame), part["intercept"], float)
            for i, (fuel, row) in enumerate(zip(frame["fuel"], frame[train.NUM].to_numpy(float))):
                z[i] += part["fuel"][fuel]
                for col, value in zip(train.NUM, row):
                    key = train.KEYS[col]
                    z[i] += (part["coef"][key] + part["fuel_coef"][fuel][key]) * value
            return z

        p = 1 / (1 + np.exp(-by_hand(self.export["extinction"], scope)))
        self.assertLess(np.max(np.abs(p - clf.predict_proba(per_fuel.design(scope))[:, 1])), 1e-4)
        k = by_hand(self.export["burn_rate"], scope)
        self.assertLess(np.max(np.abs(k - reg.predict(per_fuel.design(scope)))), 1e-4)

    @unittest.skipUnless(HAVE_NODE, "needs Node.js on PATH")
    def test_patched_page_computes_the_per_fuel_model(self):
        cases = cases_for(self.export, self.scope)
        got = page_predictions(ROOT / "console" / "index.html", per_fuel.OUT_JS, cases, patched=True)
        frame = pd.DataFrame([{"fuel": c["fuel"], **{col: c["values"][train.KEYS[col]] for col in train.NUM}} for c in cases])
        scope = self.scope
        ext = scope[scope["test_end"].isin(["Extinction", "Completion"])]
        rate = scope[scope["burn_rate_mm2_s"].notna()]
        clf = per_fuel.classifier().fit(per_fuel.design(ext), (ext["test_end"] == "Extinction").to_numpy(int))
        reg = per_fuel.regressor().fit(per_fuel.design(rate), rate["burn_rate_mm2_s"].to_numpy(float))
        p_out = np.array([g["pOut"] for g in got])
        raw_k = np.array([g["rawK"] for g in got])
        self.assertLess(np.max(np.abs(p_out - clf.predict_proba(per_fuel.design(frame))[:, 1])), 1e-4)
        self.assertLess(np.max(np.abs(raw_k - reg.predict(per_fuel.design(frame)))), 1e-4)
        self.assertLess(np.max(np.abs(np.array([g["pKeep"] for g in got]) - (1 - p_out))), 1e-12)
        self.assertLess(np.max(np.abs(np.array([g["K"] for g in got]) - np.maximum(0, raw_k))), 1e-12)
        # The unpatched page ignores "fuel_coef": it must not be mistaken for a page that already supports the model.
        plain = page_predictions(ROOT / "console" / "index.html", per_fuel.OUT_JS, cases, patched=False)
        self.assertGreater(np.max(np.abs(np.array([g["pOut"] for g in plain]) - p_out)), 0.05)

    @unittest.skipUnless(HAVE_NODE, "needs Node.js on PATH")
    def test_patched_page_leaves_the_current_model_unchanged(self):
        cases = cases_for(self.current, self.scope)
        before = page_predictions(ROOT / "console" / "index.html", ROOT / "console" / "model.js", cases, patched=False)
        after = page_predictions(ROOT / "console" / "index.html", ROOT / "console" / "model.js", cases, patched=True)
        self.assertEqual(before, after)

    def test_patch_refuses_a_page_it_does_not_recognise(self):
        page = (ROOT / "console" / "index.html").read_text(encoding="utf-8")
        once = patch_console.patched(page)
        self.assertNotEqual(once, page)
        with self.assertRaises(ValueError):
            patch_console.patched(once)                      # already patched
        with self.assertRaises(ValueError):
            patch_console.patched(page.replace("pKeep >= 0.35", "pKeep >= 0.4"))   # a line it edits has changed


if __name__ == "__main__":
    unittest.main()
