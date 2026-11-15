# Submission form draft

Everything in English. Deadline: Sunday Nov 15, 11:59 PM, team owner's local time
(confirm on the team page). "Submit for Judging" is final.

Status of this draft: updated Nov 15 (Oxygen map from NASA's test tables, zoomable
star map, Ignite, two-machine AI, live copy). Lines marked TO ADD need the owner.

## Project name

Flame in Freefall Crew Fire Console

## High-level project summary

A dashboard that summarizes, ranks and interprets NASA's microgravity combustion
investigations for fire safety, driven with a gamepad on a handheld, with its AI
running on our own hardware instead of the cloud. The NASA research page summarizes
the 24 combustion investigations in NASA's Physical Sciences Informatics (PSI)
database and ranks them for the user's question: prevention, detection, suppression,
or the oxygen-rich cabin air planned for the Moon Base. An Oxygen map, read from nine
of NASA's own test tables, shows where every test sits against that air: of 746
microgravity tests that record oxygen and pressure, 20 were run in it. The Flame
console page goes deep on one investigation, the Flame Extinguishment Experiment
(FLEX): two small models trained on 252 real tests predict whether a fuel-droplet
flame burns until the fuel is gone or goes out first, and a star map shows every real
test, which the user can pick and replay from NASA's measurements. The Fire drill
page turns the same data into a game. On every page Ember, a language model on the
team's RTX 5080 PC or a smaller one on the handheld itself, answers questions from
the NASA records only, cites them and reads the answer aloud. It needs no internet. The dashboard says so in red when the settings leave what
NASA actually tested. It runs as one web page on a Lenovo Legion Go.

## Link to project demo
Video up to 30 seconds with English subtitles, or up to 7 slides. Public link, no login.

TO ADD: public video link, after filming on the Legion Go (script in `docs/demo-script.md`).

## Link to final project
The public GitHub repo. No login needed to view.

https://github.com/jeerun/flame-in-freefall

A live copy to try in a browser (everything except the AI, which runs on our PC):
https://jeerun.github.io/flame-in-freefall/

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
and suppression, and the challenge adds a fourth concern: the Moon Base will run on
air with 30% oxygen or more at low pressure. Pick one of the four and the page ranks
the investigations from "direct" to "related". Choose suppression and BASS and FLEX
come first; choose detection and the smoke experiments SAME and SAME-R come first;
choose cabin air and the ACME Burning Rate Emulator leads, because it tested the
cabin atmospheres NASA considers for crewed missions. The ranking can be shown as a
numbered list or as an orbit view: the question in the middle, each investigation on
a ring set by its relevance, one quarter of the sky per kind of fuel, each drawn with
a small picture of that fuel. Similar investigations end up side by side. On the
Flame console page the same idea is applied to single tests: every reading ranks the
three closest real FLEX tests and shows how each one ended.

**Compares: the Oxygen map.** The brief says the Moon Base will likely run on 30%
oxygen or more at 10.2 psi or less, so we asked NASA's own data how many microgravity
tests were run in that air. A script downloads the Experimental Table of every
combustion investigation from PSI and reads the oxygen level, and where the table has
it the pressure, of each test from nine of them: FLEX, CFI, CFI-G, Flame Design,
BASS-II, Saffire-I and Saffire-II. The map has three levels of detail: the range each
investigation covered, every test as a dot, and every test against pressure with the
Moon Base air, Earth and a spacesuit marked. Its headline is a count, not an
estimate: 746 tests record both the oxygen and the pressure of the surrounding gas.
20 of them were run in Moon Base air, all of them gas flames from CFI-G, and 17 FLEX
droplet tests sit just above the pressure line, at 10.2 to 10.5 psi. The solid
material tests, BASS-II and Saffire, give no pressure in their tables and did not go
above 22.2% oxygen.

**Interprets: the Flame console page.** It takes one investigation, FLEX, and makes its
274-test table something you can explore by hand. Set the fuel (heptane or methanol),
oxygen, pressure, carbon dioxide, helium and droplet size, and the page shows:

- the chance the flame burns until the fuel is gone, and the chance it goes out first;
- the burning rate, and how long the droplet would last at that rate;
- a confidence box: green inside the tested range, amber when no real test is close or
  when nearby real tests disagree with the model, red outside what FLEX tested;
