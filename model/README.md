# Model

The training script lives here and writes one file: `../console/model.js`.
The console reads that file and replaces its built-in mock numbers.

## What model.js must look like

See `model.example.js` in this folder. Copy its shape exactly.

- `extinction` is a logistic regression:
  P(flame goes out) = sigmoid(intercept + fuel[fuel] + sum(coef[key] * value))
- `burn_rate` is a linear regression, in mm^2/s:
  K = intercept + fuel[fuel] + sum(coef[key] * value)
- Coefficients apply to raw values in the units shown. Do not standardize the
  inputs, or convert the coefficients back to raw units before exporting.
- `data_min` and `data_max` are the real minimum and maximum of each column in
  the training data. The "outside the tested range" warning depends on them.
- `min` and `max` are how far the slider goes. Make them a little wider than the
  data so the warning can be shown.
- Set `meta.mock` to false, `meta.source` to the dataset name, and `meta.rows`
  to the number of tests used.

## Extra fields in the real export

`train.py` also writes these. The console uses them when present and still runs
without them (the example file leaves them out).

- `meta.auc`, `meta.burn_rate_mae`, `meta.rows_burn_rate`: held-out accuracy,
  shown in the fine print of the explanation panel.
- `meta.exclusive`: pairs of settings that no test combined, `[["co2","he"]]`.
  Both above zero counts as outside the tested range.
- `meta.far_distance`: the 95th percentile of each test's distance to its nearest
  same-fuel neighbour. A reading farther than this from every test gets a warning.
- `tests`: one row per in-scope test,
  `[test, id, fuel, o2 %, pressure atm, co2 %, he %, droplet mm, test end, burning rate]`.
  The console shows the closest one and counts how the nearby ones ended.
  Distance: same fuel only, each setting divided by its tested range
  (`data_max - data_min`), then the straight-line distance.

## Rules that keep the result honest

- Use only settings known before ignition as inputs. Never feed in anything
  measured after the burn (burn time, extinction diameter): that leaks the answer.
- Hold out part of the data and report accuracy on it, not on the training rows.
- Write the accuracy numbers into `docs/submission.md`, good or bad.
