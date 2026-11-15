# Flame in Freefall crew fire console

Team Second Toe, 2026 NASA Space Apps Challenge (Universal Event).
Challenge: Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data.

## What it is

A dashboard that summarizes, ranks and interprets NASA's microgravity combustion
investigations for fire safety, built to be driven with a gamepad on a handheld. Its
AI runs on the team's own PC, not in the cloud. It has three pages.

- **NASA research** (the home page) summarizes the 24 combustion investigations in
  NASA's PSI database and ranks them for the question you pick: prevention,
  detection, suppression, or cabin air (the oxygen-rich, low-pressure air planned for
  the Moon Base). The list can be switched to an orbit view: the question sits in the
  middle and the investigations circle it, the most relevant nearest the centre, one
  quarter of the sky per kind of fuel.
- **Flame console** goes deep on one investigation, the Flame Extinguishment
  Experiment (FLEX). Set the fuel, oxygen, pressure, carbon dioxide, helium and
  droplet size, and it shows the chance a droplet flame burns until the fuel is gone,
  the burning rate, and an explanation that ranks the closest real NASA tests. One
  button switches the cabin air to the Moon Base case from the challenge brief. Under
  the reading is a star map: every star is a real FLEX test, its shape and colour say
  how it ended, its size how fast it burned. Point at a star with the right stick to
  read it, replay it from NASA's measurements, or move the settings onto it. The page
  warns when the settings fall outside what the experiments actually tested.
- **Fire drill** is a ten-round game. It shows the settings of a real FLEX test and
  you guess how it ended. It then replays the test, shows NASA's recorded result and
  keeps score, you against the model, with a streak, a rank and a best score.
- **Ember**, the on-board AI, is on every page when the dashboard is served from the
  team's PC. It is a language model running on that PC's RTX 5080. It answers
  questions from the NASA PSI records and the numbers on screen, cites the PSI ids it
  used, and can read its answers aloud. Nothing leaves the local network.

The console numbers come from two small models trained on FLEX (PSI-69). The
research summaries and ranks were written by an AI model from the PSI records and
are labelled as such. It is a study and planning tool, not a crew procedure.

## Status

Working on real data (Nov 14, 2026).

- Done: data cleaned, models trained and reviewed, all three pages and the local AI
  built and checked on the team's PC in a desktop browser, with keyboard and a
  simulated gamepad.
- Not done yet: trying it on the real Lenovo Legion Go (alone and over Wi-Fi to the
  PC), the demo video, the submission form.

## Run it

There are two ways.

**Without the AI, fully offline.** Open `console/index.html` in Edge or Chrome and
press F11. No install, no internet. Keep `console/model.js` and `console/research.js`
next to it. Without `model.js` the page falls back to made-up numbers and shows a
yellow "Mock numbers" banner. Without `research.js` the NASA research page is hidden.

**With the AI, served from the team's PC.** One-time setup on the PC with the GPU:
install Ollama from https://ollama.com and pull the model.

    ollama pull gemma4:12b

Then double-click `Start dashboard.bat` in the repo folder on that PC. It opens the
dashboard in the browser and prints the address to open on the Legion Go. The same
thing by hand, from the repo root:

    py server/serve.py           (this PC only: open http://localhost:8000)
    py server/serve.py --lan     (also the Legion Go on the same Wi-Fi)

The first time, Windows asks whether to let Python through the firewall: allow it on
private networks. The script needs only the Python standard library. If the PC is
off or out of reach, open the file directly as above: everything except Ember still
works.

## Controls

Press A on the start screen. RB and LB turn the page. The Menu button opens Ember,
who answers the first question straight away; Up/Down pick another, A asks it,
B closes.

| Page | Gamepad | Keyboard |
|---|---|---|
| NASA research | Left/Right change the question. Up/Down move through the ranked list. X switches between the list and the orbit view. In the orbit view the right stick points at an investigation. | Arrows, X |
| Flame console | Up/Down pick a setting, Left/Right change it (hold to repeat). A explain, B close, X switch cabin air, Y reset. Right stick picks a star on the map, RT replays that test, pressing the right stick moves the settings onto it. | Arrows, Enter, Esc, X, R, `[` and `]` pick a star, P replay, G go there |
| Fire drill | Left "went out first", Right "burned all its fuel", A next test, Y new game, B home. | Arrows, Enter, R, Esc |
| Everywhere | RB/LB pages, Menu opens Ember. | 1, 2, 3 pages, `/` Ember, V voice on or off (while Ember is open), M sound on or off |

The controller buzzes, an alarm sounds and the flame picture turns into a question
mark when the settings leave what NASA tested. Touch works too. Sound, voice and
rumble depend on the browser and the device: if one is missing, nothing else breaks.

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
| `server/` | 3 Console | `serve.py`: serves the dashboard on the local network and passes questions for Ember to the language model on the PC. |
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

Inside the product, three kinds of AI, each labelled on screen:

- Ember ("Ask Ember"): Gemma 4 (12B, an open model from Google) run locally with Ollama on
  the team's RTX 5080 PC. `server/serve.py` gives it the NASA PSI text for the
  investigations closest to the question, or the reading on screen, and tells it to
  answer only from that and to cite PSI ids. Its answers are written on the spot and
  can be wrong. Nothing is sent to the internet.
- The summaries, "why it matters" lines and 0 to 3 relevance scores on the NASA
  research page were written ahead of time by Claude (Anthropic) from each
  investigation's PSI record (`data/clean/research_notes.json`). Titles, project type
  and hardware are copied from PSI unchanged.
- The predictions on the Flame console page come from plain logistic and linear
  regression, which is machine learning but not generative AI.

While building it we used Claude (Anthropic), an AI assistant: planning, writing the
dashboard code, the server and the data-cleaning and training scripts, reviewing and
re-running them, reading the PSI-69 table and the challenge page, finding sources,
and drafting the documentation.

No AI-generated images, video or audio are used, and no data value was generated or
changed by AI. Keep this section current: the submission form asks where and how AI
was used.
