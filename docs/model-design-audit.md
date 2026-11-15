# Model design audit: the holes we found, and what closes them

Written 15 November 2026 on branch `fix/model-design-gaps`.

We went looking for holes in our own model design, with the data. This page lists
what turned up, what was done about each, and what is still open. Every number comes
from `model/design_audit.py` (results in `model/per_fuel/design_audit.json`) or from
`model/metrics.json`. Both are seeded: a re-run gives the same files.

    python model/train_per_fuel.py
    python model/design_audit.py

The two formulas the console already used are **unchanged** by this work: every
reading it showed before is the same (heptane at the starting values 57 %, Moon Base
99 %, tests 108 and 183 at 25.6 % and 25.7 %). What changed is what is shown beside
them.

## Short version

| # | Hole | What the data say | What was done | Still open |
|---|---|---|---|---|
| 1 | The outcome model spoke of two endings. NASA's table has three. | 53 of 252 tests ended in "Disruption". They are most tests in oxygen-rich air, and a model predicts them well (AUC 0.89). | A third formula gives the chance of a disruption. The page shows it beside the reading and turns amber at 50 % or more. | The table does not say what a disruption is. |
| 2 | One number, no range. | Refitted on resampled tests, the 57 % at the starting values falls between 34 % and 75 %. | The page shows that range beside the number. | The range covers which tests were run, not what the formula leaves out. |
| 3 | "The flame went out" sounds like "little burned". | When methanol flames went out, a median of 82 % of the droplet's volume was already gone. Heptane: 40 %. | The evidence box and the test list say how much was gone in nearby tests. | Methanol droplets take up water, so volume is not exactly fuel. |
| 4 | Accuracy quoted as single numbers, pooled over fuels. | AUC 0.90, but 0.83 to 0.96 with the tests resampled. Methanol 0.64 to 0.97. Burning rate R² 0.62 for heptane, 0.87 for methanol. | `model/metrics.json` now reports intervals and each fuel separately. The documents quote them. | |
| 5 | Methanol has 8 completions for 6 parameters of its own. | When the model said 30 to 65 % for methanol, 14 % completed (about five tests per split). | Smaller and more heavily penalised methanol models were tried. All scored worse held out, so the model stays. The range on screen is wide there. | Yes. More methanol completions would be needed. |
| 6 | Pressure cannot be separated from the gas mix. | At 0.7 atm only 2 heptane and 4 methanol clear outcomes are plain oxygen and nitrogen. | Documented. The page already flags the pressure slope as unsettled. Tests above 1.1 atm confirm the direction for methanol only. | Yes, for heptane. |
| 7 | "Time to consume the droplet" has no check. | For the 27 completions it is a median 1.18 times NASA's burn time. | Documented, with the spread. | The number on screen is unchanged. |
| 8 | The page's "tested range" pools both fuels. | Methanol was never run below 1.61 mm, heptane never above 45 % carbon dioxide. | Documented, not changed: per-fuel ranges would turn the Moon Base preset red over 0.001 atm. | Yes, a small one. |
| 9 | No file pins the package versions. | The scripts need scikit-learn 1.9. | `requirements.txt`. | |

## 1. A third ending

The outcome formula is fitted to tests that ended in "Extinction" or "Completion".
NASA's table has a third ending, "Disruption", for 53 of the 252 tests in scope.
Leaving them out would be harmless if they were scattered at random. They are not:

| Oxygen | Heptane, disrupted | Methanol, disrupted |
|---|---|---|
| up to 15 % | 0 of 9 | 0 of 36 |
| above 15 to 18 % | 1 of 29 | 0 of 35 |
| above 18 to 21.5 % | 11 of 38 | 5 of 40 |
| above 21.5 to below 25 % | 8 of 18 | 5 of 18 |
| 25 % or more | 11 of 12 | 12 of 17 |

Near the Moon Base preset (heptane, 29 to 31 % oxygen, about 0.7 atm) there are four
tests. All four were disrupted. So the "99 %" the page showed there was the chance of
burning all the fuel *if the test is not disrupted*, which almost never happened.

**What closes it.** A third formula, same inputs and same recipe as the other two,
fitted on all 252 tests: the chance that a test ends in a disruption.

- Held out (5 folds, 20 repeats, penalty picked inside each fold): AUC 0.892, Brier
  score 0.101 against 0.166 for no model.
- Does its percentage mean what it says? When it said under 10 %, 3.4 % were
  disrupted. At 10 to 30 %: 17.5 %. At 30 to 65 %: 47.8 %. At 65 % or more: 81.9 %.