- an explanation: which settings push the result which way, the three closest real
  tests, how the nearby tests ended, and the model's measured accuracy.

**A star map of the real tests, and a replay.** Under the reading, every real FLEX
test with the chosen fuel is drawn as a star: oxygen across, droplet size up. An
orange star with eight spikes burned all its fuel, a blue star with four went out
first, and the bigger the star, the faster NASA measured it burning. A cross marks
the current settings and lines run to the three closest tests. The right stick points
at any star: the page names that test, can move every setting onto it, and can replay
it. In a replay the droplet shrinks between the start and end diameters NASA
recorded, over the recorded burn time, and then the flame goes out or the fuel runs
out, as recorded. It is the data played back, not a physics simulation, and the
screen says so. The map zooms to the whole screen with three levels of detail: the
stars, a grid with the test numbers, and the lines where the model puts the chance
of burning all the fuel at 25, 50 and 75%, so the model can be compared with the
real outcomes at a glance.

**Plays like a handheld game.** It opens on a start screen and everything is driven
with a gamepad, with sound effects made in the browser. The flame picture breathes
faster as the burning rate rises. When the settings leave what NASA tested, the
controller buzzes, an alarm sounds and the picture turns into a question mark. A
third page, Fire drill, is a ten-round game: it shows the settings of a real FLEX
test, the player guesses whether the flame went out first or burned all its fuel, and
the page replays the test, reveals NASA's recorded result and keeps score, player
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
at true scale shrinks at the predicted burning rate, and whether this run burns all
its fuel is drawn at random with the model's odds, so pressing it a few times shows
what "35%" means. When a run goes out, the size it stops at is borrowed from a real
nearby test. The picture is drawn to look like FLEX footage and is labelled an
illustration. Outside the tested range it refuses to run.

**Built for gloved hands.** A crew member may be wearing gloves, so every function
can be reached from the sticks and buttons. The left stick slides a setting across
its whole range in about a second. Warnings arrive as a banner, a sound and a
vibration: when the settings leave what NASA tested, when the risk turns high, and
when nearby real tests disagree with the model. We have not tried it with gloves.

**Takes the data with you.** The challenge asks for data that supports predictive
modelling. One button saves the 252 real tests in use, with the model's prediction
beside each, as a CSV file. From the handheld, one press sends that file to the
computer that serves the dashboard, into a folder that can be a shared drive, so the
data does not stay on the handheld. It works without internet.

**Where the AI is.** Three places, each stated on screen.

- Ember, the on-board AI, on every page. A language model (Gemma 4, 12 billion
  parameters) runs on the team's own PC with an RTX 5080, and the handheld reaches it
  over the local network. A smaller Gemma 4 can run on the handheld itself: it then
  uses the PC while the PC answers, switches to its own model when the PC is out of
  reach, and a banner says which one answered. One button asks it. On the research page it answers
  questions such as "For a Moon Base cabin with about 30% oxygen at low pressure,
  which investigations matter most, and why?", "Compare BASS-II with BASS" or "What
  did this investigation measure, and with which instruments?" from the PSI text of
  the investigations closest to the question and the counts from NASA's test tables. On the console page it interprets the
  current reading in plain words, and in the Fire drill it adds one sentence on why a
  test may have ended the way it did. It is told to answer only from the material it
  is given, to cite PSI identifiers, to copy numbers exactly, and to say so when the
  records do not hold the answer. Answers arrive in a few seconds and can be read
  aloud. No cloud service is involved, which is how a crew far from Earth would have
  to run it.
- The summaries and relevance ranks on the research page were written ahead of time
  by an AI model (Claude) from each investigation's PSI record and stored in the
  page, so they are there even when the PC is not.
- The predictions on the console page come from machine-learning models trained on
  NASA data.

If the PC is switched off, the dashboard still opens as a plain file and everything
except Ember works, fully offline.

**How it works.**

1. Data. From NASA PSI: the FLEX Experimental Table (PSI-69, 274 droplet combustion
   tests), the repository's own descriptions of every combustion investigation, and
   the Experimental Table of each one that has one (25 files, kept unchanged).
   A script cleans the table without removing rows or guessing values. 252 tests are
   in scope (pressure at or below 1.1 atm, known droplet size).
