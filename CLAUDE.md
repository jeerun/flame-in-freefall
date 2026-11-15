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

Done:
- Team created on the Space Apps site, challenge selected.
- This repo created (public) with the folder skeleton.
- `console/index.html` works on mock numbers. Checked in headless Chrome with
  keyboard input and a simulated gamepad. Fits 1280x680 and 1280x800.

Not done:
- Console has not been tried on the real Legion Go yet. If the gamepad moves the
  mouse instead, the device is in desktop mode and needs gamepad mode.
- FLEX data is not downloaded yet. This blocks the model.
- Teammates still need to join the team on the Space Apps site. Join requests only
  work while the team's "looking for members" box is ticked; untick it after all
  five are in. Teammates must also be invited to this repo as collaborators.
- Nobody has read the official challenge page closely yet. Do that before adding features.

## Next steps, in order

1. Download the FLEX experimental table (CSV) into `data/raw/`.
2. Write `data/clean/` from it: one tidy CSV, units converted, column notes.
3. Train the two models in `model/`, report held-out accuracy, export `console/model.js`.
4. Open the console with the real `model.js`, check the range warning uses real min/max.
5. Fill `docs/sources.md` and `docs/submission.md`.
6. Film the 30-second demo on the Legion Go.

## Data

NASA Physical Sciences Informatics, PSI-69, Flame Extinguishment Experiment (FLEX),
version 5. https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
DOI 10.60555/mbq8-0451. Listed licence CC0-1.0.

Columns shown on the PSI page: test number, identifier, date, fuel, ambient pressure
(mmHg), initial O2, N2, CO2 and He as mole fractions, initial droplet diameter (mm),
visible flame extinction diameter (mm), burning rate, burn time (s), test end.

Unverified, taken from other teams' public READMEs. Check each against the file:
- 274 tests.
- Test end is one of Extinction, Disruption, Completion.
- Fuels are methanol and n-heptane, pressure only about 0.7 to 1 atm.
- The dataset mixes space and ground tests and has no column saying which is which.

Consequences for us:
- Convert mmHg to atm and mole fraction to percent so they match the console.
- Helium is a diluent in the data but not a console input yet. Decide: add it, or
  restrict training to rows without helium. Write the choice down.
- Decide how to treat Disruption rows (probably exclude) and write it down.
- If pressure really spans only 0.7 to 1 atm, the pressure slider will mostly sit
  outside the tested range. That is fine and is what the warning is for, but the
  default and the slider limits in `model.js` should reflect the real data.

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
