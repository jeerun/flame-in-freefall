# Submission form draft

Everything in English. Deadline: Sunday Nov 15, 11:59 PM, team owner's local time
(confirm on the team page). "Submit for Judging" is final.

Status of this draft: rewritten Nov 14 after comparing the build with the official
challenge page. Lines marked TO ADD need the owner.

## Project name

Flame in Freefall Crew Fire Console

## High-level project summary

A gamepad-driven dashboard that turns NASA's microgravity combustion data into
fire-safety answers, with its AI running on our own hardware instead of the cloud.
The NASA research page summarizes and ranks the 24 combustion investigations in
NASA's Physical Sciences Informatics (PSI) database by what the user needs:
preventing a fire, detecting it, or putting it out. The Flame console page goes deep
on one of them, the Flame Extinguishment Experiment (FLEX): two small models trained
on 252 real tests predict whether a fuel-droplet flame burns until the fuel is gone
or goes out first, for any cabin air the user sets, including the oxygen-rich,
low-pressure air expected in the Moon Base. The Fire drill page turns the same data
into a game: guess how a real NASA test ended, and see whether you beat the model.
On every page, "Ask the AI" sends the question to a language model on the team's
RTX 5080 PC, which answers from the NASA records only and cites them. Every reading
ranks the closest real NASA tests, and the dashboard says so in red when the settings
leave what NASA actually tested. It runs as one web page on a Lenovo Legion Go.

## Link to project demo
Video up to 30 seconds with English subtitles, or up to 7 slides. Public link, no login.

TO ADD: public video link, after filming on the Legion Go (script in `docs/demo-script.md`).

## Link to final project
The public GitHub repo. No login needed to view.

https://github.com/jeerun/flame-in-freefall

## Detailed project description
What it does, how it works, what benefit it has, what tools and languages we used.

**The challenge asks for** an interactive, SI-powered, web-based dashboard that
summarizes, ranks and interprets NASA's microgravity combustion investigations for
fire safety. Here is how each word is answered.

**Summarizes: the NASA research page.** It lists the 24 combustion-science
investigations that the PSI repository returns for "combustion" (BASS, Saffire, SAME,
FLEX, FLEX-2, the ACME experiments and others). For each one it shows what the
experiment did, what changed between tests, the kind of fuel, the hardware, and why it
matters for fire safety, in plain language, with the PSI identifier to find it.

**Ranks: by the part of fire safety you need.** NASA's fire-safety work is prevention,
detection and suppression. Pick one and the page ranks the investigations from
"direct" to "related" for that need. Choose suppression and BASS and FLEX come first;
choose detection and the smoke experiments SAME and SAME-R come first; choose
prevention and the material-flammability experiments lead, including the ACME Burning
Rate Emulator, which tested the cabin atmospheres NASA considers for crewed missions.
On the Flame console page the same idea is applied to single tests: every reading
ranks the three closest real FLEX tests and shows how each one ended.

**Interprets: the Flame console page.** It takes one investigation, FLEX, and makes its
274-test table something you can explore by hand. Set the fuel (heptane or methanol),
oxygen, pressure, carbon dioxide, helium and droplet size, and the page shows:

- the chance the flame burns until the fuel is gone, and the chance it goes out first;
- the burning rate, and how long the droplet would last at that rate;
- a confidence box: green inside the tested range, amber when no real test is close or
  when nearby real tests disagree with the model, red outside what FLEX tested;
- an explanation: which settings push the result which way, the three closest real
  tests, how the nearby tests ended, and the model's measured accuracy.

**Plays like a handheld game.** Everything is driven with a gamepad. The flame picture
breathes faster as the burning rate rises, the controller buzzes when the settings
leave what NASA tested, and the picture turns into a question mark there. A third
page, Fire drill, is a ten-round game: it shows the settings of a real FLEX test, the
player guesses whether the flame went out first or burned all its fuel, and the page
reveals NASA's recorded result and keeps score, player against model. Five of the ten
tests burned all their fuel and five went out, so guessing one answer every time does
not win. It is a quick way to build intuition for what makes a flame survive in
microgravity, and it shows the model's misses as openly as its hits.