2. Models. Two deliberately small models, so every number can be explained: a
   logistic regression for "the flame went out before the fuel was gone" against "it
   burned until the fuel was gone", and a linear regression for the burning rate.
   Inputs are only things known before ignition.
3. Export. Scripts write the model, the list of real tests, the research notes and
   the oxygen and pressure of each test in nine tables into three small JavaScript
   files.
4. Dashboard. One HTML file with no libraries reads them. It works with a gamepad,
   touch or keyboard and fits a 1280x680 screen.
5. Local AI. A small Python script on the PC serves the dashboard on the local
   network. For each question it picks the PSI records that share the most words with
   the question, adds the top of our own ranking for the need on screen, a one-line
   catalogue of all 24 and the counts from the test tables, and hands that to the
   language model through Ollama. The answer streams back to the handheld. The same
   script keeps the CSV file the handheld sends.

**How we keep it honest.**

- The tested range of each input is the real minimum and maximum in the data. Outside
  it, the numbers are dimmed and the page says the risk is unknown.
- No FLEX test mixed carbon dioxide and helium, so setting both counts as untested.
- Gas settings that add up to more than 100% are rejected.
- Inside the range, the page still measures the distance to the closest real test and
  warns when it is far, or when the nearby tests had no clear outcome.
- If most nearby real tests ended the other way from the model, the page says so and
  tells the user to trust the tests.
- Accuracy is measured on tests held out of training and shown on screen.
- A teammate checked the model independently, twice: an audit that reports each
  outcome separately instead of one accuracy figure (`docs/scientific-validation.md`),
  and a test that runs the page's own prediction code against the Python model on 820
  inputs and finds the same numbers to within rounding (`docs/model-parity.md`).
- AI-written text is labelled as AI-written, next to facts copied from PSI.
- The Oxygen map counts rows of NASA's tables as published. A row whose oxygen cell
  is not a number is left out and reported as left out. Inverse gas flames, where the
  oxygen flows out of the burner, are drawn but not counted as cabin atmospheres.
- Ember's answers to 18 fixed questions are stored in the repo with two automatic
  checks: every number must appear in the material it was given, and every PSI id
  must sit next to the right investigation name. All 18 pass. They still wait for a
  person to read them.
- The language model never sees the internet, only NASA's PSI text and the numbers on
  screen. In our tests it declined a question the records cannot answer instead of
  making something up. Its answers are still labelled as possibly wrong.

**Results, on held-out tests** (5-fold cross-validation repeated 20 times):

- Flame outcome, 199 tests (172 went out, 27 burned until the fuel was gone):
  AUC 0.81. Accuracy 0.887, against 0.864 for always answering "goes out". The two
  outcomes are lopsided, so the AUC is the fairer number.
- Burning rate, 252 tests: mean absolute error 0.048 mm²/s, R² 0.71. The measured
  values spread about 0.14 mm²/s around their mean.
- Keeping repeat tests at the same conditions together in one fold gives almost the
  same numbers (AUC 0.80, R² 0.70).
- When the page says under 10%, 4% of those tests burned to completion; at
  35 to 65%, 67% did. The model rarely goes above 65%.
- An independent audit by a teammate, with a separately fitted model on the same 199
  tests (five-fold cross-validation over five seeds): mean accuracy 88.8%, balanced
  accuracy 61.4%. Read as a yes or no at 50%, it finds on average only 23.7% of the
  tests that burned to completion (heptane 19%, methanol 35%).

**Limits we know about.**

- The predictions cover one investigation, FLEX. The other 23 are summarized and
  ranked, not modelled. Seven investigations are compared on one thing only: the
  oxygen and pressure their tests were run at. The Oxygen map shows where tests were
  run, not what happened in them.
- The Mars base setting is an assumption, as the page says. Ignite shows the model's
  odds, not physics.
- The two-machine AI was checked with two copies of the server on one PC, not yet on
  the real handheld.
- The relevance ranks are an AI model's reading of NASA's descriptions, on a 0 to 3
  scale. They are a starting point, not a NASA rating.
- In Fire drill the model was trained on the tests it is scored on, so its score there
  is not a measure of accuracy. The held-out numbers above are. The page says so.