| Settings | Burns all its fuel, among clear outcomes | Disruption | All three: disruption / burns all / goes out |
|---|---|---|---|
| Heptane at the starting values | 57 % | 32 % | 32 / 39 / 29 |
| Methanol at the starting values | 3 % | 12 % | 12 / 3 / 85 |
| Heptane in Moon Base air | 99.9 %, shown as 99 % | 98 % | 98 / 2 / 0 |
| Methanol in Moon Base air | 76 % | 85 % | 85 / 11 / 3 |
| Heptane at 24 % oxygen | 92 % | 68 % | 68 / 29 / 3 |
| Heptane at 16 % oxygen | 4 % | 4 % | 4 / 4 / 93 |

On the page: "Disruption chance N%" sits under the main reading. At 50 % or more the
evidence box turns amber ("Most tests like this were disrupted"), the one-line reading
says so, and the meter loses its colour. The explanation, the comparison table, the
CSV file (a new column) and Ember's instructions carry it too.

**Still open.** NASA's table and its PSI record do not say what a disruption is. We
report how often it was recorded. We do not say what it means for a fire.

## 2. A range for the main reading

The page showed one percentage. With 27 completions in 199 tests, that number moves
a good deal with which tests happened to be run.

**What closes it.** `model/train_per_fuel.py` already refitted the outcome formula
1000 times on resampled tests, to see which slopes keep their sign. The first 300 of
those refits now go into the export (`extinction_draws`), and the page shows where
the middle 90 % of them put the reading:

| Settings | Reading | Range |
|---|---|---|
| Heptane at the starting values | 57 % | 34 to 75 % |
| Methanol at the starting values | 3 % | 0.1 to 9 %, shown as 1 to 9 % |
| Heptane at 24 % oxygen | 92 % | 79 to 97 % |
| Methanol in Moon Base air | 76 % | 40 to 97 % |
| Heptane in Moon Base air | 99.9 % | 98.4 to 100 %, shown as 98 to 99 % |

**Still open.** The range says how much the estimate hangs on which tests were run.
It does not cover what the formula leaves out. The last row shows it: the range is
narrow there because every refit extrapolates the same straight line, while the real
problem is hole 1. The page's fine print says what the range is and is not.

A compact alternative, one table of variances instead of 300 refits, was tried and
dropped: it gives the same range in the middle of the scale but too wide a one near
0 % (for methanol at the starting values 0.3 to 28 %, where all 1000 refits give 0.2
to 8.5 %).

## 3. What "went out" hides

The label "Extinction" means the visible flame went out before the fuel was gone. It
says nothing about how much had burned. From the two diameters NASA recorded, the
share of the droplet's volume already gone at that moment:

| Fuel | Tests | Median | Middle half | 90 % or more gone | Less than half gone |
|---|---|---|---|---|---|
| Heptane | 54 | 40 % | 11 to 55 % | 5 | 35 |
| Methanol | 101 | 82 % | 45 to 89 % | 24 | 29 |

So a methanol reading of "97 % visible extinction" is not a reading of "almost
nothing burns": typically four fifths of the droplet was gone first.

**What closes it.** The evidence box now adds, for the nearby tests that went out,
the median share of the droplet's volume that was gone, and the list of closest tests
gives it for each test. No formula was added: these are NASA's own diameters.

**Still open.** 17 extinction tests have no usable end diameter. Methanol droplets
take up water as they burn, so for methanol the volume left is not all fuel.

## 4. How sure the accuracy numbers are

- Outcome formula, AUC 0.902. With the tests resampled (each with its held-out
  chance), the 95 % interval is 0.83 to 0.96. Heptane 0.906 (0.82 to 0.98), methanol
  0.847 (0.64 to 0.97).
- Does the percentage mean what it says, per fuel, held out:

| Model said | Heptane: tests per split, happened | Methanol: tests per split, happened |
|---|---|---|
| under 10 % | 32, 4 % | 103, 2 % |
| 10 to 30 % | 20, 14 % | 14, 25 % |
| 30 to 65 % | 14, 39 % | 5, 14 % |
| 65 % or more | 10, 97 % | 2, 73 % |

- Near-certain readings held up: when the model said under 1 % (76 tests per
  split), 1.3 % burned to completion. Over 99 % (1 test per split): all did.
- Burning rate: R² 0.732 overall, but 0.619 for heptane (MAE 0.069 mm²/s) and 0.873
  for methanol (MAE 0.026). It is least accurate for the tests that burned to
  completion (MAE 0.090, and 0.022 too low on average).

## 5. Methanol has 8 completions

Each fuel has six parameters of its own. Heptane has 19 completions for them,
methanol 8. The outcome is not perfectly separable (without a penalty the training
AUC is 0.955 for heptane and 0.932 for methanol, not 1), so the fit is defined. But
the middle of methanol's scale is not trustworthy: see the table above.

Five of the 8 methanol completions are in gas with 15 to 30 % carbon dioxide, and 6
are at about 0.7 atm. A straight-line formula cannot make much of that.

