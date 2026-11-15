# Model

Two scripts, run in this order, write the file the console reads, `../console/model.js`.
The console reads that file and replaces its built-in mock numbers.

1. `train.py` builds the base export in `pooled/`: the scope, the tested range of every
   input, the sliders, the test rows, and the earlier models where both fuels share one
   slope per setting (the console used those until Nov 15, 2026).
2. `train_per_fuel.py` trains the models the console uses, where each fuel has its own
   slopes, puts them into that export and writes `../console/model.js` and
   `metrics.json`.

`compare_models.py` measures the console's model against the earlier one and six other
candidates on held-out tests, and `verify_per_fuel.py` checks that result with separate
code. Both write into `per_fuel/`. The write-up is `../docs/per-fuel-model.md`.

`design_audit.py` looks for holes in the model design (which tests the outcome model
leaves out, how far a reading moves between refits, what the labels hide) and writes
`per_fuel/design_audit.json`. The write-up is `../docs/model-design-audit.md`.

## What model.js must look like

See `model.example.js` in this folder. Copy its shape exactly.

- `extinction` is a logistic regression:
  P(flame goes out) = sigmoid(intercept + fuel[fuel] + sum((coef[key] + fuel_coef[fuel][key]) * value))
- `burn_rate` is a linear regression, in mm^2/s:
  K = intercept + fuel[fuel] + sum((coef[key] + fuel_coef[fuel][key]) * value)
- `fuel_coef` holds what each fuel adds to the shared slopes. It may be left out: the
  page then uses the shared slopes alone, as in the example file and the base export.
- `disruption` (optional) has the same shape as `extinction`:
  P(test ends in "Disruption") = sigmoid(the same sum). "Disruption" is NASA's label
  for an ending with no clear outcome. Without it the page shows no disruption chance.
- Coefficients apply to raw values in the units shown. Do not standardize the
  inputs, or convert the coefficients back to raw units before exporting.
- `data_min` and `data_max` are the real minimum and maximum of each column in
  the training data. The "outside the tested range" warning depends on them.
- `min` and `max` are how far the slider goes. Make them a little wider than the
  data so the warning can be shown.
- Set `meta.mock` to false, `meta.source` to the dataset name, and `meta.rows`
  to the number of tests used.

## Extra fields in the real export

The training scripts also write these. The console uses them when present and still
runs without them (the example file leaves them out).

- `meta.watch`: the chance of burning all the fuel from which the page says "could go
  either way" and shows a "Watch" banner. 0.30 in the real export, 0.35 without it.
- `meta.unsure`: per fuel, the settings whose slope changes sign in more than one in
  ten refits on resampled tests. The explanation panel says so next to any sentence
  that leans on one of them.

- `extinction_draws` and `meta.range`: the extinction formula refitted on resampled
  tests, one row per refit: the intercept, one slope per setting (in the order of
  `features`), then for each further fuel its offset and what it adds to each slope.
  The page shows where the middle of them put the reading (`meta.range.percentiles`,
  5 and 95). Without them the page shows no range.
- `meta.auc`, `meta.burn_rate_mae`, `meta.rows_burn_rate`, `meta.auc_disruption`,
  `meta.rows_disruption`: held-out accuracy, shown in the fine print of the
  explanation panel.
- `meta.exclusive`: pairs of settings that no test combined, `[["co2","he"]]`.
  Both above zero counts as outside the tested range.
- `meta.far_distance`: the 95th percentile of each test's distance to its nearest
  same-fuel neighbour. A reading farther than this from every test gets a warning.
- `tests`: one row per in-scope test,
  `[test, id, fuel, o2 %, pressure atm, co2 %, he %, droplet mm, test end, burning rate, burn time s, end diameter mm]`.
  The console shows the closest ones, counts how the nearby ones ended, draws every
  test as a star on its map, and replays a test on screen. Burn time and end diameter
  are measured after the burn: they are there for the replay only and are never
  model inputs.
  Distance: same fuel only, each setting divided by its tested range
  (`data_max - data_min`), then the straight-line distance.

## Rules that keep the result honest

- Use only settings known before ignition as inputs. Never feed in anything
  measured after the burn (burn time, extinction diameter): that leaks the answer.
- Hold out part of the data and report accuracy on it, not on the training rows.
- Write the accuracy numbers into `docs/submission.md`, good or bad.
