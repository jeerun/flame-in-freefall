# Per-fuel model: a proposed replacement for the two console models

> **Update, 15 November 2026: the console now uses this model.** The switch was made the same day, after
> the training and the comparison below were re-run on the team's PC (identical files) and the gain was
> checked with separate code and stricter hold-outs (`model/verify_per_fuel.py`, results in
> `model/per_fuel/independent_check.json`): held out one gas mix or one test day at a time, AUC goes from
> 0.80 to 0.90, and this model is ahead of the earlier one in more than 99 % of 4000 paired resamples.
>
> What moved with the switch: `model/train_per_fuel.py` now writes `console/model.js` and
> `model/metrics.json`; `model/train.py` writes the base export and the earlier model into `model/pooled/`
> (run it first); `model/per_fuel/model.js` and `metrics.json` are gone, their content is in those two
> files; `patch_console.py` has been applied and now refuses to run again; in `comparison.json` the earlier
> model is called `one_slope` and the keys no longer say "proposed". Two things were added on the way in:
> the page shows no chance below 1 % or above 99 %, and the export lists the slopes whose sign is not
> stable (`meta.unsure`), which the explanation panel now flags.
>
> The text below is the proposal as it was written. Where it says "the current model" it means the
> earlier, one-slope model, and its "not done in this branch" section has since been done.

Written 15 November 2026 against repository commit
`dd72ee287b1cfebc28253f00956d6106b9704145`, branch `feature/per-fuel-model`.

## What this is, and what it is not

A second version of the two console models, trained and checked next to the current
one. It predicts held-out FLEX tests better than the current model and better than
every other candidate tried here (numbers below).

**Nothing that runs today is changed.** This branch only adds files. `model/train.py`,
`console/model.js`, `console/index.html`, `model/metrics.json` and the published copy
on `gh-pages` are exactly as they were. The console still shows the current model.
Switching it over is a separate step, described at the end, for the owners of
`model/` and `console/` to decide.

It is a study and planning model like the current one, not a crew procedure.

## Files added

| File | What it is |
|---|---|
| `model/train_per_fuel.py` | Trains the per-fuel model. Writes only into `model/per_fuel/`. |
| `model/per_fuel/model.js` | The export, in the shape of `console/model.js` with `fuel_coef` added. |
| `model/per_fuel/metrics.json` | Held-out accuracy, in the shape of `model/metrics.json`. |
| `model/compare_models.py` | Compares the candidates on the same held-out tests. |
| `model/per_fuel/comparison.json` | Every number in the tables below. |
| `model/per_fuel/patch_console.py` | The change `console/index.html` needs to read the new export: 11 exact replacements, no function added. Not applied by anything here. |
| `tests/test_per_fuel_model.py` | Six tests. |
| `docs/per-fuel-model.md` | This document. |

## Run from the repository root

Needs Python with numpy, pandas and scikit-learn. The two page tests also need
Node.js on PATH and are skipped without it.

    python model/train_per_fuel.py
    python model/compare_models.py
    python -m unittest discover -s tests -p test_per_fuel_model.py -v

The first takes a few seconds, the second a few minutes. Both are seeded: a re-run
gives the same files.

## What is different from the current model

Same data (`data/clean/flex_clean.csv`), same scope (252 tests at or below 1.1 atm with
a known droplet size), same six inputs, same two kinds of model (logistic regression
for "goes out", linear regression for the burning rate), same seed and repeats. The
script imports these from `model/train.py` instead of copying them.

Two things change:

1. **Each fuel has its own slope for every setting.** The current model gives heptane
   and methanol the same slopes and only a different starting point. The data say the
   fuels respond differently: carbon dioxide clearly pushes heptane flames toward going
   out, and shows no such effect for methanol.
2. **The strength of the penalty is chosen from the data** (C from 0.3, 1, 3, 10; it
   picks 10) by cross-validation inside the training rows only. The current model
   fixes C at 1. Because the choice is made again inside every training fold, the
   held-out numbers below include it and are not flattered by it.

The formula on the page becomes, for both models:

    intercept + fuel[fuel] + sum((coef[key] + fuel_coef[fuel][key]) * value)

A third, separate proposal comes with the export as `meta.watch = 0.30`: a "watch"
level for the console at a 30 % chance of burning all the fuel (see below).

## Results on held-out tests

Five-fold cross-validation repeated 20 times, the protocol of `model/train.py`.
199 tests for the outcome (172 went out, 27 burned to completion), 252 for the
burning rate.

