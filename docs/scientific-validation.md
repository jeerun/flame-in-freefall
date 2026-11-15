# Second Toe — Scientific Validation Method & Review Notes

**Project:** NASA Space Apps 2026 · Flame in Freefall

**Workstream:** Independent Scientific Validation · `feature/scientific-validation`

**Status:** V2.1 passed all 5 automated tests and completed a cleaned NASA FLEX audit using 5-fold stratified row cross-validation across 5 seeds. Results are diagnostic, not certification or validation of the deployed console model.

## Purpose and scope

The `model/science_audit.py` tool **trains and evaluates a separate audit model** on the cleaned NASA FLEX data. It does not evaluate or alter the saved model used by the handheld console. It is not a spacecraft fire-risk predictor and does not certify fire suppression. Cross-validation scores must not be presented as accuracy of the deployed console unless independently verified against its exact preprocessing and model artifacts.

## How to run

From the repository root, with Python, NumPy, Pandas, and scikit-learn installed:

```powershell
py model/science_audit.py --repeats 5 --check-pressure 0.85
```

If the dataset has a *verified* `run_id` or experiment identifier, use **grouped CV** only after checking what constitutes an independent experiment:

```powershell
py model/science_audit.py --group-col run_id --repeats 5 --check-pressure 0.85
```

Do **not** invent group IDs or assume a similarly named column is a valid grouping key. Inspect any such column first. The tool fails with a clear error if a proposed grouping cannot support class-stratified group CV.

The script writes these generated files into `model/`:

| Output | Contents |
|---|---|
| `science_audit_report.json` | Confusion matrices, per-class metrics, per-fuel results, repeated-CV summaries, pressure coverage, limitations |
| `calibration_bins.csv` | Equal-count calibration bins for the first CV seed only |
| `cv_seeds_metrics.csv` | Each repeated stratified CV seed, including Completion and Extinction precision/recall/F1 |
| `science_audit_summary.md` | Automatically generated teammate-friendly findings and cautions |

## Preliminary findings from 15 November screenshots (V1 run)

The following values are **from the team member's earlier local independent audit**, not from the deployed model and not automatically V2 results.

- 274 raw rows; 252 feature-valid rows; 199 classification rows.
- Extinction: 172 of 199; Completion: 27 of 199. Baseline always predicting Extinction has **86.4% accuracy**.
- First-seed audit accuracy approximately **89.45%**; historically reported balanced accuracy **67.89%** (inconsistent with the matrix below; must be rechecked); ROC-AUC approximately **0.813**; Brier score approximately **0.0843**.
- Heptane: 75 classification cases, 19 Completion; Completion recall about **0.26**; Extinction recall **1.00**.
- Methanol: 124 classification cases, 8 Completion; Completion recall about **0.38**; Extinction recall about **0.98**; fuel-specific ROC-AUC about **0.59**.
- Combined confusion matrix (actual rows Completion, Extinction; prediction columns Completion, Extinction): `[[8, 19], [2, 170]]`. Thus 19/27 observed Completion cases were predicted as Extinction at threshold 0.5 in that *audit run*.
- The Heptane pressure observations in the report cluster around approximately **0.69–0.72 atm** and **0.99–1.01 atm**. A query at 0.85 atm lies in an observed pressure gap, even though it is inside the global minimum and maximum.

**Interpretation:** Raw accuracy obscures weak Completion recall. The high Extinction prevalence makes a naive baseline look accurate. Because only 27 Completion examples exist, class-specific estimates and per-bin calibration are fragile. The V2 script evaluates these metrics across multiple split seeds; this does not replace a genuinely independent test set.

The matrix `[[8, 19], [2, 170]]` implies balanced accuracy `(8/27 + 170/172)/2 = 0.64233` (64.23%), not 67.89%. The screenshot-derived values above are historical notes, not a verified coherent result set. Use the generated report from the actual CSV as authoritative.

## V2.1 additions and verification

- Raw pressure values determine ranges, gaps and query warnings; the rounded histogram is display-only.
- `fold_training_prevalence_baselines` fits each constant baseline on the training fold only, pooling both fuels. Existing prevalence baselines remain descriptive references calculated from the full reported subset.
- Dataset and script SHA-256 hashes and Python/package versions support reproducibility.
- Absent-class recall is `null`, not evidence of zero sensitivity.
- Five automated tests pass: known confusion-matrix arithmetic, raw-pressure boundaries, group isolation, absent-class recall, and full row/group CV output generation. Test data are synthetic, not NASA FLEX.
- The real cleaned CSV, deployed artifacts and repository are not included here; no new real-data metrics, commit or PR is claimed.

### Pressure evidence wording