**What was tried.** The same folds for every candidate, penalty as in the console's
model (`model/per_fuel/design_audit.json`):

| Candidate | AUC | Brier | Methanol AUC | Methanol, 30 to 65 % band: said / happened |
|---|---|---|---|---|
| **Console model: own slope for every setting** | **0.902** | **0.0674** | **0.846** | 43 % / 14 % |
| Methanol's own slopes penalised 4 times more | 0.892 | 0.0716 | 0.833 | 44 % / 31 % |
| Methanol's own slopes penalised 16 times more | 0.866 | 0.0769 | 0.762 | 46 % / 32 % |
| Own slopes for oxygen and droplet size only | 0.891 | 0.0714 | 0.827 | 43 % / 37 % |
| Own slope for oxygen only | 0.809 | 0.0874 | 0.609 | 46 % / 35 % |
| One set of slopes (the earlier model's shape) | 0.810 | 0.0860 | 0.603 | 46 % / 33 % |

Every smaller model is better in that one band and worse everywhere else. The band
holds about five tests per split, so the gain there is mostly noise. The console's
model stays, and the range on screen is wide where methanol is uncertain (40 to 97 %
in Moon Base air).

## 6. Pressure and the gas mix

Pressure sits at two levels. The lower one almost always comes with a diluent:

| Clear outcomes | Oxygen and nitrogen only | With carbon dioxide | With helium |
|---|---|---|---|
| Heptane, about 0.7 atm | 2 | 13 | 10 |
| Heptane, about 1.0 atm | 24 | 16 | 10 |
| Methanol, about 0.7 atm | 4 | 31 | 12 |
| Methanol, about 1.0 atm | 37 | 28 | 12 |

The Moon Base preset is plain oxygen and nitrogen at 0.69 atm: the two smallest cells.

Nine tests above 1.1 atm (2.0 to 3.05 atm) are outside the model's scope. Adding
them to the refits settles the direction for methanol (more pressure, more likely to
go out, in 99 % of refits against 87 % without them) and not for heptane (50 %). The
page keeps flagging pressure as unsettled for both fuels, which is the cautious side.

## 7. Time to consume the droplet

The page divides the droplet's diameter squared by the modelled burning rate. For
the 27 tests that burned to completion, that time (with the rate held out) is a
median 1.18 times NASA's burn time, middle half 0.94 to 1.42, range 0.87 to 3.3.
NASA's own measured rate gives 1.17, so most of the gap is the rule, not the model.
Read "about".

## 8. Smaller things

- **The tested range pools both fuels.** Oxygen 12 to 34 % (heptane starts at 13),
  carbon dioxide up to 50 % (heptane 45), droplet 1.1 to 4.67 mm (methanol 1.61 to
  4.53). Tried on the page: heptane at 48 % carbon dioxide is caught by the
  nearest-test check, which uses the chosen fuel's tests only ("Far from any real
  test"). A methanol droplet of 1.3 mm is not: it reads "Inside the tested range",
  because the closest methanol test, at 1.61 mm, counts as near. Not changed here:
  with per-fuel ranges the Moon Base preset, 0.694 atm, would sit 0.001 atm below the
  lowest heptane test (0.695 atm) and turn red for no real reason.
- **Most tests have a twin.** 185 of 199 clear outcomes share fuel, gas mix and
  pressure level with another test. That is why the held-out numbers were also
  computed with whole gas mixes held out (AUC 0.900, `model/per_fuel/comparison.json`).
  In 15 of the 70 groups both outcomes occur: there droplet size or chance decides.
- **No separate test set.** PSI has no other table with per-test heptane or methanol
  droplet outcomes: the FLEX-2 table lists its test matrix, not tests, and CFI burned
  other fuels. So the model was chosen and scored on the same tests, as the
  documents say.
- **No variable left unused.** NASA's FLEX table gives the fuel, the pressure, the
  gas mix and the droplet size before ignition. The model uses all of them. Things
  the table does not record (a support fibre, the igniter) cannot be checked.

## How this was checked

- `tests/test_per_fuel_model.py`: a re-run reproduces the export and the metrics;
  the exported disruption formula gives the fitted model's predictions; the page's
  own code gives the same disruption chance and the same range as Python on 652
  inputs; an export without the new fields still works and shows neither.
- `tests/test_design_audit.py`: the counts in `design_audit.json` are recomputed
  from the cleaned table, and its readings from the export.
- `tests/test_console_features.cjs` and the 40 browser scenarios check the new
  numbers on the page against the exported coefficients.
- Not checked: any of this on the real handheld.

## Use of AI

The audit, the code and this document were written with Claude (Anthropic) at the
team owner's request. No data value was generated or changed by AI.
