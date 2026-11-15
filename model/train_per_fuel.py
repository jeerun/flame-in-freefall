"""Step 2 of 2. Train the two models the console uses, where each fuel has its own slopes, and export them.

Run from the repo root, after model/train.py:  python model/train_per_fuel.py
Needs: pandas, numpy, scikit-learn (written and checked with scikit-learn 1.9).

Writes
  console/model.js     the export the page reads: the base export from step 1 with the two formulas
                       replaced, plus "fuel_coef", "meta.watch" and "meta.unsure"
  model/metrics.json   held-out accuracy of these models

The console was switched to this model on Nov 15, 2026 (see docs/per-fuel-model.md for the
comparison that decided it).

What is different from model/train.py
  - Each fuel has its own slope for every setting. train.py gives heptane and
    methanol the same slopes and only a different starting point.
  - The strength of the logistic regression's penalty is picked from C_GRID by
    cross-validation inside the training rows only, so the held-out numbers
    also cover that choice.
Everything else is train.py's: the data, the scope, the inputs, the seed, the
number of repeats, and the two kinds of model (logistic and linear regression).
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression, LogisticRegressionCV
from sklearn.metrics import brier_score_loss, mean_absolute_error, r2_score, roc_auc_score
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean" / "flex_clean.csv"
BASE_JS = ROOT / "model" / "pooled" / "model.js"   # read only, written by model/train.py: ranges, sliders and the test rows are copied from it
OUT_DIR = ROOT / "console"
OUT_JS = OUT_DIR / "model.js"
OUT_METRICS = ROOT / "model" / "metrics.json"

C_GRID = [0.3, 1.0, 3.0, 10.0]   # penalty strengths tried (larger = weaker penalty)
WATCH = 0.30                     # the "watch" level: chance of burning all the fuel at or above this
BOOTSTRAPS = 1000                # refits on resampled tests, to see which slopes keep their sign


def load_train():
    """model/train.py as a module, so its constants and helpers are used, not copied."""
    spec = importlib.util.spec_from_file_location("training", ROOT / "model" / "train.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


train = load_train()
NUM, KEYS, FUELS, SEED, REPEATS = train.NUM, train.KEYS, train.FUELS, train.SEED, train.REPEATS


def scope_of(df):
    """The same rows as train.py: pressure known and at or below the limit, droplet size known."""
    return df[df["pressure_atm"].notna() & (df["pressure_atm"] <= train.MAX_PRESSURE_ATM) & df["d0_mm"].notna()].copy()


def design(df):
    """train.py's columns (settings, methanol flag), then each setting times that flag: methanol's own slopes."""
    base = train.design(df)
    return np.hstack([base, base[:, :len(NUM)] * base[:, len(NUM):]])


def classifier():
    inner = StratifiedKFold(4, shuffle=True, random_state=SEED)
    return make_pipeline(StandardScaler(), LogisticRegressionCV(
        Cs=C_GRID, cv=inner, scoring="neg_brier_score", l1_ratios=(0,), use_legacy_attributes=False, max_iter=20000))


def regressor():
    return make_pipeline(StandardScaler(), LinearRegression())


def as_parts(intercept, coef):
    """coef follows design(): heptane's slopes, methanol's offset, then what methanol adds to each slope."""
    n = len(NUM)
    return {
        "intercept": round(intercept, 6),
        "fuel": {"heptane": 0, "methanol": round(float(coef[n]), 6)},
        "coef": {KEYS[c]: round(float(v), 6) for c, v in zip(NUM, coef[:n])},
        "fuel_coef": {
            "heptane": {KEYS[c]: 0 for c in NUM},
            "methanol": {KEYS[c]: round(float(v), 6) for c, v in zip(NUM, coef[n + 1:])},
        },
    }


def slope_stability(ext, c):
    """Refit the outcome model on resampled tests: which slopes keep their sign?

    A slope whose sign flips in more than one refit in ten is one the tests do not settle. The console
    says so next to any sentence that leans on it (the export lists them under meta.unsure).
    """
    X, y = design(ext), (ext["test_end"] == "Extinction").to_numpy(int)

    def raw(Xb, yb):
        return train.raw_coefficients(make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=20000)).fit(Xb, yb))[1]

    n, k = len(y), len(NUM)
    fitted, rng, boots = raw(X, y), np.random.default_rng(SEED), []
    while len(boots) < BOOTSTRAPS:
        i = rng.integers(0, n, n)
        if y[i].min() != y[i].max():
            boots.append(raw(X[i], y[i]))
    boots = np.array(boots)
    out = {}
    for j, col in enumerate(NUM):
        for fuel_name, value, draws in (("heptane", fitted[j], boots[:, j]),
                                        ("methanol", fitted[j] + fitted[k + 1 + j], boots[:, j] + boots[:, k + 1 + j])):
            lo, hi = np.percentile(draws, [5, 95])
            out.setdefault(col, {})[fuel_name] = {
                "slope": round(float(value), 3), "p5": round(float(lo), 3), "p95": round(float(hi), 3),
                "sign_is_stable": bool(lo > 0 or hi < 0),
            }
    return out


def read_base_export():
    text = BASE_JS.read_text(encoding="utf-8")
    return json.loads(text[text.index("{"):text.rindex("}") + 1])


def main():
    df = pd.read_csv(CLEAN)
    scope = scope_of(df)

    # ---------- model 1: extinction ----------
    ext = scope[scope["test_end"].isin(["Extinction", "Completion"])].copy()
    Xe, ye = design(ext), (ext["test_end"] == "Extinction").to_numpy(int)
    clf = classifier()
    is_fuel = {k: (ext["fuel"] == k).to_numpy() for k, _ in FUELS}
    done = ye == 0   # burned to completion

    aucs, briers, accs = [], [], []
    fuel_aucs = {k: [] for k, _ in FUELS}
    found_at_half, watch_found, watch_false = [], [], []
    for r in range(REPEATS):
        cv = StratifiedKFold(5, shuffle=True, random_state=SEED + r)
        p = cross_val_predict(clf, Xe, ye, cv=cv, method="predict_proba")[:, 1]
        aucs.append(roc_auc_score(ye, p))
        briers.append(brier_score_loss(ye, p))
        accs.append(np.mean((p >= 0.5) == ye))
        for k in fuel_aucs:
            fuel_aucs[k].append(roc_auc_score(ye[is_fuel[k]], p[is_fuel[k]]))
        keep = 1 - p   # chance of burning all the fuel, as the console shows it
        found_at_half.append(np.mean(keep[done] > 0.5))
        watch_found.append(np.mean(keep[done] >= WATCH))
        watch_false.append(np.mean(keep[~done] >= WATCH))
    base_rate = float(ye.mean())
    clf.fit(Xe, ye)
    chosen_c = float(np.ravel(clf.steps[-1][1].C_)[0])
    ext_parts = as_parts(*train.raw_coefficients(clf))
    stability = slope_stability(ext, chosen_c)
    unsure = {k: [KEYS[c] for c in NUM if not stability[c][k]["sign_is_stable"]] for k, _ in FUELS}

    # ---------- model 2: burning rate ----------
    br = scope[scope["burn_rate_mm2_s"].notna()].copy()
    Xb, yb = design(br), br["burn_rate_mm2_s"].to_numpy(float)
    reg = regressor()
    r2s, maes = [], []
    for r in range(REPEATS):
        cv = KFold(5, shuffle=True, random_state=SEED + r)
        pred = cross_val_predict(reg, Xb, yb, cv=cv)
        r2s.append(r2_score(yb, pred))
        maes.append(mean_absolute_error(yb, pred))
    reg.fit(Xb, yb)
    br_parts = as_parts(*train.raw_coefficients(reg))

    metrics = {
        "tests_in_source": int(len(df)),
        "tests_in_scope": int(len(scope)),
        "extinction": {
            "rows": int(len(ext)),
            "went_out": int(ye.sum()),
            "burned_to_completion": int(len(ye) - ye.sum()),
            "cv": f"5-fold stratified, repeated {REPEATS} times; penalty strength picked inside each training fold",
            "penalty_c_grid": C_GRID,
            "penalty_c_chosen": chosen_c,
            "auc": round(float(np.mean(aucs)), 3),
            "auc_by_fuel": {k: round(float(np.mean(v)), 3) for k, v in fuel_aucs.items()},
            "accuracy": round(float(np.mean(accs)), 3),
            "accuracy_if_always_guessing_went_out": round(max(base_rate, 1 - base_rate), 3),
            "brier": round(float(np.mean(briers)), 4),
            "brier_if_always_guessing_base_rate": round(base_rate * (1 - base_rate), 4),
            "completions_found_at_50_pct": round(float(np.mean(found_at_half)), 3),
            "watch_level": WATCH,
            "completions_at_or_above_watch": round(float(np.mean(watch_found)), 3),
            "went_out_at_or_above_watch": round(float(np.mean(watch_false)), 3),
            "bootstrap_refits": BOOTSTRAPS,
            "slopes_whose_sign_is_not_stable": unsure,
        },
        "burn_rate": {
            "rows": int(len(br)),
            "cv": f"5-fold, repeated {REPEATS} times",
            "r2": round(float(np.mean(r2s)), 3),
            "mean_abs_error_mm2_s": round(float(np.mean(maes)), 3),
            "target_std_mm2_s": round(float(np.std(yb)), 3),
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_METRICS.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    # The export is the current one with the two formulas and their accuracy replaced. Ranges, sliders,
    # the nearest-test distance and the test rows do not depend on the formula, so they are kept as they are.
    model = read_base_export()
    if model["meta"].get("mock") is not False or [f["key"] for f in model["features"]] != [KEYS[c] for c in NUM]:
        raise SystemExit("model/pooled/model.js is not the base export this script expects. Run model/train.py first.")
    if model["meta"]["rows"] != len(ext) or model["meta"]["rows_burn_rate"] != len(br) or len(model["tests"]) != len(scope):
        raise SystemExit("model/pooled/model.js was built from different rows. Run model/train.py first.")
    model["meta"]["auc"] = metrics["extinction"]["auc"]
    model["meta"]["burn_rate_mae"] = metrics["burn_rate"]["mean_abs_error_mm2_s"]
    model["meta"]["watch"] = WATCH
    model["meta"]["unsure"] = unsure      # per fuel: settings whose direction the tests do not settle
    model["extinction"] = ext_parts
    model["burn_rate"] = br_parts
    OUT_JS.write_text(
        "// Generated by model/train_per_fuel.py from NASA PSI-69 FLEX. Do not edit by hand.\n"
        "window.FLAME_MODEL = " + json.dumps(model, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, indent=2))
    print("extinction:", ext_parts)
    print("burn rate: ", br_parts)
    print(f"wrote {OUT_JS.relative_to(ROOT)} ({OUT_JS.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
