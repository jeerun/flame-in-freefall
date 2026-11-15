# Project context

Handoff notes so a new Claude session can pick this project up without the
earlier conversation. Written Saturday Nov 14, 2026, about 8:35 PM Mountain Time.
Update the Status section whenever something lands.

## How to work with this team

- The repo owner writes in Thai, often from a phone. Reply in Thai, short, answer first.
- Anything the team or the judges read (README, docs, form text, UI text) is in English.
- Time is the constraint. Prefer the smallest thing that works over the best thing.
- Be honest about what is real. Never present mock or unverified numbers as results.

## What we are building

Team Second Toe (5 people), 2026 NASA Space Apps Challenge, Universal Event.
Challenge: "Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity
Combustion Data" (the site spells it SI-Powered).

A handheld fire-safety console for spacecraft crew. The user sets fuel, oxygen,
pressure, carbon dioxide and droplet size. The console shows the chance a droplet
flame keeps burning, the burning rate, a plain-language explanation, and a clear
warning when the settings fall outside what the experiments tested.

Hardware the team wants to show off:
- RTX 5080 PC: data cleaning and model training in Python.
- Lenovo Legion Go: runs the console offline as one HTML page, driven by its gamepad.

## Deadline and checkpoints

Submission closes Sunday Nov 15, 11:59 PM in the team owner's local time
(Mountain, UTC-7). Confirm the time on the team page. "Submit for Judging" is final.

- Midnight Sat: clean CSV and a first chart exist. If not, switch challenge to
  Space Mission Design Game.
- 8 AM Sun: `console/model.js` exported from real data.
- 10 AM: console shows real numbers, mock banner gone.
- 2 PM: feature freeze.
- 6 PM: demo video and form text done.
- 9 PM: submit.

## Status

Last updated Saturday Nov 14, about 9:00 PM Mountain Time.

Done:
- Team created on the Space Apps site, challenge selected.
- This repo created (public) with the folder skeleton.
- `console/index.html` works on mock numbers. Checked in headless Chrome with
  keyboard input and a simulated gamepad. Fits 1280x680 and 1280x800.
- FLEX data is in `data/raw/psi69_flex_experimental_table.tsv` (see Data below
  for how it was obtained).
- `data/clean/build_clean.py` builds `data/clean/flex_clean.csv` (274 tests).
- `model/train.py` has been run once. Numbers are in `model/metrics.json`.
  Nobody has reviewed that script or its output yet.

Not done:
- `console/model.js` is NOT committed on purpose. The console has not been wired
  to the real model or checked with it, so it must keep showing the mock banner.
- Console has not been tried on the real Legion Go yet. If the gamepad moves the
  mouse instead, the device is in desktop mode and needs gamepad mode.
- Teammates still need to join the team on the Space Apps site. Join requests only
  work while the team's "looking for members" box is ticked; untick it after all
  five are in. Teammates must also be invited to this repo as collaborators.
- Nobody has read the official challenge page closely yet. Do that before adding features.
- `docs/sources.md` and `docs/submission.md` are still empty templates.

## Next steps, in order

1. Review `model/train.py` and `model/metrics.json`. Then run, from the repo root:
   `python data/clean/build_clean.py` and `python model/train.py`
   (needs pandas, numpy, scikit-learn). This writes `console/model.js`.
2. Wire the console to the real model. The model now has a fifth input, helium,
   and extra fields. In `console/index.html`:
   - The helium row appears by itself (rows are built from `features`), but the
     "rest of the air is nitrogen" note must subtract helium too, and should warn
     if the gases add up to more than 100%.
   - Use `meta.exclusive` ([["co2","he"]]): no test mixed CO2 and helium, so both
     above zero counts as outside the tested range.
   - Use `tests` and `meta.far_distance` to find the closest real test (same fuel,
     range-normalised distance). Show it in the explanation panel, and warn when
     the closest test is farther than `far_distance`.
   - Fix the wording. "Extinction" in FLEX means the flame went out before the
     fuel was gone; "Completion" means it burned until the fuel was gone. The
     headline should say "burns until the fuel is gone", not "keeps burning".
   - Show the held-out accuracy (`meta.auc`, `meta.burn_rate_mae`) in the fine print.
   - Check that six rows still fit at 1280x680.
3. Open the console in a browser with `model.js` present, check the numbers and
   warnings make sense, then commit `console/model.js`.
4. Fill `docs/sources.md` and `docs/submission.md`, including the accuracy numbers.
5. Try the console on the Legion Go.
6. Film the 30-second demo on the Legion Go.

## Data

