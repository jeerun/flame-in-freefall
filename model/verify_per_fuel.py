"""An independent check of the per-fuel model, made before the console was switched to it.

Run from the repo root:  python model/verify_per_fuel.py        (about a minute)
Needs: pandas, numpy, scikit-learn.

Writes model/per_fuel/independent_check.json and prints the tables. It changes nothing else.

It shares no code with model/train_per_fuel.py or model/compare_models.py, on purpose: it reads the
cleaned table, rebuilds the scope and fits its own models. It asks four things the comparison does not:

  1. Does a per-fuel model still win when it is built another way (two separate fits, one per fuel)
     and held out more strictly: one test at a time, one gas mix at a time, one test day at a time?
  2. Is the gain larger than what resampling the tests would give by chance (paired bootstrap)?
  3. Does the chosen penalty sit on a cliff, or does accuracy level off and then fall as it weakens?
  4. What do the two models give the methanol tests that burned to completion, when those are held out?

Like every number here, the answers are about the 199 FLEX tests that exist. They cannot show how a
model would do on a new experiment, a new fuel or a real cabin fire.
"""
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "model" / "per_fuel" / "independent_check.json"
NUM = ["o2_pct", "pressure_atm", "co2_pct", "he_pct", "d0_mm"]
SEED, RESAMPLES = 7, 4000
EARLIER, CONSOLE = "one slope for both fuels, C=1 (the earlier model)", "fuel-by-setting terms, C=10 (the console's model)"

df = pd.read_csv(ROOT / "data" / "clean" / "flex_clean.csv")
scope = df[df["pressure_atm"].notna() & (df["pressure_atm"] <= 1.1) & df["d0_mm"].notna()]
ext = scope[scope["test_end"].isin(["Extinction", "Completion"])].reset_index(drop=True)
y = (ext["test_end"] == "Extinction").to_numpy(int)          # 1 = the flame went out
fuel = ext["fuel"].to_numpy()
X = ext[NUM].to_numpy(float)


def logistic(c):
    return make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=20000))


def one_slope(Xtr, ytr, ftr):
    flag = lambda f: (f == "methanol").astype(float)[:, None]
    m = logistic(1.0).fit(np.hstack([Xtr, flag(ftr)]), ytr)
    return lambda Xte, fte: m.predict_proba(np.hstack([Xte, flag(fte)]))[:, 1]


def separate(c):
    """Two fits, one per fuel: the same idea as the console's model, built without interaction terms."""
    def fit(Xtr, ytr, ftr):
        models = {}
        for f in ("heptane", "methanol"):
            k = ftr == f
            models[f] = logistic(c).fit(Xtr[k], ytr[k]) if len(set(ytr[k])) > 1 else float(ytr[k].mean())

        def predict(Xte, fte):
            p = np.zeros(len(Xte))
            for f, m in models.items():
                k = fte == f
                if k.any():
                    p[k] = m if isinstance(m, float) else m.predict_proba(Xte[k])[:, 1]
            return p
        return predict
    return fit


def interaction(c):
    """One fit with a fuel flag and fuel-by-setting terms: the shape of the console's model."""
    def design(Xa, fa):
        m = (fa == "methanol").astype(float)[:, None]
        return np.hstack([Xa, m, Xa * m])

    def fit(Xtr, ytr, ftr):
        model = logistic(c).fit(design(Xtr, ftr), ytr)
        return lambda Xte, fte: model.predict_proba(design(Xte, fte))[:, 1]
    fit.design = design
    return fit


def held_out(fit, splits):
    p = np.full(len(y), np.nan)
    for tr, te in splits:
        p[te] = fit(X[tr], y[tr], fuel[tr])(X[te], fuel[te])
    return p


def score(p):
    hep, met, keep = fuel == "heptane", fuel == "methanol", 1 - p
    return {"auc": round(float(roc_auc_score(y, p)), 3), "auc_heptane": round(float(roc_auc_score(y[hep], p[hep])), 3),
            "auc_methanol": round(float(roc_auc_score(y[met], p[met])), 3), "brier": round(float(brier_score_loss(y, p)), 4),
            "log_loss": round(float(log_loss(y, np.clip(p, 1e-6, 1 - 1e-6))), 3),
            "completions_found_at_50_pct": round(float(np.mean(keep[y == 0] > 0.5)), 3),
            "went_out_called_completion_at_50_pct": round(float(np.mean(keep[y == 1] > 0.5)), 3)}


