# Submission form draft

Everything in English. Deadline: Sunday Nov 15, 11:59 PM, team owner's local time
(confirm on the team page). "Submit for Judging" is final.

Status of this draft: written Nov 14 before the official challenge page was compared
line by line (step 4). Adjust the summary and description if that comparison finds a gap.
Lines marked TO ADD need the owner.

## Project name

Flame in Freefall Crew Fire Console

## High-level project summary

A handheld console for studying fire risk in a spacecraft cabin. The user sets the
fuel, oxygen, pressure, carbon dioxide, helium and droplet size with a gamepad. Two
small models trained on 252 real tests from NASA's Flame Extinguishment Experiment
(FLEX, PSI-69) answer one question: if a droplet of liquid fuel ignites in this
atmosphere, will the flame burn until the fuel is gone, or go out first, and how fast
does it burn? Every reading comes with a plain-language explanation that names the
closest real NASA test and how it ended. When the settings leave what FLEX actually
tested, the console says so in red instead of guessing. It runs offline as one web
page on a Lenovo Legion Go.

## Link to project demo
Video up to 30 seconds with English subtitles, or up to 7 slides. Public link, no login.

TO ADD: public video link, after filming on the Legion Go (script in `docs/demo-script.md`).

## Link to final project
The public GitHub repo. No login needed to view.

https://github.com/jeerun/flame-in-freefall

## Detailed project description
What it does, how it works, what benefit it has, what tools and languages we used.

**What it does.** On the left the user sets six things: fuel (heptane or methanol),
oxygen, pressure, carbon dioxide, helium and the initial droplet diameter. On the
right the console shows:

- the chance the flame burns until the fuel is gone, and the chance it goes out first;
- the burning rate in mm²/s, and how long the droplet would last at that rate;
- a confidence box: green inside the tested range, amber when no real test is close
  or when nearby real tests disagree with the model, red when the settings are
  outside what FLEX tested;
- an explanation panel (button A) that says which settings push the result which way,
  names the closest real FLEX test and how it ended, counts how the nearby tests
  ended, and states the model's measured accuracy.

**How it works.**

1. Data. The FLEX Experimental Table from NASA PSI-69: 274 droplet combustion tests.
   A script cleans it without removing rows or guessing values, and flags unreadable
   cells. 252 tests are in scope (pressure at or below 1.1 atm, known droplet size).
2. Models. Two deliberately small models, so that every number can be explained:
   a logistic regression for "the flame went out before the fuel was gone" against
   "it burned until the fuel was gone", and a linear regression for the burning
   rate. Inputs are only things known before ignition. Burn time and extinction
   diameter are never inputs, because they would leak the answer.
3. Export. The training script writes the coefficients, the tested range of every
   input and the list of real tests into one small JavaScript file.
4. Console. One HTML file with no libraries and no network access reads that file.
   It works with a gamepad, touch or keyboard and fits a 1280x680 screen.

**How we keep it honest.**

- The tested range of each input is the real minimum and maximum in the data. Outside
  it, the numbers are dimmed and the console says the risk is unknown.
- No FLEX test mixed carbon dioxide and helium, so setting both counts as untested.
- Gas settings that add up to more than 100% are rejected.
- Inside the range, the console still measures the distance to the closest real test
  and warns when it is far, for example between the two pressure levels FLEX used.
- If most nearby real tests ended the other way from the model, the console says so
  and tells the user to trust the tests.
- Accuracy is measured on tests held out of training and shown on screen.

**Results, on held-out tests** (5-fold cross-validation repeated 20 times):

- Flame outcome, 199 tests (172 went out, 27 burned until the fuel was gone):
  AUC 0.81. Accuracy 0.887, against 0.864 for always answering "goes out". The two
  outcomes are lopsided, so the AUC is the fairer number.
- Burning rate, 252 tests: mean absolute error 0.048 mm²/s, R² 0.71. The measured
  values spread about 0.14 mm²/s around their mean.
- Keeping repeat tests at the same conditions together in one fold gives almost the
  same numbers (AUC 0.80, R² 0.70).
- When the console says under 10%, 4% of those tests burned to completion; at
  35 to 65%, 67% did. The model rarely goes above 65%.

