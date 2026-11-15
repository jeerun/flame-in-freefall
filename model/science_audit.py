"""Independent scientific validation audit for NASA FLEX / Team Second Toe.

Run from the REPOSITORY ROOT (not inside model/):

    py model/science_audit.py
    py model/science_audit.py --repeats 10 --check-pressure 0.85

If experimental/run identifiers are available, explicitly opt in to grouped CV:

    py model/science_audit.py --group-col run_id --repeats 5

Outputs (under --output-dir, default model/):
    science_audit_report.json   Detailed results + limitations
    calibration_bins.csv       Reliability bins from the first CV seed
    cv_seeds_metrics.csv       Per-seed metrics including per-fuel class metrics
    science_audit_summary.md   Short review-ready summary for teammates

IMPORTANT: This audit REFITS a separate model on the cleaned data. It does not
validate the deployed console model, change train.py or console files, create a
spacecraft safety classifier, or establish certified OOD thresholds.

Dependencies: numpy, pandas, scikit-learn.
"""
from __future__ import annotations

import argparse
import json
import math
import hashlib
import platform
import sklearn
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    GroupKFold,
    KFold,
    StratifiedGroupKFold,
    StratifiedKFold,
    cross_val_predict,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["o2_pct", "pressure_atm", "co2_pct", "he_pct", "d0_mm"]
REQUIRED = FEATURES + ["fuel", "test_end", "burn_rate_mm2_s"]
FUEL_TYPES = ("heptane", "methanol")
LABELS = {0: "completion", 1: "extinction"}


def finite_num(value: float | int | None, digits: int = 5) -> float | None:
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    return round(v, digits) if math.isfinite(v) else None


def load_scope(csv_path: Path, group_col: str | None) -> tuple[pd.DataFrame, dict, list[str]]:
    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Missing cleaned FLEX dataset: {csv_path}. Use --data PATH."
        )
    df = pd.read_csv(csv_path)
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError(
            f"Cleaned FLEX CSV schema does not match. Missing: {missing}; "
            f"available columns: {list(df.columns)}"
        )
    if group_col is not None and group_col not in df.columns:
        raise ValueError(
            f"--group-col '{group_col}' does not exist. Available columns: {list(df.columns)}"
        )
    df["fuel"] = df["fuel"].astype("string").str.strip().str.lower()
    df["test_end"] = df["test_end"].astype("string").str.strip().str.lower()
    for col in FEATURES + ["burn_rate_mm2_s"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)

    # Match the independent v1 audit scope so prior values remain comparable.
    valid = (
        df["fuel"].isin(FUEL_TYPES)
        & df[FEATURES].notna().all(axis=1)
        & df["pressure_atm"].between(0, 1.1, inclusive="right")
        & df["d0_mm"].gt(0)
        & df["o2_pct"].between(0, 100)
        & df["co2_pct"].between(0, 100)
        & df["he_pct"].between(0, 100)
    )
    scope = df.loc[valid].copy()
    if scope.empty:
        raise ValueError("No rows remain after FLEX scope and feature checks.")
    if group_col is not None:
        if scope[group_col].isna().any() or scope[group_col].astype(str).str.strip().eq("").any():
            raise ValueError(
                f"Column '{group_col}' has missing/blank group IDs in usable rows. "
                "Fix the source IDs first; do not silently assign groups."
            )

    candidate_names = [
        col for col in df.columns
        if ("run" in col.lower() or "experiment" in col.lower() or "trial" in col.lower())
        and col not in REQUIRED
    ]
    counts = {
        "raw_rows": int(len(df)),
        "usable_feature_rows": int(len(scope)),
        "excluded_rows": int((~valid).sum()),
        "classification_rows": int(scope["test_end"].isin(["extinction", "completion"]).sum()),
        "regression_rows": int(scope["burn_rate_mm2_s"].notna().sum()),
        "feature_rows_with_gas_total_over_100_pct": int(
            (scope[["o2_pct", "co2_pct", "he_pct"]].sum(axis=1) > 100 + 1e-8).sum()
        ),
    }
    return scope, counts, candidate_names


