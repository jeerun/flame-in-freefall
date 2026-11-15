"""Train the two console models on the cleaned FLEX table and export console/model.js.

Run from the repo root:  python model/train.py
Needs: pandas, numpy, scikit-learn.

Model 1  logistic regression: does the flame go out before the fuel is gone?
         (test_end "Extinction" = 1, "Completion" = 0, "Disruption" left out)
Model 2  linear regression: burning-rate constant K in mm^2/s.

Inputs are only things known before ignition: fuel, oxygen, pressure,
carbon dioxide, helium, initial droplet diameter.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import brier_score_loss, mean_absolute_error, r2_score, roc_auc_score
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean" / "flex_clean.csv"
OUT_JS = ROOT / "console" / "model.js"
OUT_METRICS = ROOT / "model" / "metrics.json"

NUM = ["o2_pct", "pressure_atm", "co2_pct", "he_pct", "d0_mm"]
KEYS = {"o2_pct": "o2", "pressure_atm": "p", "co2_pct": "co2", "he_pct": "he", "d0_mm": "d0"}
FUELS = [("heptane", "Heptane"), ("methanol", "Methanol")]
MAX_PRESSURE_ATM = 1.1   # see "Scope" in model/README.md
SEED = 7
REPEATS = 20


def design(df):
    X = df[NUM].to_numpy(float)
    methanol = (df["fuel"] == "methanol").to_numpy(float)[:, None]
    return np.hstack([X, methanol])


def raw_coefficients(pipe):
    """Undo the standardisation so coefficients apply to raw values."""
    scaler, est = pipe.steps[0][1], pipe.steps[1][1]
    coef = np.ravel(est.coef_) / scaler.scale_
    intercept = float(np.ravel(est.intercept_)[0] - np.sum(coef * scaler.mean_))
    return intercept, coef


def as_parts(intercept, coef):
    return {
        "intercept": round(intercept, 6),
        "fuel": {"heptane": 0, "methanol": round(float(coef[-1]), 6)},
        "coef": {KEYS[c]: round(float(v), 6) for c, v in zip(NUM, coef[:-1])},
    }


def main():
    df = pd.read_csv(CLEAN)
    n_all = len(df)

    scope = df[df["pressure_atm"].notna() & (df["pressure_atm"] <= MAX_PRESSURE_ATM) & df["d0_mm"].notna()].copy()

    # ---------- model 1: extinction ----------
    ext = scope[scope["test_end"].isin(["Extinction", "Completion"])].copy()
    Xe, ye = design(ext), (ext["test_end"] == "Extinction").to_numpy(int)
    clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))

    aucs, briers, accs = [], [], []
    for r in range(REPEATS):
        cv = StratifiedKFold(5, shuffle=True, random_state=SEED + r)
        p = cross_val_predict(clf, Xe, ye, cv=cv, method="predict_proba")[:, 1]
        aucs.append(roc_auc_score(ye, p))
        briers.append(brier_score_loss(ye, p))
        accs.append(np.mean((p >= 0.5) == ye))
    base_rate = float(ye.mean())
    clf.fit(Xe, ye)
    ext_parts = as_parts(*raw_coefficients(clf))

    # ---------- model 2: burning rate ----------
    br = scope[scope["burn_rate_mm2_s"].notna()].copy()
    Xb, yb = design(br), br["burn_rate_mm2_s"].to_numpy(float)
    reg = make_pipeline(StandardScaler(), LinearRegression())
    r2s, maes = [], []
    for r in range(REPEATS):
        cv = KFold(5, shuffle=True, random_state=SEED + r)
        pred = cross_val_predict(reg, Xb, yb, cv=cv)
        r2s.append(r2_score(yb, pred))
        maes.append(mean_absolute_error(yb, pred))
    reg.fit(Xb, yb)
    br_parts = as_parts(*raw_coefficients(reg))

    # ---------- ranges, nearest-test table ----------
    lo, hi = scope[NUM].min(), scope[NUM].max()
    span = (hi - lo).to_numpy(float)

    def nn_dist(frame):
        """Leave-one-out distance to the nearest same-fuel test, range-normalised."""
        out = []
        for fuel, g in frame.groupby("fuel"):
            Z = (g[NUM].to_numpy(float) - lo.to_numpy(float)) / span
            D = np.sqrt(((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1))
            np.fill_diagonal(D, np.inf)
            out.extend(D.min(1))
        return np.array(out)

    far = float(np.quantile(nn_dist(scope), 0.95))

    slider = {  # key: (min, max, step, digits, default, label, unit)
        "o2":  (8, 40, 0.5, 1, 21, "Oxygen", "%"),
        "p":   (0.5, 1.5, 0.01, 2, 1.0, "Pressure", "atm"),
        "co2": (0, 60, 1, 0, 0, "Carbon dioxide", "%"),
        "he":  (0, 55, 1, 0, 0, "Helium", "%"),
        "d0":  (0.5, 5.5, 0.1, 1, 3.0, "Droplet diameter", "mm"),
    }
    features = []
    for col in NUM:
        k = KEYS[col]
        mn, mx, step, digits, default, label, unit = slider[k]
        features.append({
            "key": k, "label": label, "unit": unit, "min": mn, "max": mx, "step": step,
            "digits": digits, "default": default,
            "data_min": round(float(lo[col]), 3), "data_max": round(float(hi[col]), 3),
        })

    tests = [
        [int(t.test), t.flex_id, t.fuel, t.o2_pct, round(t.pressure_atm, 3), t.co2_pct, t.he_pct, t.d0_mm,
         t.test_end, None if pd.isna(t.burn_rate_mm2_s) else t.burn_rate_mm2_s]
        for t in scope.itertuples()
    ]

    metrics = {
        "tests_in_source": n_all,
        "tests_in_scope": int(len(scope)),
        "extinction": {
            "rows": int(len(ext)),
            "went_out": int(ye.sum()),
            "burned_to_completion": int(len(ye) - ye.sum()),
            "cv": f"5-fold stratified, repeated {REPEATS} times",
            "auc": round(float(np.mean(aucs)), 3),
            "accuracy": round(float(np.mean(accs)), 3),
            "accuracy_if_always_guessing_went_out": round(max(base_rate, 1 - base_rate), 3),
            "brier": round(float(np.mean(briers)), 4),
            "brier_if_always_guessing_base_rate": round(base_rate * (1 - base_rate), 4),
        },
        "burn_rate": {
            "rows": int(len(br)),
            "cv": f"5-fold, repeated {REPEATS} times",
            "r2": round(float(np.mean(r2s)), 3),
            "mean_abs_error_mm2_s": round(float(np.mean(maes)), 3),
            "target_std_mm2_s": round(float(np.std(yb)), 3),
        },
    }
    OUT_METRICS.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    model = {
        "meta": {
            "mock": False,
            "source": "NASA PSI-69 FLEX",
            "rows": int(len(ext)),
            "rows_burn_rate": int(len(br)),
            "auc": metrics["extinction"]["auc"],
            "burn_rate_mae": metrics["burn_rate"]["mean_abs_error_mm2_s"],
            "far_distance": round(far, 3),
            "exclusive": [["co2", "he"]],
        },
        "fuels": [{"key": k, "label": l} for k, l in FUELS],
        "features": features,
        "extinction": ext_parts,
        "burn_rate": br_parts,
        "tests": tests,
    }
    OUT_JS.write_text(
        "// Generated by model/train.py from NASA PSI-69 FLEX. Do not edit by hand.\n"
        "window.FLAME_MODEL = " + json.dumps(model, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, indent=2))
    print("extinction:", ext_parts)
    print("burn rate: ", br_parts)
    print("far distance (95th pct nearest-test):", round(far, 3))
    print(f"wrote {OUT_JS.relative_to(ROOT)} ({OUT_JS.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