One button switches the cabin air between Earth-like air and the Moon Base case from
the challenge brief (oxygen 30% or more at 10.2 psi or less). FLEX ran tests at that
pressure and oxygen level, so the page can show both what the model expects there and
that the nearest real tests were inconclusive.

**Where the AI is.** Three places, each stated on screen.

- "Ask the AI", on every page. A language model (Gemma 4, 12 billion parameters) runs
  on the team's own PC with an RTX 5080, and the handheld reaches it over the local
  network. On the research page it answers questions such as "For a Moon Base cabin
  with about 30% oxygen at low pressure, which investigations matter most, and why?"
  from the PSI text of the investigations closest to the question. On the console
  page it interprets the current reading in plain words. It is told to answer only
  from the material it is given, to cite PSI identifiers, and to say so when the
  records do not hold the answer. Answers arrive in a few seconds. No cloud service
  is involved, which is how a crew far from Earth would have to run it.
- The summaries and relevance ranks on the research page were written ahead of time
  by an AI model (Claude) from each investigation's PSI record and stored in the
  page, so they are there even when the PC is not.
- The predictions on the console page come from machine-learning models trained on
  NASA data.

If the PC is switched off, the dashboard still opens as a plain file and everything
except "Ask the AI" works, fully offline.

**How it works.**

1. Data. From NASA PSI: the FLEX Experimental Table (PSI-69, 274 droplet combustion
   tests) and the repository's own descriptions of every combustion investigation.
   A script cleans the table without removing rows or guessing values. 252 tests are
   in scope (pressure at or below 1.1 atm, known droplet size).
2. Models. Two deliberately small models, so every number can be explained: a
   logistic regression for "the flame went out before the fuel was gone" against "it
   burned until the fuel was gone", and a linear regression for the burning rate.
   Inputs are only things known before ignition.
3. Export. Scripts write the model, the list of real tests and the research notes
   into two small JavaScript files.
4. Dashboard. One HTML file with no libraries reads them. It works with a gamepad,
   touch or keyboard and fits a 1280x680 screen.
5. Local AI. A small Python script on the PC serves the dashboard on the local
   network. For each question it picks the PSI records that share the most words with
   the question, adds a one-line catalogue of all 24, and hands that to the language
   model running on the GPU through Ollama. The answer streams back to the handheld.

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
- AI-written text is labelled as AI-written, next to facts copied from PSI.
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

**Limits we know about.**

- The predictions cover one investigation, FLEX. The other 23 are summarized and
  ranked, not modelled, and their raw data is not compared.
- The relevance ranks are an AI model's reading of NASA's descriptions, on a 0 to 3
  scale. They are a starting point, not a NASA rating.
- In Fire drill the model was trained on the tests it is scored on, so its score there
  is not a measure of accuracy. The held-out numbers above are. The page says so.
- "Ask the AI" can be wrong or imprecise, like any language model. We spot-checked a
  handful of answers against the PSI records, not a formal evaluation. It needs the
  PC to be on and reachable; without it that one button disappears.
- The outcome model separates heptane tests well (AUC about 0.8 within heptane) and
  methanol tests poorly (about 0.6): only 8 of 124 methanol tests burned to completion.
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
dashboard. Ollama running the open Gemma 4 12B model on an NVIDIA RTX 5080 for
"Ask the AI". Git and GitHub. Shown on a Lenovo Legion Go.

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

- "Ask the AI" uses Gemma 4 12B, an open language model from Google, run locally with
  Ollama on the team's own RTX 5080 PC. It answers the user's questions at run time
  from the NASA PSI records and the numbers on screen, which our server puts in its
  prompt, and it is instructed to cite PSI identifiers and not to guess. Its answers
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
  SHA-256 hashes), reading the official challenge page and finding the NASA sources
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