| Measure | Current model | Per-fuel model |
|---|---|---|
| AUC, both fuels | 0.813 | 0.902 |
| AUC, heptane only | 0.846 | 0.906 |
| AUC, methanol only | 0.605 | 0.847 |
| Brier score (lower is better; 0.117 with no model) | 0.0865 | 0.0676 |
| Log loss (lower is better) | 0.315 | 0.237 |
| Accuracy (0.864 for always answering "goes out") | 0.887 | 0.915 |
| Completions found, read as yes or no at 50 % | 21.7 % | 52.4 % |
| Tests that went out but were called completion at 50 % | 0.8 % | 2.4 % |
| Burning rate, R² | 0.705 | 0.732 |
| Burning rate, mean absolute error (mm²/s) | 0.048 | 0.045 |

The "current model" column is recomputed by `model/compare_models.py` and matches
`model/metrics.json`.

## Comparison with other candidates

Every candidate sees the same rows and the same folds, so the comparison is paired.
"Grouped" keeps all tests with the same fuel and gas mix in one fold (68 groups), so
a test is never predicted from its own replicates.

Flame outcome:

| Candidate | AUC | Brier | Log loss | AUC grouped | Brier grouped |
|---|---|---|---|---|---|
| Current console model | 0.813 | 0.0865 | 0.315 | 0.805 | 0.0867 |
| Current model, rarer outcome weighted up | 0.801 | 0.1717 | 0.511 | 0.789 | 0.1744 |
| Per-fuel slopes, fixed penalty (C=1) | 0.875 | 0.0763 | 0.267 | 0.872 | 0.0745 |
| **Per-fuel slopes, penalty chosen from the data (proposed)** | **0.902** | **0.0676** | **0.237** | **0.900** | **0.0670** |
| Per-fuel slopes plus two curved terms | 0.902 | 0.0699 | 0.241 | 0.902 | 0.0694 |
| Gradient-boosted trees | 0.786 | 0.0968 | 0.336 | 0.766 | 0.1006 |
| Random forest | 0.814 | 0.0908 | 0.311 | 0.785 | 0.0961 |
| No model (always the share that went out) | n/a | 0.1173 | 0.397 | n/a | 0.1174 |

Burning rate:

| Candidate | R² | Mean abs. error | R² grouped | Mean abs. error grouped |
|---|---|---|---|---|
| Current console model | 0.705 | 0.048 | 0.698 | 0.049 |
| **Per-fuel slopes (proposed)** | **0.732** | **0.045** | **0.724** | **0.046** |
| Per-fuel slopes plus two curved terms | 0.742 | 0.045 | 0.722 | 0.047 |
| Gradient-boosted trees | 0.664 | 0.053 | 0.618 | 0.058 |

## Is it the best one? What the comparison shows, exactly

- **Against the current model:** better on AUC, Brier score and log loss in all 20
  repeats, with either way of holding out. Burning rate: better on both measures in 20
  of 20 repeats by rows, and in 19 (R²) and 20 (error) of 20 grouped.
- **Against the other candidates:** the lowest Brier score and the lowest log loss of
  all of them, with either way of holding out. These two measures score the percentage
  itself, which is what the console shows.
- **Where another candidate is level or ahead on one measure:**
  - Adding two curved terms gives the same AUC (0.902; the proposed model is ahead in
    9 of 20 repeats) and a slightly higher burning-rate R² by rows (0.742). It has a worse Brier
    score in 20 of 20 repeats, loses its R² lead when replicates are kept together,
    and needs four more coefficients per model. Not worth it.
  - Weighting the rarer outcome up finds 76 % of the completions at 50 %, but it also
    puts 46 % of the tests that went out at or above 30 %, and its Brier score doubles:
    its percentages can no longer be read as chances.
- **Trees do worse than the current model**, and could not be exported as a formula.

So the claim is: **of the eight candidates tried, on held-out FLEX tests, this one
gives the most accurate percentages, and it is level with the best on ranking.** It is
not a proof that no better model exists, and it says nothing about a new experiment, a
fuel FLEX did not burn, or a real cabin fire.

## Checks on the model itself

**Do its percentages mean what they say?** Held out, pooled over the 20 repeats:

| Chance of burning all the fuel | Tests per repeat | Share that did |
|---|---|---|
| under 10 % | 134.7 | 3 % |
| 10 to 20 % | 18.3 | 16 % |
| 20 to 30 % | 15.2 | 22 % |
| 30 to 65 % | 18.8 | 33 % |
| 65 % and above | 12.0 | 93 % |

