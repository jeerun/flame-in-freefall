# Python–Console numerical parity

Checked 15 November 2026 against repository commit
`6162bcaabc4d3c88dfa119d0f472f8d51b450662`.

## Purpose

Verify that the exported model and the actual Console inference functions compute
matching numbers. This is not cross-validation, probability calibration, a UI
browser test, or a safety assessment. Production files are not changed.

## Run from the repository root

Requires Python with numpy, pandas and scikit-learn, plus Node.js on PATH.

```powershell
py model/check_parity.py
py -m unittest discover -s tests -p test_model_parity.py -v
```

The first command writes `model/parity_report.json` and exits nonzero on a
numerical mismatch. Source hashes and runtime versions identify the exact inputs.
A missing dependency, changed extraction anchor or invalid model produces an error
instead of a passing result.

## What is compared

1. Refit the current `train.py` configuration and scope without calling its
   artifact-writing main function. Reuse its feature design and export helpers.
2. Read `console/model.js` in Node VM. Check the feature order and supported fuels.
3. Extract and execute the actual `linear` and `predictFor` functions from
   `console/index.html`. No copied JavaScript prediction formula is used.
4. Compare Python raw-coefficient calculations to JavaScript using absolute
   tolerance 1e-12. Compare the full-precision sklearn refit to JavaScript with
   tolerance 1e-4 (probability units or mm²/s respectively), allowing small
   six-decimal export rounding differences. These are numerical tolerances,
   not acceptable physical prediction errors.
5. Check `pKeep = 1 - pOut` and `K = max(0, rawK)` explicitly.

Input mapping: `o2_pct→o2`, `pressure_atm→p`, `co2_pct→co2`, `he_pct→he`,
`d0_mm→d0`; percentages are on the 0–100 scale, pressure in atm, diameter in mm.
Methanol is the binary indicator in Python. Extinction is class 1. The Console
returns both extinction (`pOut`) and completion (`pKeep`) probabilities.

## Verified results

820 inputs: 252 source rows, 4 default/gap cases, 64 slider corners, and 500 seeded
random cases. Numerical stress probes include OOD/physically invalid mixtures;
they are not additional experimental evidence.

| Comparison | Maximum absolute error |
|---|---:|
| Exported coefficients: Python vs JS extinction probability | 3.33e-16 |
| Exported coefficients: Python vs JS raw burning rate | 4.44e-16 mm²/s |
| Full-precision refit vs JS extinction probability | 5.30e-6 |
| Full-precision refit vs JS raw burning rate | 3.92e-5 mm²/s |
| Completion complement and zero clamp | 0 |

Both models' rounded refit coefficients match the committed export exactly in
this environment. One stress case produced a negative raw rate; zero clamping
was exercised. All three tests passed, including deliberate probability reversal
and clamp removal in isolated temporary copies.

## Limits and next work

- The historical serialized Python estimators are not present; this compares a
  current refit and the committed export.
- Explicit scope and fitting setup mirror the current training script. Review
  this checker whenever training or input schema changes.
- Node VM checks pure inference, not DOM input parsing, slider events, displayed
  rounding, browser fallback, or the live GitHub Pages deployment.
- No model thresholds, coefficients, UI warnings or deployment were changed.
- Next: test browser inputs/display against these predictions, then evaluate the
  actual training pipeline with leakage-safe CV. Keep performance and numerical
  parity claims separate.
