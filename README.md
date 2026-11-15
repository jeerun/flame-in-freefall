# Flame in Freefall crew fire console

Team Second Toe, 2026 NASA Space Apps Challenge (Universal Event).
Challenge: Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data.

## What it is

An offline, gamepad-driven dashboard that turns NASA's microgravity combustion data
into fire-safety answers. It has two pages.

- **NASA research** summarizes and ranks the 24 combustion investigations in NASA's
  PSI database by what you need: preventing a fire, detecting it, or putting it out.
- **Flame console** goes deep on one of them, the Flame Extinguishment Experiment
  (FLEX). Set the fuel, oxygen, pressure, carbon dioxide, helium and droplet size,
  and it shows the chance a droplet flame burns until the fuel is gone, the burning
  rate, and a plain-language explanation that ranks the closest real NASA tests. One
  button switches the cabin air to the Moon Base case from the challenge brief. It
  warns when the settings fall outside what the experiments actually tested.

The console numbers come from two small models trained on FLEX (PSI-69). The
research summaries and ranks were written by an AI model from the PSI records and
are labelled as such. It is a study and planning tool, not a crew procedure.

## Status

Working on real data (Nov 14, 2026).

- Done: data cleaned, models trained and reviewed, both pages built and checked in a
  desktop browser with keyboard and a simulated gamepad.
- Not done yet: trying it on the real Lenovo Legion Go, the demo video, the
  submission form.

## Run it

Open `console/index.html` in Edge or Chrome and press F11. No install, no internet.
Keep `console/model.js` and `console/research.js` next to it. Without `model.js` the
page falls back to made-up numbers and shows a yellow "Mock numbers" banner. Without
`research.js` the NASA research page is hidden.

Controls on the Flame console page: Up/Down pick a setting, Left/Right change it
(hold to repeat), A explain, B close, X switch cabin air, Y reset. LB or RB switches
page. On the NASA research page: Left/Right change the question, Up/Down move through
the list, B goes back. Touch and keyboard also work (arrows, Enter, Esc, X, R, 1, 2).

## Rebuild

Needs Python with pandas, numpy and scikit-learn. From the repo root:

    python data/clean/build_clean.py
    python model/train.py
    python data/clean/build_research.py

The first builds `data/clean/flex_clean.csv` from the raw table. The second trains
both models, writes `model/metrics.json` and exports `console/model.js`. The results
are seeded, so a re-run gives the same numbers. The third joins the PSI records with
the notes in `data/clean/research_notes.json` and writes `console/research.js`.

## Data

All from NASA Physical Sciences Informatics (PSI), the source named by the challenge.

- PSI-69, Flame Extinguishment Experiment (FLEX), version 5, Experimental Table.
  DOI 10.60555/mbq8-0451, licence CC0-1.0.
  https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
  Read from the table shown on that page on Nov 14, 2026: 274 droplet combustion
  tests (methanol 157, heptane 117). 252 are used: pressure at or below 1.1 atm with
  a known droplet size.
- The PSI records of the combustion investigations (title, project type, hardware,
  objectives, approach), from the repository's search for "combustion" on
  Nov 14, 2026: 26 records, 24 of them combustion science.
  https://psi.nasa.gov/physci/repo/search?q=combustion

Details in `data/raw/README.md` and `data/clean/README.md`. Every source, and where
each sentence on screen comes from, is in `docs/sources.md`.

![How the 252 in-scope FLEX tests ended, by oxygen and droplet size, for heptane and methanol](docs/flex_outcomes.png)

The chart is drawn from the cleaned table by `python docs/make_chart.py` (needs matplotlib).

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
| `data/clean/` | 1 Data | One tidy CSV built from the raw files, plus notes on each column. Also the research notes and the script that writes `console/research.js`. |
| `model/` | 2 Model | Training script. It writes `console/model.js`. |
| `console/` | 3 Console | `index.html`, the page that runs on the Legion Go, with `model.js` and `research.js`. |
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

We used Claude (Anthropic), an AI assistant.

Inside the product: the summaries, "why it matters" lines and 0 to 3 relevance scores
on the NASA research page were written by Claude from each investigation's PSI
record (`data/clean/research_notes.json`). The page labels them as AI-written.
Titles, project type and hardware are copied from PSI unchanged. The predictions on
the Flame console page come from plain logistic and linear regression, which is
machine learning but not generative AI. No AI model runs on the device.

While building it: planning, writing the dashboard code and the data-cleaning and
training scripts, reviewing and re-running them, reading the PSI-69 table and the
challenge page, finding sources, and drafting the documentation.

No AI-generated images, video or audio are used, and no data value was generated or
changed by AI. Keep this section current: the submission form asks where and how AI
was used.