The current model rarely goes above 65 % (3 tests). This one does for about 12 tests,
and nearly all of them burned to completion.

**Which slopes can be trusted?** The model was refitted 1000 times on resampled tests.
A slope counts as stable when 90 % of the refits agree on its sign.

| Setting | Heptane | Methanol |
|---|---|---|
| Oxygen | stable: more oxygen, less likely to go out | stable: same direction |
| Droplet size | stable: larger droplet, more likely to go out | **not stable** |
| Carbon dioxide | stable: more, more likely to go out | **not stable**, close to zero |
| Helium | stable: more, more likely to go out | stable: same direction |
| Pressure | **not stable** | **not stable** |

**The four methanol tests the current model misses** (tests 97, 108, 111, 112: 0.7 atm,
20 to 30 % carbon dioxide, burned to completion; under 5 % from the current model) get
9 to 21 % held out. Better, still low.

## The "watch" level

Read as a yes or no at 50 %, any of these models misses many completions. A lower
level catches more: at a 30 % chance of burning all the fuel, the per-fuel model flags
64.1 % of the tests that burned to completion and 7.9 % of those that went out.

Most of that gain comes from the level, not from the new model: the current model at
30 % flags 60.7 % and 7.6 %. The level could be adopted on its own.

## Limits that remain

- Methanol still has only 8 tests that burned to completion (of 124). Its droplet-size
  and carbon-dioxide slopes are not stable, so the explanation panel's "pushes toward"
  sentences for those two settings on methanol should not be leaned on.
- Pressure still sits at two levels (about 0.7 and 1.0 atm). Its effect is not known
  for either fuel, in either model.
- "Goes out" still means the visible flame.
- Still no column saying which rows are space tests and which are ground tests.
- Half of the completions are still missed at 50 %.
- The comparison reuses the same 199 and 252 tests. There is no separate test set.
- The readings on screen change. With every setting at its starting value the chance
  of burning all the fuel goes from 35 % to 57 % for heptane and from 8 % to 3 % for
  methanol. `docs/demo-script.md` quotes readings from the current model.

## How it was checked

- `tests/test_per_fuel_model.py`, six tests, all pass here (Python 3.13,
  scikit-learn 1.9.1, Node 22): a re-run reproduces the committed export and metrics;
  only the two formulas and their accuracy differ from the current export; the exported
  coefficients give the fitted model's predictions; the page's own prediction code,
  patched in a temporary copy, matches the Python model on 652 inputs to within 0.0001;
  the patched page gives exactly the same numbers as the unpatched page when it is given
  the current `model.js`; and the patch refuses a page it has already changed or no
  longer recognises.
- The existing tests still pass (`test_model_parity.py` 3 of 3, `test_science_audit.py`
  5 of 5, `node tests/test_console_features.cjs`). The last one also passes on a patched
  copy of the page with the current export.
- Headless Chrome at 1280x680 and 1280x800, on temporary copies: the patched page with
  the new export shows no page errors and no scrolling on any of the three pages, the
  explanation panel does not overflow, the zoomed star map draws its three model lines,
  and the "Watch" banner appears when the reading crosses 30 %. The patched page with
  the current export behaves exactly like the unpatched page on the same script.
- Not checked: the real Legion Go, a real gamepad, sound and rumble, Ember's answers
  about a reading, the Fire drill scores with the new model.

## Switching the console over (not done in this branch)

For the owners of `model/` and `console/`, after review:

1. `python model/per_fuel/patch_console.py` (`--check` first: it says whether the page
   still matches and writes nothing).
2. Copy `model/per_fuel/model.js` over `console/model.js`.
3. Run the tests above and the usual browser checks.

Then these would be out of date and need the same care:

- `python model/train.py` would write the old model back over `console/model.js`.
  The two training scripts should become one first.
- `model/check_parity.py` refits the `train.py` recipe and would report a mismatch.
  `tests/test_per_fuel_model.py` holds the same check for the new model.
- The accuracy numbers in `README.md`, `docs/submission.md` and `docs/sources.md`, the
  readings in `docs/demo-script.md`, and the notes in `PROJECT-NOTES.md`.
- `tests/test_console_features.cjs` expects the current model's reading (35 % at the
  starting values) and fails on the new one (57 %) until that number is updated.
- `docs/scientific-validation.md` audits a refit of the current recipe.
- `docs/ember-check.md` should be regenerated.
- The published copy: `git subtree push --prefix console origin gh-pages`.

The page change is backward compatible: a page with the patch still reads an export
without `fuel_coef` or `meta.watch` and behaves as before.