def main():
    gas = ext[["fuel", "o2_pct", "co2_pct", "he_pct"]].astype(str).agg("|".join, axis=1).to_numpy()
    day = ext["date"].astype(str).to_numpy()
    schemes = {
        "leave one test out": [(np.setdiff1d(np.arange(len(y)), [i]), np.array([i])) for i in range(len(y))],
        "leave one gas mix out": list(LeaveOneGroupOut().split(X, y, gas)),
        "leave one test day out": list(LeaveOneGroupOut().split(X, y, day)),
    }
    models = {EARLIER: one_slope, "two separate fits, C=1": separate(1.0), "two separate fits, C=10": separate(10.0), CONSOLE: interaction(10.0)}
    result = {"tests": int(len(y)), "went_out": int(y.sum()), "burned_to_completion": int((1 - y).sum()),
              "gas_mixes": int(len(set(gas))), "test_days": int(len(set(day))), "held_out": {}, "paired_bootstrap": {}}
    kept = {}
    cols = ["auc", "auc_heptane", "auc_methanol", "brier", "log_loss", "completions_found_at_50_pct", "went_out_called_completion_at_50_pct"]
    for scheme, splits in schemes.items():
        print(f"\n{scheme} ({len(splits)} folds)")
        print("  " + "model".ljust(52) + "".join(c[:9].rjust(10) for c in cols))
        result["held_out"][scheme] = {}
        for name, fit in models.items():
            p = held_out(fit, splits)
            kept[(scheme, name)] = p
            result["held_out"][scheme][name] = score(p)
            print("  " + name.ljust(52) + "".join(f"{result['held_out'][scheme][name][c]:10.3f}" for c in cols))

    # 2. the same tests resampled 4000 times, both models scored on each resample (paired)
    rng = np.random.default_rng(SEED)
    for scheme in ("leave one test out", "leave one gas mix out"):
        a, b = kept[(scheme, EARLIER)], kept[(scheme, CONSOLE)]
        gains = {"brier": [], "log_loss": [], "auc": []}
        for _ in range(RESAMPLES):
            i = rng.integers(0, len(y), len(y))
            if y[i].min() == y[i].max():
                continue
            gains["brier"].append(brier_score_loss(y[i], a[i]) - brier_score_loss(y[i], b[i]))
            gains["log_loss"].append(log_loss(y[i], np.clip(a[i], 1e-6, 1 - 1e-6)) - log_loss(y[i], np.clip(b[i], 1e-6, 1 - 1e-6)))
            gains["auc"].append(roc_auc_score(y[i], b[i]) - roc_auc_score(y[i], a[i]))
        result["paired_bootstrap"][scheme] = {
            k: {"mean_gain": round(float(np.mean(v)), 4), "p2_5": round(float(np.percentile(v, 2.5)), 4), "p97_5": round(float(np.percentile(v, 97.5)), 4),
                "share_of_resamples_where_the_console_model_is_better": round(float(np.mean(np.array(v) > 0)), 3)} for k, v in gains.items()}
        print(f"\npaired bootstrap, {scheme}: the console's model minus the earlier one (positive = better)")
        for k, v in result["paired_bootstrap"][scheme].items():
            print(f"  {k:9s} gain {v['mean_gain']:.4f} [{v['p2_5']:.4f}, {v['p97_5']:.4f}], better in {100 * v['share_of_resamples_where_the_console_model_is_better']:.1f} % of resamples")

    # 3. the penalty: held out one gas mix at a time, from a strong penalty to almost none
    design = interaction(1.0).design
    result["penalty"] = []
    print("\npenalty strength (larger C = weaker penalty), leave one gas mix out")
    for c in [0.3, 1, 3, 10, 30, 100, 1000]:
        s = score(held_out(interaction(float(c)), schemes["leave one gas mix out"]))
        fitted = logistic(float(c)).fit(design(X, fuel), y).predict_proba(design(X, fuel))[:, 1]
        row = {"C": c, "auc": s["auc"], "brier": s["brier"], "log_loss": s["log_loss"],
               "fitted_chances_below_1_or_above_99_pct": int(np.sum((fitted > 0.99) | (fitted < 0.01)))}
        result["penalty"].append(row)
        print(f"  C={c:<6} auc {row['auc']:.3f}  brier {row['brier']:.4f}  log loss {row['log_loss']:.3f}  fitted chances below 1 % or above 99 %: {row['fitted_chances_below_1_or_above_99_pct']} of {len(y)}")

    # 4. the methanol tests that burned to completion, each held out together with its whole gas mix
    a, b = kept[("leave one gas mix out", EARLIER)], kept[("leave one gas mix out", CONSOLE)]
    result["methanol_completions_held_out"] = []
    print("\nmethanol tests that burned to completion: chance of burning all the fuel when held out with their gas mix")
    for i in np.where((fuel == "methanol") & (y == 0))[0]:
        r = ext.iloc[i]
        row = {"test": int(r.test), "o2_pct": float(r.o2_pct), "pressure_atm": round(float(r.pressure_atm), 2), "co2_pct": float(r.co2_pct), "d0_mm": float(r.d0_mm),
               "earlier_model_pct": round(float(100 * (1 - a[i])), 1), "console_model_pct": round(float(100 * (1 - b[i])), 1)}
        result["methanol_completions_held_out"].append(row)
        print(f"  test {row['test']:3d}: O2 {row['o2_pct']:4.1f} %, {row['pressure_atm']:.2f} atm, CO2 {row['co2_pct']:4.1f} %, {row['d0_mm']:.2f} mm | earlier {row['earlier_model_pct']:5.1f} %, console {row['console_model_pct']:5.1f} %")

    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
