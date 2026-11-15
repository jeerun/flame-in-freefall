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
pressure, carbon dioxide, helium and droplet size. The console shows the chance a
droplet flame burns until the fuel is gone, the burning rate, a plain-language
explanation, and a clear warning when the settings fall outside what the
experiments tested.

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

The draft PR includes shared research views and FLEX readings. Open a shared URL on
the hosted dashboard, or paste a view code into another offline copy. The Oxygen
map has a mobile layout and an investigation selector. Ignite and Ember use native
dialogs with keyboard focus contained while open.

The evidence preview adds two research activities from Saffire-II and BASS-II and a FLEX counterexample comparison. The Oxygen map counts published table rows, including duplicates. Outcome estimates apply to clear outcomes only, and the Moon preset flags inconclusive nearby tests. Replays require recorded burn time and measured diameters, except for an inferred zero endpoint after fuel completion. The included video is a desktop capture. The notes below record earlier milestones.

Last updated Sunday Nov 15, about 12:15 AM by the owner's PC clock (Pacific Time).

Done:
- Team created on the Space Apps site, challenge selected.
- This repo created (public) with the folder skeleton.
- FLEX data is in `data/raw/psi69_flex_experimental_table.tsv` (see Data below
  for how it was obtained).
- `data/clean/build_clean.py` builds `data/clean/flex_clean.csv` (274 tests).
- Step 1 done: `model/train.py` and `model/metrics.json` reviewed, both scripts
  re-run. See "Review of the first run" under Data for what was checked and the
  caveats that must go into the docs.
- Step 2 done: `console/index.html` is wired to the real model (see Console below
  for what it now does).
- Step 3 done: `console/model.js` is committed. With it present the mock banner is
  gone and the header reads "Model: NASA PSI-69 FLEX, 199 tests". Checked in
  headless Edge at 1280x680 and 1280x800: no scrolling, no clipped text, no page
  errors, numbers match the Python model, every warning fires, keyboard and a
  simulated standard gamepad (d-pad, left stick, A, B, Y, hold to repeat) all work.
  Without `model.js` the page still falls back to the mock model and its banner.

- Step 5 done: `docs/sources.md` is filled. Every source in it was opened and read
  on Nov 14 (the PSI-69 page in a browser, the FLEX requirements PDF as text, the
  NTRS and NASA pages). The explanation panel gained one sourced sentence: "goes
  out" means the visible flame, and FLEX found cool flames after it.