**Limits we know about.**

- The outcome model separates heptane tests well (AUC about 0.8 within heptane) and
  methanol tests poorly (about 0.6): only 8 of 124 methanol tests burned to completion.
  It gives under 5% to four methanol tests in 20 to 30% carbon dioxide at 0.7 atm that
  did burn to completion. The nearby-test count on screen shows them.
- Pressure sits at only two levels, about 0.7 and 1.0 atm, so its effect is weakly known.
- "Goes out" means the visible flame. FLEX found that fuel can keep reacting afterwards
  in a cool flame, which this console does not model.
- The PSI-69 page says the investigation used both space-based data and ground-based
  tests, and the table does not mark which row is which. We do not claim every row is
  a space experiment.
- It is a study and planning tool, not a crew procedure. The flame picture is an
  illustration, not a simulation.

**Benefit.** FLEX produced hundreds of careful measurements that are hard to read as
a table. The console turns them into something a crew member, student or mission
planner can explore by hand in seconds, and it always shows where the data stops.

**Tools and languages.** Python (pandas, NumPy, scikit-learn) for cleaning and
training. HTML, CSS and plain JavaScript with the browser Gamepad API for the console.
Git and GitHub. Trained on a desktop PC in seconds; shown on a Lenovo Legion Go.

## NASA data
Copy from docs/sources.md.

NASA Physical Sciences Informatics (PSI), investigation PSI-69, Flame Extinguishment
Experiment (FLEX), version 5, Experimental Table. DOI 10.60555/mbq8-0451, licence
CC0-1.0. https://psi.nasa.gov/physci/repo/data/investigations/PSI-69

We used the table of 274 droplet combustion tests: fuel, ambient pressure, initial
oxygen, carbon dioxide and helium fractions and initial droplet diameter as model
inputs, and the "Test end" and "Burning rate" columns as what the models predict.
The console also shows individual tests from this table as the "closest real test".

NASA pages and documents we used for the wording on screen (full list with what we
took from each in `docs/sources.md`):

- FLEX Research Requirements Document, NASA Glenn, 2005.
  https://www1.grc.nasa.gov/wp-content/uploads/FLEX_EIRD_v4.pdf
- "Methanol Droplet Combustion in Oxygen-Inert Environments in Microgravity", NASA
  NTRS 20130014061. https://ntrs.nasa.gov/citations/20130014061
- "Studying Combustion and Fire Safety", NASA, 2023.
  https://www.nasa.gov/missions/station/iss-research/studying-combustion-and-fire-safety/
- "Fire in Space", NASA Astronomy Picture of the Day, Aug 10, 2021.
  https://science.nasa.gov/image-article/apod-2021-august-10-fire-in-space/
- "Mechanisms of droplet combustion", NASA NTRS 19820015551.
  https://ntrs.nasa.gov/citations/19820015551

## Space agency partner and other data

None. The project uses NASA data only. Software: Python, pandas, NumPy and
scikit-learn (open source).

## Use of artificial intelligence
Where and how we used AI. Copy from the README and add anything new.

We used Claude (Anthropic), an AI assistant, for:

- planning the project and the repository layout;
- writing the console (`console/index.html`);
- writing the data-cleaning and training scripts, then reviewing them and re-running
  them to confirm the numbers;
- reading the PSI-69 table from the NASA page into a file (checked page by page with
  SHA-256 hashes) and finding the NASA sources listed in `docs/sources.md`;
- drafting the documentation and this form text.

No AI-generated images, video or audio are used. The models inside the console are a
plain logistic regression and a plain linear regression, not generative AI. No data
value was generated or changed by AI: every number on screen comes from the NASA
table or from the two regressions trained on it.

TO ADD (owner): anything teammates did with AI tools outside this repo.

## Model accuracy (for the description)
Held-out accuracy for "does the flame go out": AUC 0.81; accuracy 0.887 against 0.864 for always answering "goes out" (199 tests, 5-fold cross-validation repeated 20 times).
Held-out error for burning rate: mean absolute error 0.048 mm²/s, R² 0.71 (252 tests).
Number of tests used: 252 of the 274 in the table (199 for the flame outcome, 252 for burning rate).