def design(frame: pd.DataFrame) -> np.ndarray:
    x = frame[FEATURES].to_numpy(dtype=float)
    is_methanol = frame["fuel"].eq("methanol").to_numpy(dtype=float).reshape(-1, 1)
    return np.column_stack([x, is_methanol])


def class_metrics(y: np.ndarray, prob: np.ndarray) -> dict:
    """Per-class diagnostics at 0.5; order is completion=0, extinction=1."""
    y = np.asarray(y, dtype=int)
    p = np.asarray(prob, dtype=float)
    pred = (p >= 0.5).astype(int)
    counts = confusion_matrix(y, pred, labels=[0, 1]).astype(int)
    answer = {
        "n": int(len(y)),
        "completion_n": int(np.sum(y == 0)),
        "extinction_n": int(np.sum(y == 1)),
        "extinction_fraction": finite_num(np.mean(y)),
        "mean_predicted_extinction": finite_num(np.mean(p)),
        "brier_score": finite_num(brier_score_loss(y, p)),
        "constant_prevalence_baseline_brier": finite_num(
            brier_score_loss(y, np.full(len(y), np.mean(y)))
        ),
        "accuracy_at_0_5": finite_num(np.mean(y == pred)),
        "majority_class_baseline_accuracy": finite_num(max(np.mean(y), 1 - np.mean(y))),
        "confusion_matrix_rows_actual_completion_extinction": counts.tolist(),
        "balanced_accuracy_at_0_5": (
            finite_num(balanced_accuracy_score(y, pred))
            if np.unique(y).size == 2 else None
        ),
        "roc_auc": finite_num(roc_auc_score(y, p)) if np.unique(y).size == 2 else None,
        "macro_f1_at_0_5": finite_num(f1_score(y, pred, labels=[0, 1], average="macro", zero_division=0)),
        "per_class_at_0_5": {},
        "completion_misclassified_as_extinction_n": int(counts[0, 1]),
        "completion_misclassified_as_extinction_fraction": (
            finite_num(counts[0, 1] / counts[0].sum()) if counts[0].sum() else None
        ),
    }
    for cls in (0, 1):
        name = LABELS[cls]
        answer["per_class_at_0_5"][name] = {
            "support": int(np.sum(y == cls)),
            "predicted_count": int(np.sum(pred == cls)),
            "precision_undefined_no_predictions": bool(np.sum(pred == cls) == 0),
            "recall_undefined_no_actual_cases": bool(np.sum(y == cls) == 0),
            "precision": finite_num(precision_score(y, pred, pos_label=cls, zero_division=0)),
            "recall": finite_num(recall_score(y, pred, pos_label=cls, zero_division=0)),
            "f1": finite_num(f1_score(y, pred, pos_label=cls, zero_division=0)),
        }
        if not np.any(y == cls):
            answer["per_class_at_0_5"][name]["recall"] = None
    return answer


def cal_bins(y: np.ndarray, prob: np.ndarray, fuel: str) -> list[dict]:
    df = pd.DataFrame({"actual": y, "predicted": prob})
    if len(df) < 2 or df["predicted"].nunique() < 2:
        return []
    n_bins = min(5, len(df), int(df["predicted"].nunique()))
    df["bin"] = pd.qcut(df["predicted"], q=n_bins, duplicates="drop")
    result = []
    for iv, g in df.groupby("bin", observed=True):
        mean_pred = float(g["predicted"].mean())
        mean_actual = float(g["actual"].mean())
        result.append({
            "fuel": fuel,
            "predicted_probability_bin": str(iv),
            "n": int(len(g)),
            "mean_predicted_extinction": finite_num(mean_pred),
            "observed_extinction_fraction": finite_num(mean_actual),
            "absolute_calibration_gap": finite_num(abs(mean_pred - mean_actual)),
        })
    return result


