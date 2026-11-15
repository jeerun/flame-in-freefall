"""Tests for the console's per-fuel model: the export reproduces, the page computes the same numbers, nothing else changed.

Run from the repo root:  python -m unittest discover -s tests -p test_per_fuel_model.py -v
Needs numpy, pandas and scikit-learn. The two page tests also need Node.js on PATH and are
skipped without it. Everything runs in temporary folders: no file in the repo is written.

Written for the pull request that proposed the model. On Nov 15, 2026 the console was switched to it, so
"the export" is now console/model.js, the base it is compared with is model/pooled/model.js, and the page
is tested as it is instead of through the patch.
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
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

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


def page_predictions(page_html, model_js, cases):
    """Run the page's own prediction code in Node, from a temporary copy that is given model_js as its export."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "console").mkdir()
        (root / "tests").mkdir()
        text = Path(page_html).read_text(encoding="utf-8")
        (root / "console" / "index.html").write_text(text, encoding="utf-8")
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
        cls.export = read_export(per_fuel.OUT_JS)        # console/model.js
        cls.base = read_export(per_fuel.BASE_JS)         # model/pooled/model.js: the base export with the earlier, one-slope formulas

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

    def test_only_the_two_formulas_and_their_accuracy_differ_from_the_base_export(self):
        new, old = self.export, self.base
        for key in ("fuels", "features", "tests"):
            self.assertEqual(new[key], old[key], key)
        changed = {k for k in set(new["meta"]) | set(old["meta"]) if new["meta"].get(k) != old["meta"].get(k)}
        self.assertEqual(changed, {"auc", "burn_rate_mae", "watch", "unsure"})
        self.assertNotIn("fuel_coef", old["extinction"])
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
    def test_page_computes_the_per_fuel_model(self):
        cases = cases_for(self.export, self.scope)
        got = page_predictions(ROOT / "console" / "index.html", per_fuel.OUT_JS, cases)
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
        # The two models must really differ on these inputs, or the check above would pass for the wrong export.
        plain = page_predictions(ROOT / "console" / "index.html", per_fuel.BASE_JS, cases)
        self.assertGreater(np.max(np.abs(np.array([g["pOut"] for g in plain]) - p_out)), 0.05)

    @unittest.skipUnless(HAVE_NODE, "needs Node.js on PATH")
    def test_page_still_reads_an_export_without_fuel_slopes(self):
        """Given the base export, the page computes the earlier, one-slope model: the page change is backward compatible."""
        cases = cases_for(self.base, self.scope)
        got = page_predictions(ROOT / "console" / "index.html", per_fuel.BASE_JS, cases)
        frame = pd.DataFrame([{"fuel": c["fuel"], **{col: c["values"][train.KEYS[col]] for col in train.NUM}} for c in cases])
        scope = self.scope
        ext = scope[scope["test_end"].isin(["Extinction", "Completion"])]
        rate = scope[scope["burn_rate_mm2_s"].notna()]
        clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000)).fit(train.design(ext), (ext["test_end"] == "Extinction").to_numpy(int))
        reg = make_pipeline(StandardScaler(), LinearRegression()).fit(train.design(rate), rate["burn_rate_mm2_s"].to_numpy(float))
        self.assertLess(np.max(np.abs(np.array([g["pOut"] for g in got]) - clf.predict_proba(train.design(frame))[:, 1])), 1e-4)
        self.assertLess(np.max(np.abs(np.array([g["rawK"] for g in got]) - reg.predict(train.design(frame)))), 1e-4)

    def test_patch_refuses_the_page_it_has_already_changed(self):
        """The patch that taught the page the per-fuel export was applied on Nov 15, 2026. It must not apply twice."""
        page = (ROOT / "console" / "index.html").read_text(encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            patch_console.patched(page)
        self.assertIn("already patched", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