| Condition | Label | Interpretation |
|---|---|---|
| Outside this fuel's raw observed pressure range | Unsupported | Pressure extrapolation beyond observed evidence; not proof of physical impossibility |
| Strictly inside a gap at least the configured width (default 0.10 atm) | Limited Evidence | No observed pressure within that interval; heuristic review flag |
| Otherwise | Not assessed | Pressure screen did not flag a gap; does not establish joint-feature support |

Do not automatically label a query Supported from this screen or use nearest-neighbor P95 as a probability/confidence cutoff. A Supported label needs a separately specified and evaluated joint-feature coverage policy. Small Completion support (currently flagged at fewer than 10) is descriptive and is not a calibrated reliability boundary.

## Version 2 checks

1. **Class-aware reporting:** Confusion matrix in `[Completion, Extinction]` order; precision, recall, F1, support for each class; balanced accuracy and majority-class baseline.
2. **Seed stability:** Repeated 5-fold stratified cross-validation using distinct seeds. Each run produces one out-of-fold prediction per example; V2 reports mean, standard deviation, minimum and maximum across seeds. These are *descriptive* differences in splits, **not confidence intervals**.
3. **Group-level leakage prevention:** Optional `--group-col` uses stratified group folds so no verified experiment/run group spans train and validation. Without this, the audit remains row-based.
4. **Pressure coverage:** For each fuel, show a rounded display histogram and detect large internal gaps using raw pressures (default: at least 0.10 atm). `--check-pressure 0.85` reports a pressure-only evidence label. This threshold is a descriptive review aid, not an experimentally validated OOD limit.
5. **Calibration:** Equal-count reliability bins from the first seed only; sparse bins must not be interpreted as proof that any particular probability is reliable.
6. **Regression:** Evaluate burn-rate with out-of-fold MAE and R²; do not convert R² into an accuracy percentage.

## Known limitations and scientific interpretation

- The audit uses its own `StandardScaler` and `LogisticRegression(C=1.0)` model; it must not be conflated with the team's deployed JavaScript console model.
- The current label is **visible droplet-flame extinction vs fuel completion**. Visible extinction does *not* prove all combustion stopped; cool-flame chemistry can persist. The prototype does not estimate real spacecraft cabin fire risk.
- Pressure is only one input. A pressure gap warning alone cannot assess support for a *joint combination* of fuel, O₂, CO₂, He, pressure, and initial droplet diameter.
- A heuristic cutoff at 0.10 atm and nearest-neighbor percentiles are not certified OOD thresholds. Avoid labels such as “safe,” “validated,” or “95% confident.”
- Stratified row CV can leak between correlated runs. Run IDs must be verified before reporting grouped validation.
- No threshold adjustment, class weighting, or sigmoid/isotonic calibration should be deployed without a separate, leakage-safe comparison and reviewer approval.

## Proposed reviewer checklist

- [ ] Verify target definitions, feature list, and filters match the authoritative `model/train.py` and `data/clean/flex_clean.csv` in the current branch.
- [ ] Confirm that per-class support, precision, recall, F1, and confusion matrices are consistent.
- [ ] Inspect per-seed variability for Methanol vs Heptane; do not present V2 as deployed-model testing.
- [ ] Verify whether a genuine experiment/run ID exists before running grouped CV.
- [ ] Verify any claimed pressure gap against the source data and relevant fuel.
- [ ] Keep warnings visible in the console for visible-flame extinction and limited experimental coverage.
- [ ] Have the file owner review changes; merge through a Pull Request only after checking for updated `origin/main`.

## Suggested Pull Request description

**Title:** `Add independent scientific audit V2 and evidence-coverage notes`

**Summary:** Adds reusable diagnostic scripts for per-class metrics, split-seed stability, optional group CV, pressure evidence-gap reporting, and reviewer documentation. No change to model training/deployment or the handheld console. Results are explicitly labelled independent and non-operational.

**Real-data verification still required:** Run `py model/science_audit.py --repeats 5 --check-pressure 0.85`, inspect the four generated files, and compare classification totals against `model/metrics.json` and the current `model/train.py` methodology.

## Verified local audit — 15 November 2026

The audit used 199 classification samples: 27 Completion and 172 Extinction cases. Across five CV seeds, mean accuracy was 88.84%, mean balanced accuracy was 61.39%, and mean Completion recall was 23.70%.

Mean Completion recall was 18.95% for Heptane and 35.00% for Methanol. These results describe an independently refitted audit model, not the deployed console model.

Both fuels have an internal pressure evidence gap containing 0.85 atm:
- Heptane: 0.7163–0.9895 atm.
- Methanol: 0.7139–0.9913 atm.

Results are stored in `model/audit_v2_1/`. Validation is row-based; no verified experimental grouping was used. Variation across seeds is not a confidence interval or external validation.