# Submission form draft

Everything in English. Deadline: Sunday Nov 15, 11:59 PM, team owner's local time
(confirm on the team page). "Submit for Judging" is final.

The captioned demo was recorded in desktop Edge. The team previously confirmed that a
Lenovo Legion Go could reach the dashboard server, obtain Ember answers and send CSVs.
The handheld's controls, rendering, rumble and on-device model still need verification.

## Project name

Flame in Freefall Crew Fire Console

## High-level project summary

The console ranks 24 investigations from NASA’s Physical Sciences Informatics (PSI)
repository for prevention, detection, suppression or cabin atmosphere. Its Oxygen map
compares nine tables across seven investigations. Of 746 rows with ambient oxygen and
pressure, 20 meet the Moon Base thresholds in the challenge brief. Three activities
let users inspect the underlying evidence: compare Earth and orbital burn lengths,
reveal gas sensor readings and find a comparable droplet test with the opposite outcome.

Two models use the Flame Extinguishment Experiment (FLEX). One estimates completion
versus visible extinction from 199 tests with a clear outcome. The other estimates
burning rate from 252 tests. The dashboard marks settings with little experimental
support. Its optional assistant, Ember, uses Ollama on a configured machine. The
core dashboard and evidence activities open offline.

## Link to project demo
[Watch the captioned desktop demo](https://github.com/jeerun/flame-in-freefall/blob/93d2907764ed7d9ae335e4812acbada5b7f1f653/docs/crew-console-demo.mp4)

## Link to final project
The public GitHub repo. No login needed to view.

https://github.com/jeerun/flame-in-freefall

Previously published browser copy without Ember: https://jeerun.github.io/flame-in-freefall/

The linked demo shows the updated build. Open `console/index.html` from that checkout
to try its three evidence activities.

## Detailed project description
What it does, how it works, what benefit it has, what tools and languages we used.

**The challenge asks for** an interactive, SI-powered, web-based dashboard that
summarizes, ranks and interprets NASA's microgravity combustion investigations for
fire safety. Here is how each word is answered.

**Summarizes: the NASA research page.** It lists the 24 combustion-science
investigations that the PSI repository returns for "combustion" (BASS, Saffire, SAME,
FLEX, FLEX-2, the ACME experiments and others). For each one it shows what the
experiment did, what changed between tests, the kind of fuel, the hardware, and why it
matters for fire safety, in plain language, with the PSI identifier to find it. One
line at the top counts the whole collection by kind of fuel and by flight or ground.

**Ranks: by the question you bring.** NASA's fire-safety work is prevention, detection
and suppression. For Moon Base cabin air the brief anticipates 30% oxygen or more
at low pressure. Pick one of the four and the page ranks
the investigations from "direct" to "related". Choose suppression and BASS and FLEX
come first; choose detection and the smoke experiments SAME and SAME-R come first;
choose cabin air and the ACME Burning Rate Emulator leads, because it tested the
cabin atmospheres NASA considers for crewed missions. The ranking can be shown as a
numbered list or as an orbit view: the question in the middle, each investigation on
a ring set by its relevance, one quarter of the sky per kind of fuel, each drawn with
a small picture of that fuel. Similar investigations end up side by side. On the
Flame console page the same idea is applied to single tests: every reading ranks the
three closest real FLEX tests and shows how each one ended.

**Compares cabin atmospheres.** The Oxygen map reads ambient or burner oxygen from
nine PSI tables for FLEX, CFI, CFI-G, Flame Design, BASS-II, Saffire-I and Saffire-II.
Users can switch from ranges to individual rows to oxygen plotted against pressure.
Of 746 rows with measured ambient oxygen and pressure, 20 CFI-G normal-flame rows
meet both brief thresholds (at least 30% oxygen and at most 10.2 psi). No FLEX row
meets both. Seventeen FLEX rows meet the oxygen threshold at pressures above 10.2
through 10.5 psi. The counts retain eight repeated CFI rows, and FLEX has no
flight/ground label for individual rows. The BASS-II and Saffire tables used here
give no pressure and their recorded oxygen values reach 22.2% at most.

**Earth or orbit?** Four Saffire-II cases show a material's 1-g burn length. Choose
whether the Earth sample burned farther, both burned equally or the orbital sample
burned farther. Reveal the recorded orbital length and compare the two.

**Read the sensors.** Four BASS-II cases show initial and final oxygen. Guess whether
carbon monoxide rose, stayed the same or fell, then reveal the measured CO and CO₂
endpoints. Both activities show the PSI identifier, DOI and CSV line for each case.

**Interprets: the Flame console page.** It takes one investigation, FLEX, and makes its
274-test table something you can explore by hand. Set the fuel (heptane or methanol),
oxygen, pressure, carbon dioxide, helium and droplet size, and the page shows:

- the estimated chances of completion and visible extinction among clear outcomes;
- the burning rate and how long the droplet would last at that rate;
- an evidence box. Amber marks a distant match, inconclusive nearby tests or
  disagreement. Red flags settings beyond the model's scope;
- an explanation that opens with three short boxes, the prediction, the evidence from
  nearby real tests and the limits, and keeps the detail one press away: which
  settings push the result which way, the three closest real tests, how the nearby
  tests ended, and the model's measured accuracy.

**Compare two cabins.** Any set of settings can be saved as baseline A. From then on
the controls change B, and a table shows both side by side: every setting, the two
chances, the burning rate and how well the data supports each, with the difference in
percentage points. The warnings of both stay on screen, and when either set is
outside what NASA tested the difference is withheld instead of shown.

**Find counterexample.** Choose a real FLEX star and look for the opposite recorded
outcome with the same fuel, oxygen, CO₂ and helium. Among eligible pairs, the
dashboard picks the closest pressure and starting diameter after scaling each by
its tested range. It shows both NASA outcomes and both fitted model estimates.
If no pair qualifies, it says so. This comparison makes the limits of similar
conditions visible without assuming which difference caused the outcome.

**A star map of the real tests, and a replay.** Each in-scope FLEX row for the
chosen fuel appears at its oxygen level and droplet diameter. Orange and blue
stars mark completion and extinction, and gray crosses mark disruption.
The map links the current settings to three nearby tests. Eligible replays use
the measured burn time and interpolate diameter squared between endpoints. An
unrecorded completion endpoint is shown as zero for fuel depletion. Missing
burn time or an unrecorded endpoint for extinction or disruption prevents replay.
Zoom adds a grid, test numbers and contours for 25%, 50% and 75% modelled
completion among clear outcomes at the current pressure and gas settings.

**Plays like a handheld game.** It opens directly on NASA research and supports a gamepad,
with sound effects made in the browser. The flame picture breathes
faster as the burning rate rises. When the settings leave what NASA tested, the
controller buzzes, an alarm sounds and the picture turns into a question mark. A
third page, Fire drill, is a ten-round game: it shows the settings of a real FLEX
test, the player guesses whether the flame went out first or burned all its fuel, and
the page replays eligible tests, reveals NASA's recorded result and keeps score, player
against model, with a streak, a rank and a best score. Five of the ten tests burned
all their fuel and five went out, so guessing one answer every time does not win.
It is a quick way to build intuition for what makes a flame survive in microgravity,
and it shows the model's misses as openly as its hits.

One button switches the cabin air between Earth-like air, the Moon Base case from
the challenge brief (oxygen 30% or more at 10.2 psi or less) and a Mars base. The
brief gives no cabin air for Mars, so the Moon Base air is used there and the page
says it is an assumption. The background follows: the Earth from orbit, the lunar
surface, or Mars. FLEX ran tests close to that pressure and oxygen level, so the page
can show both what the model expects there and that the nearest real tests were
inconclusive.

**Ignite.** One button plays a single run of the model full screen. A droplet drawn
with a scale bar shrinks at the predicted burning rate, and whether this run burns all
its fuel is drawn at random with the model's odds, so pressing it a few times shows
what "35%" means. When a run goes out, the size it stops at is borrowed from a real
nearby test. The picture is drawn to look like FLEX footage and is labelled an
illustration. Outside the tested range it refuses to run.

**Controller operation.** A crew member may be wearing gloves. A stick sweep moves
a selected setting across its range. Banners and, on supported devices, sound and
vibration report changes in the evidence, including leaving the input ranges,
finding only inconclusive nearby tests or seeing nearby results disagree with the
model. The team has not tested glove operation.

**Takes the data with you.** The challenge asks for data that supports predictive
modelling. One button saves the 252 in-scope tests with their fitted predictions.
When the team’s server is available, Send to base stores the project CSV there.
An operator can choose a cloud-synced exports folder, in which case the sync
application may transfer the file once connected.

**Where the AI is.** Three places, each stated on screen.

- Ember, the on-board AI, on every page. A language model (Gemma 4, 12 billion
  parameters) runs on the team's own PC with an RTX 5080. The optional two-server
  setup prefers the reachable PC and falls back to the server's own configured
  model. This was tested with two instances on the PC. The intended fallback
  on the handheld itself remains unverified. On the research page Ember answers
  questions such as "For a Moon Base cabin with about 30% oxygen at low pressure,
  which investigations matter most, and why?", "Compare BASS-II with BASS" or "What
  did this investigation measure, and with which instruments?" from the PSI text of
  the investigations closest to the question and the counts from NASA's test tables. On the console page it interprets the
  current reading in plain words, and in the Fire drill it adds one sentence on why a
  test may have ended the way it did. It is told to answer only from the material it
  is given, to cite PSI identifiers, to copy numbers exactly, and to say so when the
  records do not hold the answer. Read-aloud selects an installed English voice
  advertised by the browser as local. If none is available, answers remain on screen.
- The summaries and relevance ranks on the research page were written ahead of time
  by an AI model (Claude) from each investigation's PSI record and stored in the
  page, so they are there even when the PC is not.
- The predictions on the console page come from machine-learning models trained on
  NASA data.

If the PC is switched off, the dashboard still opens as a plain file and everything
except Ember works, fully offline.

**How it works.**

1. Data. From NASA PSI: the FLEX Experimental Table (PSI-69, 274 droplet combustion
   tests), the PSI records returned for “combustion”, and 25 Experimental Table CSVs.
   The manifest records the original downloads’ hashes. Git can normalize line
   endings. `python data/clean/fetch_psi_tables.py --verify` checks the originals’
   hashes offline, restoring CRLF in memory as needed. Of the FLEX rows, 252
   have usable pressure at or below 1.1 atm and a known droplet size.
2. Models. Two deliberately small models, so every number can be explained: a
   logistic regression for "the flame went out before the fuel was gone" against "it
   burned until the fuel was gone", and a linear regression for the burning rate.
   Inputs are only things known before ignition.
3. Export. Scripts write the fitted model, in-scope tests, research notes, oxygen
   map and selected evidence rows as JavaScript data files for offline use.
4. Dashboard. One HTML file with no libraries reads them. It works with a gamepad,
   touch or keyboard and fits a 1280x680 screen.
5. Local AI. A small Python script on the PC serves the dashboard on the local
   network. For each question it picks the PSI records that share the most words with
   the question, adds the top of our own ranking for the need on screen, a one-line
   catalogue of all 24 and the counts from the test tables, and hands that to the
   language model through Ollama. The answer streams back to the handheld. The same
   script keeps the CSV file the handheld sends.

**How we keep it honest.**

- The page checks inputs against the in-scope range of each variable and flags
  unsupported combinations. Beyond that scope it dims the model reading.
- No FLEX test mixed carbon dioxide and helium, so setting both counts as untested.
- Gas settings above 100% in total are flagged as physically impossible.
- Inside the range, the page still measures the distance to the closest real test and
  warns when it is far, or when the nearby tests had no clear outcome.
- Within range, a strong model preference (below 35% or at least 65% completion)
  triggers a disagreement warning when a majority of at least two clear nearby
  outcomes went the other way.
- Accuracy is measured on tests held out of training and shown on screen.
- A teammate checked the model independently, twice: an audit that reports each
  outcome separately instead of one accuracy figure (`docs/scientific-validation.md`),
  and a test that runs the page's own prediction code against the Python model on 820
  inputs and finds the same numbers to within rounding (`docs/model-parity.md`).
  Both were re-run on the team's PC.
- AI-written text is labelled as AI-written, next to facts copied from PSI.
- The Oxygen map keeps the original table rows, including exact repeats. Rows
  with unreadable oxygen are excluded. Inverse flames use oxygen in the burner
  flow, so those rows are excluded from the cabin-conditions count.
- The repo contains 18 saved Ember answers. A smoke test flagged none: it checks
  numeric tokens against the question or supplied material and looks for a name
  fragment before bracketed PSI IDs. It cannot establish that a number belongs to
  the cited experiment or that an answer is scientifically correct. Human review
  of that saved set is still pending.

**Results on held-out FLEX rows.** Five-fold cross-validation repeated 20 times
used row-level splits. Similar settings can appear in both training and evaluation.
These scores describe performance within this FLEX dataset.

- Flame outcome, 199 tests (172 went out, 27 burned until the fuel was gone):
  AUC 0.81. Accuracy 0.887, against 0.864 for always answering "goes out". The two
  outcomes are lopsided, so the AUC is the fairer number.
- Burning rate, 252 tests: mean absolute error 0.048 mm²/s, R² 0.71. The measured
  values spread about 0.14 mm²/s around their mean.
- An independent audit by a teammate, with a separately fitted model on the same 199
  tests (five-fold cross-validation over five seeds): mean accuracy 88.8%, balanced
  accuracy 61.4%. Read as a yes or no at 50%, it finds on average only 23.7% of the
  tests that burned to completion (heptane 19%, methanol 35%).

**Limits we know about.**

- The fitted predictions cover FLEX. The Oxygen map compares atmosphere records
  across seven investigations. The Saffire-II and BASS-II activities expose selected
  recorded burn lengths and gas concentrations alongside those atmosphere records.
- The Mars base setting is an assumption, as the page says. Ignite shows the model's
  odds, not physics.
- Two-machine model fallback was exercised with two server instances on a PC.
  The physical handheld connected to the PC over Tailscale. Running the small
  model on the handheld, controller operation and rumble there remain unverified.
- The relevance ranks are an AI model's reading of NASA's descriptions, on a 0 to 3
  scale. They are a starting point, not a NASA rating.
- In Fire drill the model was trained on the tests it is scored on, so its score there
  is not a measure of accuracy. The held-out numbers above are. The page says so.
- Ember can give an incorrect attribution even when the number and investigator
  name appear in its prompt. The saved smoke checks do not grade this. Ember
  requires a reachable model server.
- Replays use recorded burn time and interpolate diameter squared. A completion
  with no measured end diameter uses zero for depletion and says so. Other missing
  required measurements leave a still illustration.
- The star map shows oxygen and droplet size only. Two stars that sit close together
  can still differ in pressure, carbon dioxide or helium, which is why the "closest
  three" lines do not always point at the nearest-looking stars.
- Only 8 of 124 methanol tests with a clear outcome completed. The small class
  count limits conclusions about this fuel.
- Read as a yes or no at 50%, the model misses most of the tests that burned to
  completion (about three in four in the independent audit). A low percentage means
  "less likely", not "it will go out".
- In-scope pressures cluster near 0.7 and 1.0 atm. Coverage between the clusters is sparse.
- "Goes out" means the visible flame. FLEX found that fuel can keep reacting afterwards
  in a cool flame, which the page does not model.
- The PSI-69 page says the investigation used both space-based data and ground-based
  tests, and the table does not mark which row is which. We do not claim every row is
  a space experiment.
- The brief identifies a gap in partial-gravity combustion data. The Moon and Mars
  buttons set atmosphere only and provide no gravity-specific validation.
- It is a study and planning tool, not a crew procedure. The flame picture is an
  illustration, not a simulation.

**Benefit.** NASA's combustion results are public but hard to find, compare and read.
This dashboard lets a student, engineer or mission planner find the investigations
that matter for their question in seconds, then explore one of them by hand, and it
always shows where the data stops.

**Tools and languages.** Python (pandas, NumPy, scikit-learn, matplotlib) for
cleaning, training and the chart, and the Python standard library for the local
server. HTML, CSS and plain JavaScript with the browser Gamepad API for the
dashboard, including the drawings (inline SVG), the sound effects (Web Audio) and the
voice (the browser's speech synthesis). Node.js for the test that runs the page's
prediction code outside a browser. Ollama running the open Gemma 4 12B model on
an NVIDIA RTX 5080 for Ember. The captioned demo was captured in desktop Edge.

## NASA data
Copy from docs/sources.md.

NASA Physical Sciences Informatics (PSI) data repository, combustion science, the
source named by the challenge. https://psi.nasa.gov/physci/repo/search?q=combustion

- Investigation PSI-69, Flame Extinguishment Experiment (FLEX), version 5, Experimental
  Table. DOI 10.60555/mbq8-0451, licence CC0-1.0.
  https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
  The 274 source rows yield 199 clear outcomes for logistic regression and 252
  burning rates for linear regression. The in-scope rows also supply the star map
  and opposite-outcome comparisons.
- The PSI records of the 24 combustion investigations (title, project type, hardware,
  objectives, approach), read through the repository's search on Nov 14, 2026.
  Used for: the NASA research page.
- Together with FLEX, six other investigations supply the nine Oxygen map tables
  downloaded from PSI on Nov 14, 2026: CFI, PSI-39, DOI 10.60555/m6pj-a914. ACME CFI-G, PSI-159,
  DOI 10.60555/cyt1-kh64. ACME Flame Design, PSI-10, DOI 10.60555/w4zy-bt45.
  BASS-II, PSI-25, DOI 10.60555/4qc4-de67. Saffire-I, PSI-98, DOI 10.60555/0t15-1z43.
  Saffire-II, PSI-99, DOI 10.60555/2chp-m469. The BASS-II gas endpoint columns
  and Saffire-II Earth/orbit burn lengths also supply the two reveal activities.
  All 25 downloaded tables are listed in `data/raw/psi_tables/MANIFEST.json`.

NASA pages and documents used for the wording on screen (full list with what we took
from each in `docs/sources.md`):

- NASA Space Apps challenge brief, "Flame in Freefall".
  https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
- FLEX Research Requirements Document, NASA Glenn, 2005.
  https://www1.grc.nasa.gov/wp-content/uploads/FLEX_EIRD_v4.pdf
- "Methanol Droplet Combustion in Oxygen-Inert Environments in Microgravity", NASA
  NTRS 20130014061. https://ntrs.nasa.gov/citations/20130014061
- "Studying Combustion and Fire Safety", NASA, 2023.
  https://www.nasa.gov/missions/station/iss-research/studying-combustion-and-fire-safety/
- "Fire in Space", NASA Astronomy Picture of the Day, Aug 10, 2021.
  https://science.nasa.gov/image-article/apod-2021-august-10-fire-in-space/
- "Burning in Microgravity", NASA, May 25, 2011. Colorized composite used on the research home page.
  https://www.nasa.gov/image-article/burning-microgravity/
- "Mechanisms of droplet combustion", NASA NTRS 19820015551.
  https://ntrs.nasa.gov/citations/19820015551

## Space agency partner and other data

No other data: the project uses NASA data only. Software and models: Python, pandas,
NumPy, scikit-learn and matplotlib (open source); Ollama (https://ollama.com) to run
a language model locally; Gemma 4 12B, an open model from Google, as that model.

## Use of artificial intelligence
Where and how we used AI. Copy from the README and add anything new.

Inside the product:

- Ember, the on-board assistant, is Gemma 4 12B, an open language model from Google,
  run locally with Ollama on the team's own RTX 5080 PC. A smaller model is
  configured for handheld fallback and awaits hardware testing. Ember adds a
  one-sentence comment after each Fire drill round, from the NASA PSI records, the
  counts we made from NASA's test tables and the numbers on screen, which our server
  puts in its prompt. The server instructs it to cite PSI identifiers and the
  interface marks generated answers as fallible. Read-aloud requires an installed
  local English voice.
- The plain-language summaries, the "why it matters" lines and the 0 to 3 relevance
  scores on the NASA research page were written ahead of time by Claude (Anthropic)
  from the PSI record of each investigation. The page labels them as AI-written and
  shows the PSI identifier so they can be checked. Titles, project type and hardware
  are copied from PSI unchanged.
- The predictions come from a logistic regression and a linear regression (machine
  learning, not generative AI) trained on the NASA FLEX table.

While building it we used Claude (Anthropic), an AI assistant, for:

- planning the project and the repository layout;
- writing the dashboard (`console/index.html`) and the local server (`server/serve.py`);
- writing the data-cleaning and training scripts, then reviewing them and re-running
  them to confirm the numbers;
- reading the PSI-69 table from the NASA page into a file (checked page by page with
  SHA-256 hashes), downloading the other PSI test tables and writing the script that
  reads them, reading the official challenge page and finding the NASA sources
  listed in `docs/sources.md`;
- drafting the documentation and this form text.

OpenAI ChatGPT/Codex helped write the summary-first explanation and baseline
comparison, which the team reviewed and tested with Claude. Codex also helped
implement and test the three evidence activities and responsive dashboard layout,
revise evidence labels, fix controls and local server handling, and capture and caption the desktop demo.
The video shows the running dashboard. The measurements in these activities
come directly from the cited PSI tables.

Two pieces were contributed by a teammate outside this workflow: the independent
audit (`model/science_audit.py`, `docs/scientific-validation.md`) and the check that
the page and the Python model give the same numbers (`model/check_parity.py`,
`docs/model-parity.md`). We could not confirm before submitting whether AI tools
helped write them, so we list them here to be safe: treat that code and text as
possibly AI-assisted. Their results do not rest on that: the audit was re-run on the
team's PC and reproduced exactly, and its five tests pass.

## Model accuracy (for the description)

- Row-held-out classification on 199 clear outcomes gave AUC 0.813 and accuracy 0.887, against 0.864 for always predicting extinction.
- Row-held-out burning-rate estimates on 252 tests had MAE 0.048 mm²/s and R² 0.705.
- The separate five-seed audit gave balanced accuracy 61.4% and completion recall 23.7% at a 50% cutoff.
