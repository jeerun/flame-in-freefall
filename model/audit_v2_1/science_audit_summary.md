# Second Toe — Scientific Validation Audit (Independent Model)

> **Scope:** This document audits a separately fitted model. It does **not** certify the saved console model, spacecraft safety, or live operational fire risk.

## Evaluation

- Data: 274 raw rows; 252 feature-valid rows; 199 labelled classification rows.
- Method: stratified row cross-validation (5 folds), 5 seeds; group field: none (row CV).
- First-seed classification: accuracy 0.894, balanced accuracy 0.642, ROC-AUC 0.813, Brier 0.0843.
- Majority-class accuracy baseline 0.864; descriptive constant-prevalence Brier reference 0.1173.

Fold baselines use only training labels (pooled fuels). Existing constant-prevalence and majority-class metrics are descriptive full-subset references, not held-out baselines.

## Fuel-specific classification (first seed, threshold 0.5)

| Fuel | n | Completion n | Completion precision | Completion recall | Completion F1 | Extinction recall | ROC-AUC |
|---|---:|---:|---:|---:|---:|---:|---:|
| heptane | 75 | 19 | 1.000 | 0.263 | 0.417 | 1.000 | 0.871 |
| methanol | 124 | 8 | 0.600 | 0.375 | 0.462 | 0.983 | 0.585 |

## Pressure evidence gaps (raw input pressures)

- **heptane:** no observed pressure strictly between 0.7163 and 0.9895 atm (gap 0.27 atm).
- **methanol:** no observed pressure strictly between 0.7139 and 0.9913 atm (gap 0.28 atm).

Pressure gaps indicate sparse **pressure-only** evidence, not a validated multivariate out-of-distribution classifier.

## Interpretation and next checks

1. Review the completion recall and its small class support, not accuracy alone.
2. Inspect `calibration_bins.csv`; do not interpret equal-count bin gaps as probability guarantees.
3. Compare multiple CV seeds in `cv_seeds_metrics.csv`; seed variation is not an independent test set.
4. If genuine experiment/run IDs exist, rerun with `--group-col COLUMN` to reduce replicate leakage.
5. Compare dataset filtering, target definitions, and features with the **deployed** console model before making UI claims.
6. State that visible droplet-flame extinction is not complete combustion termination or verified cabin fire safety.

## Limitations

- Independent audit refit; not evaluation of saved deployed model files or console output.
- Compare FEATURES, dataset filters, and hyperparameters with current model/train.py before claiming identical methodology.
- Data reused over CV seeds; seed variation is not an independent validation set or confidence interval.
- Grouped splitting is only used when --group-col is provided with genuine experiment/run IDs. Otherwise correlated replicates could inflate scores.
- Probability bins and fuel-specific class metrics can be highly unstable with few Completion cases.
- When a class is never predicted, its precision is mathematically undefined; scikit-learn zero_division=0 reports it as 0, with a separate flag.
- No threshold calibration or probability adjustment has been deployed or validated.
- Pressure gap threshold is an illustrative audit screen on raw pressure values, not a certified physical OOD boundary. Rounded histograms are display-only.
- Nearest-neighbor distances describe training-data coverage, not calibrated model confidence.
- Visible droplet-flame extinction is not evidence of complete combustion termination or spacecraft cabin fire safety.
- methanol: only 8 labelled Completion cases; estimates are fragile.