- Ember can be wrong or imprecise, like any language model. In testing it once
  attached a figure from the challenge brief to an investigation; we tightened its
  instructions and the error did not come back in our checks, but we only
  spot-checked about twenty answers against the PSI records, not a formal evaluation.
  It needs the PC to be on and reachable; without it that one button disappears.
- A replay is the recorded data played back: start diameter, end diameter and burn
  time are NASA's, the path between them is a straight line in diameter squared, and
  the glow is an illustration. Tests whose record has no end diameter are not replayed.
- The star map shows oxygen and droplet size only. Two stars that sit close together
  can still differ in pressure, carbon dioxide or helium, which is why the "closest
  three" lines do not always point at the nearest-looking stars.
- The outcome model separates heptane tests well (AUC about 0.8 within heptane) and
  methanol tests poorly (about 0.6): only 8 of 124 methanol tests burned to completion.
- Read as a yes or no at 50%, the model misses most of the tests that burned to
  completion (about three in four in the independent audit). A low percentage means
  "less likely", not "it will go out".
- Pressure sits at only two levels, about 0.7 and 1.0 atm, so its effect is weakly known.
- "Goes out" means the visible flame. FLEX found that fuel can keep reacting afterwards
  in a cool flame, which the page does not model.
- The PSI-69 page says the investigation used both space-based data and ground-based
  tests, and the table does not mark which row is which. We do not claim every row is
  a space experiment.
- PSI has no partial-gravity data yet, so nothing here is specific to Moon gravity.
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
an NVIDIA RTX 5080 for Ember. Git, GitHub and GitHub Pages. Shown on a Lenovo
Legion Go.

## NASA data
Copy from docs/sources.md.

NASA Physical Sciences Informatics (PSI) data repository, combustion science, the
source named by the challenge. https://psi.nasa.gov/physci/repo/search?q=combustion

- Investigation PSI-69, Flame Extinguishment Experiment (FLEX), version 5, Experimental
  Table. DOI 10.60555/mbq8-0451, licence CC0-1.0.
  https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
  Used for: the 274 droplet combustion tests behind both models (fuel, pressure,
  oxygen, carbon dioxide, helium and droplet diameter as inputs; "Test end" and
  "Burning rate" as what the models predict) and the real tests shown on screen.
- The PSI records of the 24 combustion investigations (title, project type, hardware,
  objectives, approach), read through the repository's search on Nov 14, 2026.
  Used for: the NASA research page.
- The Experimental Tables of seven more investigations, downloaded unchanged from PSI
  on Nov 14, 2026 and used for the Oxygen map (oxygen level and, where given, pressure
  of each test): CFI, PSI-39, DOI 10.60555/m6pj-a914. ACME CFI-G, PSI-159,
  DOI 10.60555/cyt1-kh64. ACME Flame Design, PSI-10, DOI 10.60555/w4zy-bt45.
  BASS-II, PSI-25, DOI 10.60555/4qc4-de67. Saffire-I, PSI-98, DOI 10.60555/0t15-1z43.
  Saffire-II, PSI-99, DOI 10.60555/2chp-m469. Together with FLEX: nine tables.
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
  run locally with Ollama on the team's own RTX 5080 PC (a smaller Gemma 4 can run
  on the handheld). It answers the user's questions at run time, and adds a
  one-sentence comment after each Fire drill round, from the NASA PSI records, the
  counts we made from NASA's test tables and the numbers on screen, which our server
  puts in its prompt, and it is instructed to cite PSI identifiers and not to guess. Its answers
  are generated on the spot, shown with a warning that they can be wrong, and never
  leave the local network.
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

No AI-generated images, video or audio are used. No data value was generated or
changed by AI: every number on screen comes from the NASA table or from the two
regressions trained on it.

TO ADD (owner): anything teammates did with AI tools outside this repo.

## Model accuracy (for the description)
Held-out accuracy for "does the flame go out": AUC 0.81; accuracy 0.887 against 0.864 for always answering "goes out" (199 tests, 5-fold cross-validation repeated 20 times).
Held-out error for burning rate: mean absolute error 0.048 mm²/s, R² 0.71 (252 tests).
Number of tests used: 252 of the 274 in the table (199 for the flame outcome, 252 for burning rate).
Independent audit (separately fitted model, five seeds): balanced accuracy 61.4%; finds 23.7% of the tests that burned to completion at a 50% cut-off.
