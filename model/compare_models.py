"""Compare the per-fuel model with the current console model and with other candidates, on held-out tests.

Run from the repo root:  python model/compare_models.py
Needs: pandas, numpy, scikit-learn. Takes a few minutes.

Writes model/per_fuel/comparison.json and prints the tables. It changes nothing else.

Every candidate sees the same rows and the same folds (train.py's seed and repeats),
so the differences are paired: repeat by repeat, the same tests are held out for all
of them. Two ways of holding out are used:
  rows     5-fold stratified by outcome, as in model/train.py
  grouped  the same, but all tests with the same fuel and gas mix stay in one fold,
           so a test is never predicted from its own replicates
This is a comparison on the 199 (outcome) and 252 (burning rate) FLEX tests that exist.
It can show which candidate predicts held-out FLEX tests best. It cannot show how any
of them would do on a new experiment, a new fuel or a real cabin fire.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import (HistGradientBoostingClassifier, HistGradientBoostingRegressor,
                              RandomForestClassifier)
from sklearn.linear_model import LinearRegression, LogisticRegression, LogisticRegressionCV
from sklearn.metrics import brier_score_loss, log_loss, mean_absolute_error, r2_score, roc_auc_score
from sklearn.model_selection import GroupKFold, KFold, StratifiedGroupKFold, StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "model" / "per_fuel" / "comparison.json"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "model" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


train = load("train")
per_fuel = load("train_per_fuel")
NUM, SEED, REPEATS, WATCH = train.NUM, train.SEED, train.REPEATS, per_fuel.WATCH
PROPOSED = "per_fuel"
BOOTSTRAPS = 1000


def curved(df):
    """per_fuel.design plus two bends (droplet size squared, oxygen times droplet size), each also per fuel."""
    X = per_fuel.design(df)
    o2, d0, methanol = X[:, [NUM.index("o2_pct")]], X[:, [NUM.index("d0_mm")]], X[:, [len(NUM)]]
    extra = np.hstack([d0 ** 2, o2 * d0])
    return np.hstack([X, extra, extra * methanol])


def logistic(**kw):
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=20000, **kw))


# name: (what it is, design function, estimator factory)
CLASSIFIERS = {
    "current": ("Current console model: one set of slopes for both fuels, fixed penalty (model/train.py)",
                train.design, lambda: logistic(C=1.0)),
    "current_balanced": ("Current model with the rarer outcome weighted up (class_weight='balanced')",
                         train.design, lambda: logistic(C=1.0, class_weight="balanced")),
    "per_fuel_fixed": ("Per-fuel slopes, the current fixed penalty (C=1)",
                       per_fuel.design, lambda: logistic(C=1.0)),
    "per_fuel": ("PROPOSED. Per-fuel slopes, penalty picked inside the training rows (model/train_per_fuel.py)",
                 per_fuel.design, per_fuel.classifier),
    "per_fuel_curved": ("Per-fuel slopes plus two curved terms, penalty picked the same way",
                        curved, per_fuel.classifier),
    "boosting": ("Gradient-boosted trees (depth 3, 100 rounds, rate 0.05)",
                 train.design, lambda: HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.05, random_state=SEED)),
    "forest": ("Random forest (300 trees, at least 3 tests per leaf)",
               train.design, lambda: RandomForestClassifier(300, min_samples_leaf=3, random_state=SEED)),
    "base_rate": ("No model: always the share of tests that went out",
                  train.design, lambda: DummyClassifier(strategy="prior")),
}
REGRESSORS = {
    "current": ("Current console model: one set of slopes for both fuels (model/train.py)",
                train.design, lambda: make_pipeline(StandardScaler(), LinearRegression())),
    "per_fuel": ("PROPOSED. Per-fuel slopes (model/train_per_fuel.py)", per_fuel.design, per_fuel.regressor),
    "per_fuel_curved": ("Per-fuel slopes plus two curved terms", curved, per_fuel.regressor),
    "boosting": ("Gradient-boosted trees (depth 3, 200 rounds, rate 0.05)",
                 train.design, lambda: HistGradientBoostingRegressor(max_depth=3, max_iter=200, learning_rate=0.05, random_state=SEED)),
    "mean": ("No model: always the average burning rate", train.design, lambda: DummyRegressor()),
}
HIGHER_IS_BETTER = {"auc": True, "auc_heptane": True, "auc_methanol": True, "brier": False, "log_loss": False,
                    "completions_found_at_50_pct": True, "r2": True, "mean_abs_error_mm2_s": False}


def gas_mix(df):
    return df[["fuel", "o2_pct", "co2_pct", "he_pct"]].astype(str).agg("|".join, axis=1).to_numpy()


def summarise(per_repeat, primary):
    """Means over the repeats, and how often the proposed model beat each other one on the primary measures."""
    out = {}
    for name, rows in per_repeat.items():
        out[name] = {k: round(float(np.mean([r[k] for r in rows])), 4) for k in rows[0]}
    for name, rows in per_repeat.items():
        if name == PROPOSED:
            continue
        wins = {}
        for k in primary:
            mine = np.array([r[k] for r in per_repeat[PROPOSED]])
            theirs = np.array([r[k] for r in rows])
            wins[k] = int(np.sum(mine > theirs if HIGHER_IS_BETTER[k] else mine < theirs))
        out[name]["repeats_where_proposed_is_better"] = wins
    return out


def compare_outcome(ext, grouped):
    y = (ext["test_end"] == "Extinction").to_numpy(int)
    done, groups = y == 0, gas_mix(ext)
    fuel = ext["fuel"].to_numpy()
    per_repeat = {name: [] for name in CLASSIFIERS}
    for r in range(REPEATS):
        cv = (StratifiedGroupKFold if grouped else StratifiedKFold)(5, shuffle=True, random_state=SEED + r)
        splits = list(cv.split(ext, y, groups))
        for name, (_, make_x, make_model) in CLASSIFIERS.items():
            p = cross_val_predict(make_model(), make_x(ext), y, cv=splits, method="predict_proba")[:, 1]
            keep = 1 - p
            per_repeat[name].append({
                "auc": roc_auc_score(y, p),
                "auc_heptane": roc_auc_score(y[fuel == "heptane"], p[fuel == "heptane"]),
                "auc_methanol": roc_auc_score(y[fuel == "methanol"], p[fuel == "methanol"]),
                "brier": brier_score_loss(y, p),
                "log_loss": log_loss(y, np.clip(p, 1e-6, 1 - 1e-6)),
                "completions_found_at_50_pct": float(np.mean(keep[done] > 0.5)),
                "went_out_called_completion_at_50_pct": float(np.mean(keep[~done] > 0.5)),
                "completions_at_or_above_watch": float(np.mean(keep[done] >= WATCH)),
                "went_out_at_or_above_watch": float(np.mean(keep[~done] >= WATCH)),
            })
    return summarise(per_repeat, ["auc", "brier", "log_loss"])


def compare_rate(br, grouped):
    y, groups = br["burn_rate_mm2_s"].to_numpy(float), gas_mix(br)
    per_repeat = {name: [] for name in REGRESSORS}
    for r in range(REPEATS):
        cv = (GroupKFold if grouped else KFold)(5, shuffle=True, random_state=SEED + r)
        splits = list(cv.split(br, y, groups))
        for name, (_, make_x, make_model) in REGRESSORS.items():
            pred = cross_val_predict(make_model(), make_x(br), y, cv=splits)
            per_repeat[name].append({"r2": r2_score(y, pred), "mean_abs_error_mm2_s": mean_absolute_error(y, pred)})
    return summarise(per_repeat, ["r2", "mean_abs_error_mm2_s"])


def beaten_by(table, measures):
    """Every candidate that scores better than the proposed model on a measure. Empty means the proposed one is first."""
    out = {}
    for k in measures:
        mine = table[PROPOSED][k]
        out[k] = sorted(n for n, row in table.items() if n != PROPOSED and (row[k] > mine if HIGHER_IS_BETTER[k] else row[k] < mine))
    return out


def slope_stability(ext, c):
    """Refit the proposed outcome model on resampled tests: which slopes keep their sign?"""
    X, y = per_fuel.design(ext), (ext["test_end"] == "Extinction").to_numpy(int)

    def raw(Xb, yb):
        return train.raw_coefficients(logistic(C=c).fit(Xb, yb))[1]

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


def calibration(ext):
    """Held-out chance of burning all the fuel, in bands, against what the tests did. Pooled over the repeats."""
    X, y = per_fuel.design(ext), (ext["test_end"] == "Extinction").to_numpy(int)
    keep = np.array([1 - cross_val_predict(per_fuel.classifier(), X, y, method="predict_proba",
                                           cv=StratifiedKFold(5, shuffle=True, random_state=SEED + r))[:, 1]
                     for r in range(REPEATS)])
    done = np.broadcast_to(y == 0, keep.shape)
    bands = []
    for lo, hi in [(0, 0.10), (0.10, 0.20), (0.20, WATCH), (WATCH, 0.65), (0.65, 1.0001)]:
        k = (keep >= lo) & (keep < hi)
        bands.append({"from": lo, "to": min(hi, 1.0), "tests_per_repeat": round(float(k.sum() / REPEATS), 1),
                      "share_that_burned_to_completion": round(float(done[k].mean()), 3) if k.any() else None})
    return bands


def show(title, table, columns):
    print("\n" + title)
    print("  " + "candidate".ljust(18) + "".join(c[:14].rjust(15) for c in columns))
    for name, row in table.items():
        print("  " + name.ljust(18) + "".join(f"{row[c]:15.3f}" for c in columns))


def main():
    df = pd.read_csv(per_fuel.CLEAN)
    scope = per_fuel.scope_of(df)
    ext = scope[scope["test_end"].isin(["Extinction", "Completion"])].copy()
    br = scope[scope["burn_rate_mm2_s"].notna()].copy()
    chosen_c = json.loads(per_fuel.OUT_METRICS.read_text(encoding="utf-8"))["extinction"]["penalty_c_chosen"]

    outcome = {"rows": compare_outcome(ext, False), "grouped": compare_outcome(ext, True)}
    rate = {"rows": compare_rate(br, False), "grouped": compare_rate(br, True)}
    result = {
        "proposed": PROPOSED,
        "protocol": {"folds": 5, "repeats": REPEATS, "seed": SEED, "outcome_tests": int(len(ext)), "burn_rate_tests": int(len(br)),
                     "groups_fuel_and_gas_mix": int(len(set(gas_mix(ext)))), "watch_level": WATCH},
        "outcome_candidates": {k: v[0] for k, v in CLASSIFIERS.items()},
        "burn_rate_candidates": {k: v[0] for k, v in REGRESSORS.items()},
        "outcome": outcome,
        "burn_rate": rate,
        "candidates_better_than_proposed": {
            "outcome_rows": beaten_by(outcome["rows"], ["auc", "brier", "log_loss", "auc_heptane", "auc_methanol", "completions_found_at_50_pct"]),
            "outcome_grouped": beaten_by(outcome["grouped"], ["auc", "brier", "log_loss", "auc_heptane", "auc_methanol", "completions_found_at_50_pct"]),
            "burn_rate_rows": beaten_by(rate["rows"], ["r2", "mean_abs_error_mm2_s"]),
            "burn_rate_grouped": beaten_by(rate["grouped"], ["r2", "mean_abs_error_mm2_s"]),
        },
        "proposed_slope_stability": {"penalty_c": chosen_c, "bootstrap_refits": BOOTSTRAPS,
                                     "log_odds_of_going_out_per_unit": slope_stability(ext, chosen_c)},
        "proposed_calibration_held_out": calibration(ext),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    cols = ["auc", "auc_heptane", "auc_methanol", "brier", "log_loss", "completions_found_at_50_pct", "completions_at_or_above_watch", "went_out_at_or_above_watch"]
    show("Flame outcome, held out by rows", outcome["rows"], cols)
    show("Flame outcome, held out by fuel and gas mix", outcome["grouped"], cols)
    show("Burning rate, held out by rows", rate["rows"], ["r2", "mean_abs_error_mm2_s"])
    show("Burning rate, held out by fuel and gas mix", rate["grouped"], ["r2", "mean_abs_error_mm2_s"])
    print("\nCandidates that beat the proposed model, by measure (empty = none):")
    print(json.dumps(result["candidates_better_than_proposed"], indent=2))
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