NASA Physical Sciences Informatics, PSI-69, Flame Extinguishment Experiment (FLEX),
version 5. https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
DOI 10.60555/mbq8-0451. Listed licence CC0-1.0.

Columns shown on the PSI page: test number, identifier, date, fuel, ambient pressure
(mmHg), initial O2, N2, CO2 and He as mole fractions, initial droplet diameter (mm),
visible flame extinction diameter (mm), burning rate, burn time (s), test end.

How the raw file was obtained: the downloadable CSV was not fetched. The table
shown on the PSI-69 page was read in a browser, 100 rows per page over three pages,
and saved as tab-separated text. Each page's text was checked by SHA-256 against a
hash computed inside the page, and all three matched. If someone downloads the
official Experimental Table CSV, compare it with this file and keep the official one.

Checked against the file:
- 274 tests, plus one empty row at the end. Methanol 157, heptane 117.
- Test end: Extinction 186, Disruption 61, Completion 27.
- Pressure clusters at about 0.7 atm (103 tests) and 1.0 atm (161 tests). Nine
  early tests sit at 2 to 3 atm, all with 70% CO2. Test 114 has pressure 0, which
  is a bad value.
- O2 12 to 34%. CO2 0 to 70%. Helium 0 to 45%. No test has both CO2 and helium.
- Some cells show a replacement character (unreadable in the source), and two burn
  times are written "~6" and "~9". The cleaning script flags all of these.
- Identifier 193F001 appears twice (tests 70 and 73) with different measurements.

Still unverified: the PSI description says FLEX used both space-based data and
ground-based tests, and the table has no column saying which row is which. Do not
claim that every row is a space experiment.

Decisions made in `model/train.py` (change them if the team disagrees, and say so here):
- Scope is tests at or below 1.1 atm with a known droplet size: 252 tests. The nine
  2 to 3 atm tests are left out because nothing covers 1.1 to 2 atm, so a min-to-max
  range would wrongly look continuous.
- Helium is a model input, because CO2 and helium are the two suppressants FLEX compares.
- Disruption tests are left out of the "goes out" model (the outcome is unknown) but
  kept for the burning-rate model.

First run, held out by repeated 5-fold cross-validation, not yet reviewed:
- "Goes out" model: 199 tests (172 went out, 27 burned to completion). AUC 0.81.
  Accuracy 0.887, against 0.864 for always guessing "goes out". The classes are
  lopsided, so accuracy says little. Quote the AUC and the baseline together.
- Burning-rate model: 252 tests. R2 0.71, mean absolute error 0.048 mm^2/s
  (the values spread about 0.14 mm^2/s).

## Model rules

- Inputs are only things known before ignition. Never use burn time, extinction
  diameter or anything measured after the burn: that leaks the answer.
- Two small models: logistic regression for "flame goes out", linear regression
  for burning rate (mm^2/s). Coefficients must apply to raw values in the console's
  units. Shape of the export is in `model/README.md` and `model/model.example.js`.
- `data_min` and `data_max` in the export are the real column min and max.
- Hold out data, report accuracy on the held-out part, put the numbers in
  `docs/submission.md` whether they are good or bad.
- With a few hundred rows this trains in seconds on a CPU. The 5080 is not needed
  for it. A local LLM that summarizes NASA papers is a stretch goal only.

## Console

`console/index.html` is one self-contained file: no build, no network, no libraries.
It has a built-in mock model and a yellow "Mock numbers" banner. If `console/model.js`
exists next to it and sets `window.FLAME_MODEL`, that replaces the mock and the
banner becomes a "Model: ..." label.

Controls: Up/Down pick a setting, Left/Right change it (hold to repeat), A explain,
B close, Y reset. Touch and keyboard (arrows, Enter, Esc, R) also work.

The flame picture is an illustration, not a simulation, and says so on screen.
The explanation panel says it is a model reading, not a crew procedure. Keep both.

Agreed features: range and confidence warning, gamepad control, explanation panel.
Deliberately cut: flame video analysis, combining several experiments.

## Submission requirements

- Demo: video up to 30 seconds with English subtitles, or up to 7 slides. Hosted
  outside the Space Apps site, public, no login.
- Final project link: this repo, public.
- Form fields, all in English: project name, high-level summary, demo link, final
  project link, detailed description, NASA data, partner and other data, use of AI.
- Must use NASA data to be eligible for global awards.
- Must state where and how AI was used. Claude has been used for planning, the
  console code and this skeleton. Keep the README section current.
- Work must be the team's own. Other teams' repos may be read, never copied from.

## Repo rules

- One owner per folder (see README). Small commits, clear messages.
- `data/raw/` holds files exactly as downloaded. Never edit them.