def make_cv(y: np.ndarray, groups: np.ndarray | None, folds: int, seed: int):
    counts = np.bincount(y, minlength=2)
    if counts.min() < 2:
        raise ValueError("Need at least two Extinction and Completion rows to cross-validate.")
    n_splits = min(folds, int(counts.min()))
    if groups is None:
        splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        return list(splitter.split(np.empty(len(y)), y)), n_splits

    unique_groups = np.unique(groups)
    group_support = [np.unique(groups[y == c]).size for c in (0, 1)]
    n_splits = min(n_splits, len(unique_groups), *group_support)
    if n_splits < 2:
        raise ValueError(
            "Grouping impossible: each target class must occur in at least two "
            "distinct experimental groups. Use a valid --group-col or report limitation."
        )
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    splits = list(splitter.split(np.zeros(len(y)), y, groups))
    for train, test in splits:
        if np.unique(y[train]).size < 2 or len(test) == 0:
            raise ValueError(
                f"Grouped CV seed={seed} contains a fold without both labels in training "
                "or with empty test data. Group labels may be too sparse; avoid "
                "reporting this run as a valid evaluation."
            )
        if not set(groups[train]).isdisjoint(set(groups[test])):
            raise RuntimeError("Data leakage: a group appears in both train and test.")
    return splits, n_splits


def pressure_coverage(frame: pd.DataFrame, gap_min: float, query_pressures: list[float]) -> dict:
    """Pressure-only evidence descriptions, explicitly NOT a full-feature OOD classifier."""
    result = {}
    low = frame[FEATURES].min().to_numpy(float)
    span = (frame[FEATURES].max() - frame[FEATURES].min()).to_numpy(float)
    span = np.where(span == 0, 1.0, span)
    for fuel, g in frame.groupby("fuel", sort=True):
        # Rounding to 2 dp is for the PRESSURE coverage display (as in v1).
        levels = sorted(float(q) for q in g["pressure_atm"].unique())
        level_counts = g["pressure_atm"].round(2).value_counts().sort_index()
        gaps = []
        for left, right in zip(levels, levels[1:]):
            if right - left >= gap_min - 1e-10:
                gaps.append({
                    "between_pressure_atm": [float(left), float(right)],
                    "gap_width_atm": finite_num(right - left),
                    "note": "No observed pressure strictly inside this interval; raw values used.",
                })
        checks = []
        for pressure in query_pressures:
            nearest = min(levels, key=lambda x: abs(x - pressure))
            if pressure < levels[0] or pressure > levels[-1]:
                status = "outside_observed_pressure_range"
                interval = None
            else:
                interval = next(
                    ([left, right] for left, right in zip(levels, levels[1:])
                     if left < pressure < right and right - left >= gap_min - 1e-10),
                    None,
                )
                status = (
                    "within_large_internal_pressure_gap" if interval is not None
                    else "pressure_near_observed_level_or_small_gap"
                )
            checks.append({
                "pressure_atm": finite_num(pressure),
                "pressure_coverage_status": status,
                "nearest_observed_pressure_atm": float(nearest),
                "distance_to_nearest_pressure_atm": finite_num(abs(nearest - pressure)),
                "pressure_evidence_level": (
                    "Unsupported" if status == "outside_observed_pressure_range"
                    else "Limited Evidence" if interval is not None else "Not assessed"
                ),
                "large_internal_gap_bounds_atm": interval,
                "warning": "Pressure-only screen; does not establish joint-feature support or safety.",
            })
        # Keep the v1 same-fuel leave-one-out normalized proximity summary.
        z = (g[FEATURES].to_numpy(float) - low) / span
        n = len(z)
        nn95 = None
        nnmax = None
        dupe_fraction = None
        if n > 1:
            d = np.sqrt(((z[:, None, :] - z[None, :, :]) ** 2).sum(axis=2))
            np.fill_diagonal(d, np.inf)
            nearest_dist = d.min(axis=1)
            nn95 = finite_num(np.quantile(nearest_dist, .95))
            nnmax = finite_num(nearest_dist.max())
            dupe_fraction = finite_num(np.mean(nearest_dist == 0))
        result[str(fuel)] = {
            "n": int(n),
            "observed_pressure_atm_rounded_2dp": {
                f"{float(p):.2f}": int(k) for p, k in level_counts.items()
            },
            "observed_pressure_levels_atm": levels,
            "pressure_gap_screening_min_atm": finite_num(gap_min),
            "large_internal_pressure_gaps": gaps,
            "example_pressure_checks": checks,
            "min_max_by_feature": {
                col: {"min": finite_num(g[col].min()), "max": finite_num(g[col].max())}
                for col in FEATURES
            },
            "distance_method": "same-fuel leave-one-out Euclidean / global feature range",
            "nearest_neighbor_distance_p95": nn95,
            "nearest_neighbor_distance_max": nnmax,
            "exact_duplicate_neighbor_fraction": dupe_fraction,
        }
    return result


