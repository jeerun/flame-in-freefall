# Flame in Freefall crew fire console

Team Second Toe, 2026 NASA Space Apps Challenge (Universal Event).
Challenge: Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data.

## What it is

A handheld console for studying fire risk in a spacecraft cabin. Set the fuel,
oxygen, pressure, carbon dioxide, helium and droplet size, and it shows the chance a
droplet flame burns until the fuel is gone, the burning rate, and a plain-language
explanation that names the closest real NASA test. It warns when the settings fall
outside what the experiments actually tested.

The numbers come from two small models trained on NASA's Flame Extinguishment
Experiment (FLEX, PSI-69). It is a study and planning tool, not a crew procedure.

## Status

Working on real data (Nov 14, 2026).

- Done: data cleaned, models trained and reviewed, console wired to the real model
  and checked in a desktop browser with keyboard and a simulated gamepad.
- Not done yet: trying it on the real Lenovo Legion Go, the demo video, the
  submission form.

## Run the console

Open `console/index.html` in Edge or Chrome and press F11. No install, no internet.
Keep `console/model.js` next to it: that file holds the real model. Without it the
page falls back to made-up numbers and shows a yellow "Mock numbers" banner.

Controls: Up/Down pick a setting, Left/Right change it (hold to repeat), A explain,
B close, Y reset. Touch and keyboard also work (arrows, Enter, Esc, R).

## Rebuild the model

Needs Python with pandas, numpy and scikit-learn. From the repo root:

    python data/clean/build_clean.py
    python model/train.py

The first builds `data/clean/flex_clean.csv` from the raw table. The second trains
both models, writes `model/metrics.json` and exports `console/model.js`. The results
are seeded, so a re-run gives the same numbers.

## Data

NASA Physical Sciences Informatics, PSI-69, Flame Extinguishment Experiment (FLEX),
version 5, Experimental Table. DOI 10.60555/mbq8-0451, licence CC0-1.0.
https://psi.nasa.gov/physci/repo/data/investigations/PSI-69

Read from the table shown on that page on Nov 14, 2026: 274 droplet combustion tests
(methanol 157, heptane 117). 252 are used: pressure at or below 1.1 atm with a known
droplet size. Details in `data/raw/README.md` and `data/clean/README.md`. Every
source, and where each sentence on screen comes from, is in `docs/sources.md`.

## How good is the model

Measured on tests held out of training (5-fold cross-validation, repeated 20 times):

| Model | Tests | Result |
|---|---|---|
| Does the flame go out before the fuel is gone (logistic regression) | 199 | AUC 0.81. Accuracy 0.887, against 0.864 for always answering "goes out". |
| Burning rate in mm²/s (linear regression) | 252 | Mean absolute error 0.048, R² 0.71. The values spread about 0.14. |

Known limits: the outcome model is much weaker for methanol than for heptane (only
8 of 124 methanol tests burned to completion); pressure sits at only two levels;
"goes out" means the visible flame only. More in `docs/submission.md`.

## Folders, and who owns each

| Folder | Owner (role) | What goes here |
|---|---|---|
| `data/raw/` | 1 Data | Files exactly as downloaded from NASA PSI. Never edit these. |
| `data/clean/` | 1 Data | One tidy CSV built from the raw files, plus notes on each column. |
| `model/` | 2 Model | Training script. It writes `console/model.js`. |
| `console/` | 3 Console | `index.html`, the page that runs on the Legion Go, and `model.js`. |
| `docs/sources.md` | 4 Science | Every NASA dataset and source we use. |
| `docs/submission.md` | 5 Submission | Draft text for the submission form. |
| `docs/demo-script.md`, `docs/checklist.md` | 5 Submission | Demo video script and the pre-submission checklist. |

One owner per folder. If you need a change in someone else's folder, ask them.

## Working together

1. Pull before you start. Push small changes often.
2. Stay in your own folder.
3. Not using git? On github.com open your folder, then Add file > Upload files.
4. Stuck for more than 30 minutes? Say so in the group chat.

## Use of AI

We used Claude (Anthropic), an AI assistant, for planning, for writing the console
code and the data-cleaning and training scripts, for reviewing and re-running them,
for reading the PSI-69 table from the NASA page into a file, for finding sources, and
for drafting the documentation. No AI-generated images, video or audio are used. The
models inside the console are plain logistic and linear regression, not generative
AI, and no data value was generated or changed by AI. Keep this section current: the
submission form asks where and how AI was used.
