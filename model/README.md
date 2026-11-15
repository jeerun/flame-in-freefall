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

## Rules that keep the result honest

- Use only settings known before ignition as inputs. Never feed in anything
  measured after the burn (burn time, extinction diameter): that leaks the answer.
- Hold out part of the data and report accuracy on it, not on the training rows.
- Write the accuracy numbers into `docs/submission.md`, good or bad.