def aggregate_repeat_metrics(rows: list[dict]) -> dict:
    result = {}
    for subset in sorted(set(row["fuel"] for row in rows)):
        selected = [row for row in rows if row["fuel"] == subset]
        result[subset] = {"repeats": len(selected)}
        for field in (
            "accuracy_at_0_5", "balanced_accuracy_at_0_5", "roc_auc", "brier_score",
            "completion_recall_at_0_5", "completion_precision_at_0_5", "completion_f1_at_0_5",
            "extinction_recall_at_0_5", "extinction_precision_at_0_5", "extinction_f1_at_0_5",
        ):
            values = np.asarray([r[field] for r in selected if r[field] is not None], dtype=float)
            result[subset][field] = {
                "mean": finite_num(np.mean(values)) if len(values) else None,
                "min": finite_num(np.min(values)) if len(values) else None,
                "max": finite_num(np.max(values)) if len(values) else None,
                "sd_across_seeds": finite_num(np.std(values, ddof=1)) if len(values) > 1 else None,
            }
    return result


def seed_row(seed: int, fuel: str, metrics: dict) -> dict:
    return {
        "seed": seed,
        "fuel": fuel,
        "n": metrics["n"],
        "completion_n": metrics["completion_n"],
        "extinction_n": metrics["extinction_n"],
        "accuracy_at_0_5": metrics["accuracy_at_0_5"],
        "balanced_accuracy_at_0_5": metrics["balanced_accuracy_at_0_5"],
        "roc_auc": metrics["roc_auc"],
        "brier_score": metrics["brier_score"],
        "completion_precision_at_0_5": metrics["per_class_at_0_5"]["completion"]["precision"],
        "completion_recall_at_0_5": metrics["per_class_at_0_5"]["completion"]["recall"],
        "completion_f1_at_0_5": metrics["per_class_at_0_5"]["completion"]["f1"],
        "extinction_precision_at_0_5": metrics["per_class_at_0_5"]["extinction"]["precision"],
        "extinction_recall_at_0_5": metrics["per_class_at_0_5"]["extinction"]["recall"],
        "extinction_f1_at_0_5": metrics["per_class_at_0_5"]["extinction"]["f1"],
    }


def fmt(x: float | None, places: int = 3) -> str:
    return "N/A" if x is None else f"{x:.{places}f}"