- Step 6 done: `docs/submission.md` drafted for every form field. Two lines are
  marked TO ADD for the owner (demo link, teammates' AI use). The project name
  "Flame in Freefall Crew Fire Console" is a proposal: the owner can change it.
- Step 7 done: `README.md` shows the real status, how to run and rebuild, the data,
  the accuracy and the use of AI.
- Step 8 done: `docs/demo-script.md`, six shots with buttons and subtitles. The
  readings in it were checked in a desktop browser, not on the Legion Go.
- Step 9 done: `docs/checklist.md`. Repo confirmed Public on Nov 14 (opened without
  signing in). The remaining boxes are for the owner.

- Stretch chart done: `docs/make_chart.py` draws `docs/flex_outcomes.png` from the
  cleaned table (test outcome by oxygen and droplet size, one panel per fuel). It
  is in the README. The local LLM stretch has not been started.

- Step 4 done: the official challenge page was read on Nov 14 and compared with
  the build (see "Challenge fit" below). The owner approved three additions.
  Two are in: the cabin-air buttons (X: Earth-like air, Moon Base) and the ranked
  list of the three closest real tests in the explanation panel. Checked in
  headless Edge like step 3, including X on keyboard and gamepad.

- Third approved addition done: the "NASA research" page (LB/RB or key 2). It lists
  the 24 PSI combustion investigations, ranked by relevance to prevention, detection
  or suppression, with a summary card for each. Facts come from
  `data/raw/psi_search/combustion_investigations.json`; the summaries and 0 to 3
  scores are AI-written, in `data/clean/research_notes.json`;
  `data/clean/build_research.py` joins them into `console/research.js`. Checked in
  headless Edge at 1280x680 and 1280x800: no page scrolling, every card fits, the
  list scrolls inside its own box, keyboard and simulated gamepad work.
- `docs/submission.md`, `README.md`, `docs/demo-script.md`, `docs/checklist.md` and
  `docs/sources.md` were rewritten around the challenge wording. The demo script was
  replayed with a simulated gamepad and each shot shows what the script says.

- Local AI done (the owner asked for real AI on the RTX 5080 to earn "SI-powered").
  "Ask the AI" (Menu button, or key /) appears on every page when the dashboard is
  served by `server/serve.py`. That script, standard library only, serves `console/`
  and passes each question to Gemma 4 12B running in Ollama on the owner's PC, with
  the PSI text of the four records closest to the question, or the reading on screen.
  The model is told to answer only from that and to cite PSI ids. Tested on that PC:
  model 100% on the GPU, answers in 1 to 4 seconds after warm-up, it declined a
  question the records cannot answer, the panel works with keyboard and simulated
  gamepad. `Start dashboard.bat` starts it with `--lan --open`.
- Game feel done (the owner asked for simple, easy, playful, game-like). A third page,
  "Fire drill": ten real FLEX tests, five of each outcome, guess with Left or Right,
  score against the model. The flame picture pulses with the burning rate and turns
  into a question mark outside the tested range. The controller buzzes on the red
  state and on a wrong guess. Opening "Ask the AI" asks its first question by itself.
  All checked in headless Edge at 1280x680 and 1280x800 with a simulated gamepad.
- Late evening of Nov 14, at the owner's request ("more fun", "fit the brief", "we
  are going for first place", "something new", "pictures instead of dots", "pick a
  star with the stick", "a simulation"). All of it checked the same way:
  - The pages were reordered to fit the brief: NASA research is the home page, then
    Flame console, then Fire drill. A start screen comes first (A or any key).
  - NASA research: a one-line count of the collection, a fourth ranking question
    "Cabin air" (scores added to `research_notes.json`), an orbit view (X) with a
    small picture per kind of fuel, and the right stick points at an investigation.
  - Flame console: a star map of the real tests under the reading. Right stick picks
    a star, RT replays that test in the flame picture, R3 moves the settings onto
    it (keys `[` `]`, P, G). The replay uses burn time and end diameter, which
    `model/train.py` now adds to each `tests` row in `model.js` for display only.
    The fitted model and `metrics.json` did not change.
  - Fire drill: the reveal replays the test; streak, rank, best score kept in the
    browser; one sentence from Ember after each answer when the PC is reachable.
  - Ember: the AI got a name, reads its answers aloud (V turns the voice off), and
    its prompt now forbids moving a number from the brief onto an investigation,
    after it did that once in testing.
  - Sound effects made in the browser (M mutes) and a moving starfield behind the page.

Not done:
- Nobody on the team has reviewed the AI-written research notes line by line.
- Ember's answers were spot-checked by hand (about twenty), not evaluated formally.
- Sound and voice need one touch, click or key press before a browser will play
  them. Whether a gamepad button alone unlocks them on the Legion Go is untested.
- Reaching the PC from the Legion Go over Wi-Fi has not been tried. It needs the
  owner to answer the Windows firewall prompt on the PC (Allow, private networks).
- Rumble has only been tried with a simulated gamepad.
- Console has not been tried on the real Legion Go yet (a simulated gamepad is not
  the real one). If the gamepad moves the mouse instead, the device is in desktop
  mode and needs gamepad mode.
- Owner only: try the console on the Legion Go, film and upload the demo, fill in
  the Space Apps form (see `docs/checklist.md`).
- Teammates still need to join the team on the Space Apps site. Join requests only
  work while the team's "looking for members" box is ticked; untick it after all
  five are in. Teammates must also be invited to this repo as collaborators.

- Night of Nov 14 to 15, at the owner's request (send the data off the handheld,
  choose where the AI runs with a fallback, notifications, a truer simulation, the
  stick slides the bars because a crew may wear gloves, a detailed chart with levels
  of detail, more NASA data, the scene follows the place, zoom the star map). All of
  it checked in headless Edge at 1280x680 and 1280x800 with a simulated gamepad;
  the server parts with real Ollama on the owner's PC:
  - More NASA data. `data/clean/fetch_psi_tables.py` downloaded the Experimental
    Table of every combustion investigation from PSI (25 files, unchanged, in
    `data/raw/psi_tables/` with `MANIFEST.json`). `data/clean/build_tables.py` reads
    the oxygen and pressure of each test from nine of them into `console/tables.js`
    and `data/clean/psi_tables_summary.json`. Counted: 746 tests with oxygen and
    pressure of the surrounding gas, 20 in Moon Base air (all CFI-G normal flames),
    17 more just above the pressure line at 10.2 to 10.5 psi (all FLEX).
  - Oxygen map (research page: Y, View, or key O). Three levels of detail. Inverse
    flames are hollow and not counted. Works only when `tables.js` is present.
  - Star map zoom (console: View button or key Z). Levels: stars, grid and test
    numbers (labels never overlap; left-out numbers are counted in the fine print),
    the model's 25/50/75 % lines. View no longer toggles sound on the console and
    research pages (M and the chip still do).
  - Cabin air has three buttons: Earth air, Moon Base, Mars (assumed). Mars uses the
    Moon Base air and the explanation says it is an assumption. The background
    scene (drawn, behind solid panels) is the Earth, the Moon or Mars.
  - Ignite (LT or key I): one run of the model, drawn like FLEX footage.
  - Notifications: banner, sound and buzz when the reading leaves or re-enters the
    tested range, the risk turns high (65 % or more), nearby tests disagree, Ember
    loses or regains a machine, a file is saved or sent, a new best score.
  - The left stick slides the selected bar (analog); the d-pad still steps.
  - CSV: "Download tests (CSV)" saves on the device (key D). "Send to base" (left
    stick press, key S) posts it to the server, which keeps it in `exports/` (or the
    folder in `exports-folder.txt` / `--exports`, e.g. a synced Drive folder), passes
    it to the peer machine and serves it at `/tests.csv`. Opened as a file or from
    GitHub Pages the second button is "Share" (the device's share sheet) instead.
  - Ember on two machines: every local Ollama model is a "brain"; `--peer <address>`
    adds the bigger machine's and prefers them; if the peer does not answer the
    question is answered locally and the page says so; the page re-checks every
    20 seconds. `Start on Legion Go.bat` sets this up (asks for the PC address once,
    keeps it in `pc-address.txt`, expects `gemma4:e2b` on the handheld). Checked
    with two servers on the one PC (ports 8000 and 8001), never on a real handheld.
  - Ember is also given the test-table counts and the top two records of the
    dashboard's own ranking for the need on screen. `server/ember_check.py` asks 18
    fixed questions and writes `docs/ember-check.md` with two automatic checks
    (numbers present in the material, PSI ids next to the right names). All 18 pass.
    No person has read them yet.
  - Live copy: https://jeerun.github.io/flame-in-freefall/ , the `console/` folder
    on the `gh-pages` branch. Republish after changing `console/`:
    `git subtree push --prefix console origin gh-pages`.
  - Docs brought up to date: README, `docs/submission.md`, `docs/sources.md`,
    `docs/demo-script.md` (shot 2 is now the Oxygen map), `docs/checklist.md`, the
    two data READMEs.

  - For the owner's test on the handheld (Nov 15, after midnight): `Setup Legion
    Go.bat` (winget installs Python and Ollama, pulls `gemma4:e2b`, 4.3 GB; only its
    "already installed" path was run, on the PC), `docs/legion-go-setup.md`, and in
    the server: "New device connected: <ip>" in the window, `/who` (answered only to
    the machine itself) listing every device with its request counts, and a second
    start that points at the running dashboard instead of failing. This session
    cannot reach the Legion Go: no SSH and no Claude on it.

  - For the Legion Go's own hardware (owner's photo, Nov 15): the mouse wheel turns
    the selected setting and walks lists and stars; a pointer (FPS mode, trackpad,
    mouse) picks a star by hovering, replays on click, moves the settings on
    right-click; the picked star has "Replay" and "Go there" buttons; a suggested
    key layout for the six extra buttons is in `docs/legion-go-setup.md`. Research
    cards show counts from NASA's test tables, Ember lists the records it was given
    and gets NASA's benefits text, overlays size against the screen.
  - Tailscale: the PC and the Legion Go are on one
    tailnet since Nov 15. `tailscale serve --http=80 8000` on the PC passes the
    dashboard on without a firewall change; it answered from the PC itself. The
    server reads the proxy's X-Forwarded-For so `/who` shows the real device.

  - Teammate's pull requests merged on Nov 15 at the owner's word (both additive):
    #1 independent audit (`model/science_audit.py`, `docs/scientific-validation.md`;
    re-run here, same results, 5 of 5 tests pass; key finding: Completion recall
    23.7 % at a 50 % cut-off) and #2 page-versus-Python parity check
    (`model/check_parity.py`, `docs/model-parity.md`; needs Node, not re-run here).
    Both findings are in the README and the submission draft.
  - The owner opened the dashboard on the real Legion Go over Tailscale on Nov 15
    (about 00:47 to 01:14 by the PC clock). Seen from the PC: 118 requests, 26
    questions to Ember all answered (slowest 2.1 s), 4 CSV files received, no server
    errors. What the screen, sound, rumble and buttons did was not visible from here.

  - The owner's zip of Nov 15 (made with ChatGPT/Codex, based on the then-current
    main) is merged: the explanation opens with Prediction, Real-test evidence and
    Limitations, with "Why this prediction?" (X, key W) and "Test details and
    sources" (Y, key T) as sections that open; "Save baseline" and "Compare" (keys H
    and C) show two sets of settings side by side and withhold the difference when
    either is outside the tested range. Changed on the way in: the two buttons sat
    under the settings and pushed the page past the screen (43 px at 680, 18 px at
    800), so they moved into the explanation panel; LT there saves and compares, LT
    in the comparison replaces the baseline, the right stick scrolls an open panel;
    tighter spacing on short screens. `tests/test_console_features.cjs` and the
    teammate's parity tests run here with the Node.js bundled in Playwright
    (`<venv>/Lib/site-packages/playwright/driver/node.exe`): all pass.

Not done, or not verified:
- Everything in the list above is unverified on the real Legion Go, with real
  gloves, and over real Wi-Fi, except what the previous point says.
- The share sheet ("Share" button) cannot be tested in a headless browser.
- `gemma4:e2b` exists in the Ollama library (checked Nov 14) but was never run here.
- Owner or teammate: read `docs/ember-check.md` and fill in the verdict lines.

## Challenge fit (step 4)

Official page: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
(Details and Resources tabs, read Nov 14, 2026).

What it asks for: an interactive, "super intelligence (SI) powered", web-based
dashboard that summarizes, ranks and interprets NASA's microgravity combustion
investigations in the PSI database, to give fire-safety insights for human space
exploration. Teams may let users (1) find the investigations most relevant to crew
habitats, (2) extract data that supports predictive modelling of flammability, and
(3) highlight research that informs fire-safety equipment. The data source is the
PSI repository, combustion science. The page frames fire safety as prevention,
detection and suppression, and says the Moon Base will likely run at 30% oxygen or
more and 10.2 psi or less.

How the build compared before the additions:
- Covered: interactive and web-based; built on PSI data; interprets in plain
  language; predictive modelling of flammability (option 2) from FLEX, the
  suppression investigation the page names; honest about the tested range.
- Gap: only one investigation (FLEX) of the 24 combustion ones in PSI.
- Gap: nothing was ranked.
- Gap: no AI inside the product. The models are plain regressions.
- Gap: no link to the crew atmospheres the page talks about.

What closes the gaps (owner approved all three on Nov 14):
- Cabin-air buttons with the Moon Base case from the page. Done.
- Ranked closest real tests. Done.
- "NASA research" page: all PSI combustion investigations, summarized and ranked by
  relevance to prevention, detection or suppression. Summaries and ranks are
  written by an AI model from the PSI records and labelled as such. Done.

Added after the owner asked whether this was enough for "SI-powered": a language
model running on the team's own RTX 5080 PC ("Ask the AI"), and a game page.

Still not covered, and not planned: comparing raw data across investigations, and
partial-gravity data (PSI has none yet).

## Next steps, in order

The repo owner set this list on Nov 14. Commit and push to main after each step,
and update Status above each time.

1. DONE. Review `model/train.py` and `model/metrics.json` for leaks, then run from
   the repo root `python data/clean/build_clean.py` and `python model/train.py`
   (needs pandas, numpy, scikit-learn). The numbers must match `metrics.json`.
2. DONE. Wire `console/index.html` to the real model.
3. DONE. Check the console in a browser with `model.js`, then commit `model.js`.
4. DONE (comparison and the three approved additions, see Status). Compare
   the official challenge page with what we built, and propose the smallest thing
   that closes any gap.
5. DONE. Fill `docs/sources.md`: NASA dataset, DOI, link, download date, and a source
   for every sentence shown on screen. If the wording on screen changes, update the
   claims table in that file too.
6. DONE (draft, revisit after step 4). Fill `docs/submission.md` in English, every
   form field, with the accuracy numbers and the use of AI.
7. DONE. Update `README.md`: real status, how to run, data used, use of AI.
8. DONE. Write the 30-second demo script with English subtitles, shot by shot, with
   the buttons to press on the Legion Go: `docs/demo-script.md`.
9. DONE. Pre-submission checklist: `docs/checklist.md`.

Only the owner can do these: try the console on the Legion Go, film the demo, fill
in the Space Apps site. Stop and list them when they come up.

Stretch, only if steps 1 to 7 are done before 2 PM Sunday: one chart from the real
data for the README; a local LLM on the RTX 5080 that summarizes NASA papers.

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

Review of the first run (Nov 14, step 1):
- No leak. The only inputs are fuel, O2, pressure, CO2, helium and initial droplet
  diameter. Burn time, extinction diameter and burning rate are never inputs.
- Re-running both scripts reproduces `flex_clean.csv` and `metrics.json` exactly.
- The exported raw-unit coefficients give the same predictions as the fitted
  scikit-learn models (differences below 0.00002, from rounding).
- Replicates do not inflate the score: keeping all tests with the same fuel and gas
  mix in one fold gives AUC 0.80 and R2 0.70, close to the reported numbers.
- In-scope ranges: O2 12 to 34%, pressure 0.69 to 1.02 atm, CO2 0 to 50%,
  helium 0 to 45%, droplet 1.1 to 4.67 mm. The 22 tests left out are 9 above
  1.1 atm, 1 with no pressure and 12 with no droplet size.
- Caveat to state in the docs: the "goes out" model separates heptane tests well
  (AUC about 0.81 within heptane, 56 went out, 19 completed) but barely separates
  methanol tests (about 0.60 within methanol, 116 went out, only 8 completed).
- Caveat: pressure only sits at about 0.7 and 1.0 atm, so its effect is weakly known.
- The straight-line burning-rate model can dip just below zero at the far corner of
  the sliders. The console clamps it at zero, and that corner is outside the tested range.

First run, held out by repeated 5-fold cross-validation:
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

What the wired console does (all of it reads from `model.js`, nothing is hard-coded):
- Headline is the chance the flame burns until the fuel is gone (FLEX "Completion"),
  with the chance it goes out first (FLEX "Extinction") under it.
- Red "outside the tested range" state, which also dims the numbers, when a setting
  is past its `data_min`/`data_max`, when CO2 and helium are both above zero
  (`meta.exclusive`), or when O2 + CO2 + helium add up to more than 100%.
- The nitrogen note sits on the helium row and is 100 minus O2, CO2 and helium.
- Amber "far from any real test" when the closest same-fuel test is farther than
  `meta.far_distance`, for example pressure between the 0.7 and 1.0 atm clusters.
- Amber "nearby real tests disagree with the model" when most nearby tests with a
  clear outcome went the other way from the model.
- The green state says how many nearby real tests burned until the fuel was gone.
- The explanation panel names the closest real test and how it ended, counts how
  the nearby tests ended, and shows the held-out AUC and burning-rate error.
- Below 720 px of height the spacing tightens so six rows fit at 1280x680.

How it was checked: a Playwright script driving headless Edge (kept outside the
repo). Held-out model percentages were also compared with what the tests did:
under 10% predicted, 4% completed (115 tests); 10 to 20%, 7% (30); 20 to 35%, 13%
(30); 35 to 65%, 67% (21); above 65%, 2 of 3. The model rarely goes above 65%.
It misses four methanol tests at 0.7 atm with 20 to 30% CO2 that burned to
completion (it gives them under 5%); the nearby-test count on screen shows them.

Three pages in this order: NASA research (home), Flame console,
Fire drill. RB goes forward, LB back, keys 1 to 3 jump. Menu (or key /) opens Ember,
the AI, when the page is served by `server/serve.py`. The full control table is in
the README; keep the two in step.

Controls in short. NASA research: Left/Right change the question, Up/Down move
through the ranked list, X switches list and orbit view, right stick points at an
investigation in the orbit view. Flame console: Up/Down pick a setting (or scroll
the explanation while it is open), Left/Right change it (hold to repeat), A explain,
B close, X switch cabin air, Y reset, right stick picks a star, RT replays it, R3
moves the settings onto it. Fire drill: Left "went out first", Right "burned all its
fuel", A next, Y new game, B home. In Ember's panel: Up/Down pick a question, A asks,
B closes, V voice. M mutes the sound effects.

Honesty rules for the new pieces: a star is a drawing of one real test (shape and
colour from "Test end", size from the measured burning rate); a replay plays back
NASA's start diameter, end diameter and burn time and says the glow is an
illustration; a test with no end diameter on record is not replayed; the orbit view
shows the same AI-written ranks as the list; Ember's lines are always labelled as
the AI's.

Tests live outside the repo (Playwright scripts driving headless Edge). When the
page changes, the things worth re-checking are: nothing scrolls at 1280x680 and
1280x800 on any page, the top bar stays on one line with the Ember button showing,
the explanation panel does not overflow, and the page still works opened as a file
with `model.js` only, with nothing but `index.html`, and with `#title` to show
the optional start screen. Opening the dashboard normally goes straight to research.

Running the local AI: Ollama 0.40 and the model `gemma4:12b` (8 GB) are installed
on the owner's PC (ASUS ROG, RTX 5080 16 GB). `py server/serve.py` serves
http://localhost:8000; add `--lan` for the Legion Go, `--open` to open the browser;
`Start dashboard.bat` does both. Opened as a file, the page has no AI button and
everything else works. Keep it that way: the AI must stay an extra, never a
requirement.

Fire drill honesty rules: the tests and outcomes are real PSI-69 rows; the ten are
five "Completion" and five "Extinction", so one answer every time cannot win; the
model was trained on these tests and the page says its score there is a head start,
not accuracy.

The Moon Base button sets oxygen 30% and 10.2 psi from the challenge brief. It
stores 0.694 atm, not the slider step 0.69, because 0.69 falls just under the
lowest pressure FLEX tested (about 0.6925 atm) and would be flagged as untested.

The flame picture is an illustration, not a simulation, and says so on screen.
The explanation panel says it is a model reading, not a crew procedure. Keep both.

Agreed features: range and confidence warning, gamepad control, explanation panel,
cabin-air presets, ranked closest tests, the NASA research page with its orbit view,
Ember (a local model, with voice), the Fire drill game, the star map with replay,
the start screen, sound, rumble and the animated flame picture.
Feature freeze was set for 2 PM Sunday. After that: fixes from the Legion Go test only.
Deliberately cut: flame video analysis, combining the raw data of several experiments.

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