def markdown_summary(report: dict) -> str:
    overall = report["classification_overall"]
    rows = [
        "# Second Toe — Scientific Validation Audit (Independent Model)",
        "",
        "> **Scope:** This document audits a separately fitted model. It does **not** certify the saved console model, spacecraft safety, or live operational fire risk.",
        "",
        "## Evaluation", "",
        f"- Data: {report['counts']['raw_rows']} raw rows; {report['counts']['usable_feature_rows']} feature-valid rows; "
        f"{report['counts']['classification_rows']} labelled classification rows.",
        f"- Method: {report['validation']['method']} ({report['validation']['n_folds']} folds), "
        f"{len(report['validation']['seeds'])} seeds; group field: {report['validation']['group_column'] or 'none (row CV)' }.",
        f"- First-seed classification: accuracy {fmt(overall['accuracy_at_0_5'])}, "
        f"balanced accuracy {fmt(overall['balanced_accuracy_at_0_5'])}, "
        f"ROC-AUC {fmt(overall['roc_auc'])}, Brier {fmt(overall['brier_score'], 4)}.",
        f"- Majority-class accuracy baseline {fmt(overall['majority_class_baseline_accuracy'])}; "
        f"descriptive constant-prevalence Brier reference {fmt(overall['constant_prevalence_baseline_brier'],4)}.",
        "", report["baseline_note"], "", "## Fuel-specific classification (first seed, threshold 0.5)", "",
        "| Fuel | n | Completion n | Completion precision | Completion recall | Completion F1 | Extinction recall | ROC-AUC |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for fuel, metric in report["classification_by_fuel"].items():
        c, e = metric["per_class_at_0_5"]["completion"], metric["per_class_at_0_5"]["extinction"]
        rows.append(
            f"| {fuel} | {metric['n']} | {c['support']} | {fmt(c['precision'])} | "
            f"{fmt(c['recall'])} | {fmt(c['f1'])} | {fmt(e['recall'])} | {fmt(metric['roc_auc'])} |"
        )
    rows.extend(["", "## Pressure evidence gaps (raw input pressures)", ""])
    gap_found = False
    for fuel, e in report["evidence_coverage_by_fuel"].items():
        for gap in e["large_internal_pressure_gaps"]:
            gap_found = True
            a, b = gap["between_pressure_atm"]
            rows.append(f"- **{fuel}:** no observed pressure strictly between {a:.5g} and {b:.5g} atm "
                        f"(gap {gap['gap_width_atm']:.2f} atm).")
    if not gap_found:
        rows.append("- None exceeded the configured descriptive gap threshold.")
    rows.extend([
        "", "Pressure gaps indicate sparse **pressure-only** evidence, not a validated multivariate out-of-distribution classifier.",
        "", "## Interpretation and next checks", "",
        "1. Review the completion recall and its small class support, not accuracy alone.",
        "2. Inspect `calibration_bins.csv`; do not interpret equal-count bin gaps as probability guarantees.",
        "3. Compare multiple CV seeds in `cv_seeds_metrics.csv`; seed variation is not an independent test set.",
        "4. If genuine experiment/run IDs exist, rerun with `--group-col COLUMN` to reduce replicate leakage.",
        "5. Compare dataset filtering, target definitions, and features with the **deployed** console model before making UI claims.",
        "6. State that visible droplet-flame extinction is not complete combustion termination or verified cabin fire safety.",
        "", "## Limitations", "",
    ])
    rows.extend(f"- {item}" for item in report["limitations"])
    rows.append("")
    return "\n".join(rows)


def run_audit(
    data_path: Path, output_dir: Path, seed: int, repeats: int,
    folds: int, group_col: str | None, pressure_gap_min_atm: float,
    check_pressures: list[float],
) -> tuple[Path, Path, Path, Path]:
    if repeats < 1 or repeats > 100:
        raise ValueError("--repeats must be between 1 and 100.")
    if folds < 2:
        raise ValueError("--folds must be at least 2.")
    if not math.isfinite(pressure_gap_min_atm) or pressure_gap_min_atm <= 0:
        raise ValueError("--pressure-gap-min-atm must be > 0.")
    if any(not math.isfinite(x) or x <= 0 for x in check_pressures):
        raise ValueError("--check-pressure values must be positive finite numbers.")

    scope, counts, potential_group_cols = load_scope(data_path, group_col)
    labeled = scope[scope["test_end"].isin(["extinction", "completion"])].copy()
    if labeled.empty:
        raise ValueError("No Extinction/Completion rows in cleaned dataset.")
    y = labeled["test_end"].eq("extinction").to_numpy(dtype=int)
    x = design(labeled)
    groups = labeled[group_col].to_numpy() if group_col else None
    seeds = [int(seed + i * 11) for i in range(repeats)]
    rows = []
    baseline_rows = []
    first_p = None
    n_folds = None
    for k in seeds:
        cv, n_folds_this = make_cv(y, groups, folds, k)
        n_folds = n_folds_this
        classifier = make_pipeline(
            StandardScaler(), LogisticRegression(C=1.0, max_iter=2000)
        )
        p = cross_val_predict(classifier, x, y, cv=cv, method="predict_proba")[:, 1]
        baseline_p = np.empty(len(y), dtype=float)
        for train, test in cv:
            baseline_p[test] = y[train].mean()
        for fuel in ("ALL", *FUEL_TYPES):
            mask = np.ones(len(y), dtype=bool) if fuel == "ALL" else labeled["fuel"].eq(fuel).to_numpy(dtype=bool)
            if mask.any():
                baseline_rows.append({
                    "seed": k, "fuel": fuel,
                    "brier_score": finite_num(brier_score_loss(y[mask], baseline_p[mask])),
                    "accuracy": finite_num(np.mean(y[mask] == (baseline_p[mask] >= .5))),
                })
        if first_p is None:
            first_p = p
        metrics = class_metrics(y, p)
        rows.append(seed_row(k, "ALL", metrics))
        for fuel in FUEL_TYPES:
            mask = labeled["fuel"].eq(fuel).to_numpy(dtype=bool)
            if mask.any():
                rows.append(seed_row(k, fuel, class_metrics(y[mask], p[mask])))

    assert first_p is not None
    try:
        # Keep portable report paths and avoid leaking Windows usernames in PRs.
        recorded_data_path = data_path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        recorded_data_path = "[external dataset path omitted for privacy]"
    report = {
        "schema_version": "2.1",
        "provenance": {
            "dataset_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "python": platform.python_version(), "numpy": np.__version__,
            "pandas": pd.__version__, "scikit_learn": sklearn.__version__,
        },
        "fold_training_prevalence_baselines": baseline_rows,
        "baseline_note": "Fold baselines use only training labels (pooled fuels). Existing constant-prevalence and majority-class metrics are descriptive full-subset references, not held-out baselines.",
        "data_path": recorded_data_path,
        "label_definition": "1 = visible droplet-flame extinction; 0 = completion",
        "model_for_audit": "StandardScaler + LogisticRegression(C=1.0; max_iter=2000)",
        "validation": {
            "method": "stratified GROUP cross-validation" if group_col else "stratified row cross-validation",
            "n_folds": n_folds,
            "seeds": seeds,
            "group_column": group_col,
            "candidate_group_columns_not_verified": potential_group_cols,
            "note": "Repeated seed results vary the splits of the same dataset; they are not external validation.",
        },
        "counts": counts,
        "classification_overall": class_metrics(y, first_p),
        "classification_by_fuel": {},
        "classification_repeated_seed_summary": aggregate_repeat_metrics(rows),
        "evidence_coverage_by_fuel": pressure_coverage(scope, pressure_gap_min_atm, check_pressures),
        "burn_rate_regression": None,
        "limitations": [
            "Independent audit refit; not evaluation of saved deployed model files or console output.",
            "Compare FEATURES, dataset filters, and hyperparameters with current model/train.py before claiming identical methodology.",
            "Data reused over CV seeds; seed variation is not an independent validation set or confidence interval.",
            "Grouped splitting is only used when --group-col is provided with genuine experiment/run IDs. Otherwise correlated replicates could inflate scores.",
            "Probability bins and fuel-specific class metrics can be highly unstable with few Completion cases.",
            "When a class is never predicted, its precision is mathematically undefined; scikit-learn zero_division=0 reports it as 0, with a separate flag.",
            "No threshold calibration or probability adjustment has been deployed or validated.",
            "Pressure gap threshold is an illustrative audit screen on raw pressure values, not a certified physical OOD boundary. Rounded histograms are display-only.",
            "Nearest-neighbor distances describe training-data coverage, not calibrated model confidence.",
            "Visible droplet-flame extinction is not evidence of complete combustion termination or spacecraft cabin fire safety.",
        ],
    }
    bins = cal_bins(y, first_p, "ALL")
    for fuel in FUEL_TYPES:
        mask = labeled["fuel"].eq(fuel).to_numpy(dtype=bool)
        if not mask.any():
            continue
        ym, pm = y[mask], first_p[mask]
        metric = class_metrics(ym, pm)
        report["classification_by_fuel"][fuel] = metric
        bins.extend(cal_bins(ym, pm, fuel))
        if metric["completion_n"] < 10:
            report["limitations"].append(
                f"{fuel}: only {metric['completion_n']} labelled Completion cases; estimates are fragile."
            )

    rate = scope.loc[scope["burn_rate_mm2_s"].notna()].copy()
    if len(rate) >= 3:
        target = rate["burn_rate_mm2_s"].to_numpy(dtype=float)
        n_splits_reg = min(folds, len(rate))
        if group_col:
            rgroups = rate[group_col].to_numpy()
            n_splits_reg = min(n_splits_reg, len(np.unique(rgroups)))
            if n_splits_reg < 2:
                raise ValueError("Not enough independent groups to cross-validate burn-rate regression.")
            cv_reg = GroupKFold(n_splits=n_splits_reg)
            splits_reg = list(cv_reg.split(design(rate), target, rgroups))
        else:
            cv_reg = KFold(n_splits=n_splits_reg, shuffle=True, random_state=seed)
            splits_reg = list(cv_reg.split(design(rate)))
        reg = make_pipeline(StandardScaler(), LinearRegression())
        predicted = cross_val_predict(reg, design(rate), target, cv=splits_reg)
        report["burn_rate_regression"] = {
            "n": len(rate),
            "out_of_fold_mae_mm2_s": finite_num(mean_absolute_error(target, predicted)),
            "out_of_fold_r2": finite_num(r2_score(target, predicted)),
            "negative_predictions_before_any_ui_clamp": int(np.sum(predicted < 0)),
            "negative_observed_targets": int(np.sum(target < 0)),
            "grouped_cv": bool(group_col),
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    jpath = output_dir / "science_audit_report.json"
    bpath = output_dir / "calibration_bins.csv"
    spath = output_dir / "cv_seeds_metrics.csv"
    mpath = output_dir / "science_audit_summary.md"
    jpath.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    pd.DataFrame(bins, columns=[
        "fuel", "predicted_probability_bin", "n", "mean_predicted_extinction",
        "observed_extinction_fraction", "absolute_calibration_gap",
    ]).to_csv(bpath, index=False)
    pd.DataFrame(rows).to_csv(spath, index=False)
    mpath.write_text(markdown_summary(report), encoding="utf-8")
    print("Scientific audit V2.1 completed. No existing train.py/console files were changed.")
    print(f"Data: {counts['raw_rows']} total, {counts['usable_feature_rows']} in feature scope; "
          f"classification: {len(labeled)}, regression: {counts['regression_rows']}")
    print(f"Validation: {n_folds}-fold CV x {repeats} seeds, group column: {group_col or 'NONE'}")
    a = report["classification_overall"]
    print(f"First seed: accuracy={a['accuracy_at_0_5']}, "
          f"balanced accuracy={a['balanced_accuracy_at_0_5']}, "
          f"AUC={a['roc_auc']}, Brier={a['brier_score']}")
    for fuel, info in report["classification_by_fuel"].items():
        c = info["per_class_at_0_5"]["completion"]
        print(f"  {fuel}: completion n={c['support']}, recall={c['recall']}, "
              f"precision={c['precision']}, F1={c['f1']}")
    for out in (jpath, bpath, spath, mpath):
        print(f"Created: {out}")
    print("WARNING: independent diagnostic audit only; no operational fire-safety certification.")
    return jpath, bpath, spath, mpath


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", type=Path, default=ROOT / "data/clean/flex_clean.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "model")
    parser.add_argument("--seed", type=int, default=7, help="First CV seed (default 7, then +11 per repeat)")
    parser.add_argument("--repeats", type=int, default=5, help="Number of separate CV seeds, 1–100 (default 5)")
    parser.add_argument("--folds", type=int, default=5, help="Requested CV folds (default 5)")
    parser.add_argument("--group-col", default=None, help="Real experiment/run group ID column; opt-in only")
    parser.add_argument("--pressure-gap-min-atm", type=float, default=0.10,
                        help="Descriptive rounded-pressure gap width threshold, not certified OOD (default 0.10)")
    parser.add_argument("--check-pressure", type=float, action="append", default=[],
                        help="Optional pressure (atm) to screen per fuel; can be repeated")
    args = parser.parse_args()
    try:
        run_audit(args.data, args.output_dir, args.seed, args.repeats, args.folds,
                  args.group_col, args.pressure_gap_min_atm, args.check_pressure)
    except (ValueError, FileNotFoundError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
