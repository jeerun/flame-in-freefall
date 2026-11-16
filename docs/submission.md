# Flame in Freefall · Space Apps submission draft

## 1. Project name

Flame in Freefall Crew Fire Console

## 2. High-level project summary

Could a crew choose a solid panel for a Moon cabin from NASA’s combustion data?
Our dashboard ranks 24 investigations by fire-safety topic. Its Oxygen map compares
nine tables from seven investigations. Of 746 rows with ambient oxygen and pressure,
20 match the challenge’s Moon Base thresholds. All 20 describe gas flames, leaving
the solid-panel question open. The Flame console uses NASA’s FLEX droplet tests to
estimate visible extinction or completion, disruption and burning rate. Users can
compare predictions with recorded outcomes offline. Ember, an optional local assistant,
answers questions using the selected research and measurements.

## 3. Link to project demo

https://cdn.jsdelivr.net/gh/jeerun/flame-in-freefall@86d58ee2be94d1546350fdb560ba52963f95b2b7/docs/crew-console-demo.mp4

## 4. Link to final project

https://github.com/jeerun/flame-in-freefall

## 5. Detailed project description

Open the dashboard in Orbit view, choose a fire-safety question and follow the evidence
from a research summary to its NASA source. [Open the dashboard](https://jeerun.github.io/flame-in-freefall/)

**NASA research.** The page covers 24 combustion investigations from NASA’s Physical
Sciences Informatics (PSI) repository, including BASS, Saffire, SAME, FLEX, FLEX-2
and the ACME experiments. For each one it shows what the experiment did, what
changed between tests, the kind of fuel, the hardware and why it matters for fire
safety. **Find** searches all 24 records by
name, title or PSI identifier. Research tools shows the collection counts by
kind of fuel and by flight or ground.

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
An investigation selector keeps the same series selected across all three views.
The phone layout fits the chart axes to the available width.
Of 746 rows with measured ambient oxygen and pressure, 20 CFI-G normal-flame rows
meet both brief thresholds (at least 30% oxygen and at most 10.2 psi). No FLEX row
meets both. Seventeen FLEX rows meet the oxygen threshold at pressures above 10.2
through 10.5 psi. The counts retain eight repeated CFI rows, and FLEX has no
flight/ground label for individual rows. The BASS-II and Saffire tables used here
give no pressure and their recorded oxygen values reach 22.2% at most.

**Moon evidence check.** Could a crew use those 20 rows to choose a solid cabin
panel? The offline activity lets readers inspect every matching CFI-G test's
fuel, original oxygen fraction, approximate pressure and CSV line, then open the
NASA investigation. All 20 concern gas flames, and the table has no measured
gravity per row. A solid panel's behaviour in lunar gravity remains unknown
from this comparison. [Open the activity](https://jeerun.github.io/flame-in-freefall/moon-evidence.html)

**Earth or orbit?** Four Saffire-II cases show a material's 1-g burn length. Choose
whether the Earth sample burned farther, both burned equally or the orbital sample
burned farther. Reveal the recorded orbital length and compare the two.

**Read the sensors.** Four BASS-II cases show initial and final oxygen. Guess whether
carbon monoxide rose, stayed the same or fell, then reveal the measured CO and CO₂
endpoints. Both activities show the PSI identifier, DOI and CSV line for each case.

**Interprets: the Flame console page.** It takes one investigation, FLEX, and makes its
274-test table something you can explore by hand. Set the fuel (heptane or methanol),
oxygen, pressure, carbon dioxide, helium and droplet size, and the page shows:

- the estimated chances of completion and visible extinction among clear outcomes,
  with the range in which that estimate falls when the model is refitted on
  resampled tests;
- the modelled chance that a test like this ends in "Disruption", NASA's label for
  an ending with no clear outcome, which is how most tests in oxygen-rich air ended;
- the burning rate and how long the droplet would last at that rate;
- an evidence box. Amber marks a distant match, inconclusive nearby tests,
  disagreement, or a modelled disruption chance of at least 50%. Red flags settings
  beyond the model's scope;
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

**Reopen the same evidence.** A research link preserves the question and selected
NASA investigation. A FLEX link preserves the fuel, five inputs, cabin preset and
any selected test. On a local copy, a view code can be pasted into another copy
of the dashboard. The receiving dashboard computes its own reading.

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
labels that assumption. NASA photographs on the preset controls identify Earth, the Moon and Mars. FLEX ran tests close to that pressure and oxygen level, so the page
can show both what the model expects there and that the nearest real tests were
inconclusive.

**What would put it out?** One button beside the explanation turns the model around.
It moves oxygen, carbon dioxide and helium one at a time through the range FLEX tested
and shows the first value at which the reading drops under the model's 30% watch level,
together with what nearby tests recorded. Some held-out tests below the threshold
still burned to completion. The panel explores model sensitivity. It does not
evaluate whether a gas mixture is safe to breathe or suitable for a crew.

**A one-minute tour.** A button in the top bar walks a first-time user through the three
pages in nine steps, with one part of the screen outlined at a time.

**Ignite.** One button plays a single run of the model full screen. A droplet drawn
with a scale bar shrinks at the predicted burning rate, and whether this run burns all
its fuel is drawn at random with the model's odds, so pressing it a few times shows
what "57%" means. An extinction run uses a recorded FLEX end-to-start diameter
ratio when available. Otherwise it labels the assumed stopping size. The picture is drawn to look like FLEX footage and is labelled an
illustration. The player shows playback speed and can pause on a modelled time
and diameter. Outside the tested range it withholds the run.

**Controller operation.** Crew mode opens a cabin briefing for handheld practice.
It shows the current conditions and the evidence limits above the FLEX estimate.
The crew can open the settings or the star map as needed, then return to the full
console with the same inputs. A stick sweep moves
a selected setting across its range. Banners and, on supported devices, sound and
vibration report changes in the evidence, including leaving the input ranges,
finding only inconclusive nearby tests or seeing nearby results disagree with the
model. At the handheld's full-screen size of 1280×800 the page uses no text under
12 px and thumb-sized controls. The team has not tested glove operation.

**Takes the data with you.** The challenge asks for data that supports predictive
modelling. One button saves the 252 in-scope tests with their fitted predictions.
When the team’s server is available, Send to base stores the project CSV there.
An operator can choose a cloud-synced exports folder, in which case the sync
application may transfer the file once connected.

**Ask Ember.** Ember is available from the research, console and drill pages when the
model server is reachable. Its Gemma 4 12B model runs on the team's RTX 5080 PC.
The optional two-server
setup prefers the reachable PC and falls back to the server's own configured
model. On the handheld's own server, the owner switched Ember from the PC to
the Legion Go and received a local answer. A second server on the handheld
answered with its configured peer unreachable. On the research page Ember answers
questions such as "For a Moon Base cabin with about 30% oxygen at low pressure,
which investigations matter most, and why?", "Compare BASS-II with BASS" or "What
did this investigation measure, and with which instruments?" from the PSI text of
the investigations closest to the question and the counts from NASA's test tables.
On the console page it interprets the current reading in plain words, and in the
Fire drill it adds one sentence on why a
test may have ended the way it did. It is told to answer only from the material it
is given, to cite PSI identifiers, to copy numbers exactly, and to say so when the
records do not hold the answer. Read-aloud selects an installed English voice
advertised by the browser as local. If none is available, answers remain on screen.

The evidence lab bundles six NASA clips and links to online footage of FLEX-2
flame oscillations and the Saffire-IV fabric experiment. A saved frame review identifies a possible
change in the visible flame rim in the [FLEX footage](https://svs.gsfc.nasa.gov/11318/).
A fresh review uses the Python server and an available Ollama vision model. For
English questions about BASS-II gas readings, Ember proposes a filter. Python
validates it and returns the matching CSV rows.

With the PC switched off, a local copy still runs the research, evidence activities,
predictions and drill and can save the CSV on the device. Ember and sending a CSV
to base require a reachable server.

**How it works.**

1. Data. From NASA PSI: the FLEX Experimental Table (PSI-69, 274 droplet combustion
   tests), the PSI records returned for “combustion”, and 25 Experimental Table CSVs.
   The manifest records the original downloads’ hashes. Git can normalize line
   endings. `python data/clean/fetch_psi_tables.py --verify` checks the originals’
   hashes offline, restoring CRLF in memory as needed. Of the FLEX rows, 252
   have usable pressure at or below 1.1 atm and a known droplet size.
2. Models. One logistic regression estimates completion versus visible extinction on
   the 199 clear outcomes. A second logistic regression estimates disruption from
   all 252 in-scope rows. A linear regression uses those 252 rows to estimate
   burning rate. The inputs are settings known before ignition. Each fuel has its own
   slopes. The clear-outcome model selects penalty strength inside each outer
   training fold.
3. Export. Scripts write the fitted model, in-scope tests, research notes, oxygen
   map and selected evidence rows as JavaScript data files for offline use.
4. Dashboard. HTML, CSS and plain JavaScript read the bundled data. The interface
   supports a gamepad, touch and keyboard.
5. Local AI. The Python server can serve the dashboard to devices on a configured
   local network. For research questions it picks the PSI records that share the most words with
   the question, adds the top of our own ranking for the need on screen, a one-line
   catalogue of all 24 and the counts from the test tables, and hands that to the
   language model through Ollama. The answer streams back to the handheld. The same
   script keeps the CSV file the handheld sends.

**How we keep it honest.**

- The page checks inputs against the in-scope range of each variable and flags
  unsupported combinations. Beyond that scope it dims the model reading.
- No in-scope FLEX row mixed carbon dioxide and helium, so setting both counts as untested.
- Gas settings above 100% in total are flagged as physically impossible.
- Inside the range, the page still measures the distance to the closest real test and
  warns when it is far, or when the nearby tests had no clear outcome.
- Within range, a strong model preference (below 30% or at least 65% completion)
  triggers a disagreement warning when a majority of at least two clear nearby
  outcomes went the other way.
- Accuracy is measured on tests held out of training and shown on screen.
- The model was chosen in the open. A teammate's audit showed that our first model,
  with one set of slopes for both fuels, found fewer than a quarter of the tests that
  burned to completion (`docs/scientific-validation.md`). Another teammate trained a
  model with separate slopes for each fuel and compared eight candidates on the same
  held-out tests (`docs/per-fuel-model.md`). We re-ran both, checked the gain with a
  separate script and stricter hold-outs (`model/verify_per_fuel.py`), and only then
  switched the console. A third check runs the page's own prediction code against
  the Python model on 820 inputs and finds the same numbers to within rounding
  (`docs/model-parity.md`).
- The main reading displays estimates from 1% to 99%. This is a display rule.
- We looked for holes in our own model design and wrote down all nine, closed or not
  (`docs/model-design-audit.md`). The largest: the outcome model leaves out the 53
  tests NASA labels "Disruption", and they are not scattered at random. At 25%
  oxygen or more, 11 of 12 heptane tests and 12 of 17 methanol tests ended that way,
  and none at 15% or less. So a third formula gives the chance of a disruption, the
  page shows it beside the reading, and at 50% or more the reading turns amber and
  says the percentage describes only the rest.
- Beside the main reading is a range: where the estimate falls in the middle 90% of
  300 refits on resampled tests. Heptane at the starting values reads 57%, range 34%
  to 75%.
- "The visible flame went out" does not mean little burned. Where nearby flames went
  out, the evidence box gives the share of the droplet's volume that was already
  gone: across the table a median of 40% for heptane and 82% for methanol.
- Where resampling the tests does not settle which way a setting pushes for a fuel
  (pressure for both fuels; droplet size and carbon dioxide for methanol), the
  explanation says so on the line that leans on it.
- Each research card links its summary to the original PSI record.
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

- Of 199 clear outcomes, 172 were visible extinctions and 27 were completions.
  AUC was 0.902 overall, 0.906 within heptane and 0.847 within methanol.
  Accuracy was 0.915, compared with 0.864 for always predicting extinction.
- At a 50% cutoff the model identified 52.4% of completions and called about 2%
  of extinctions completions. At the 30% study threshold it identified 64.1% of
  completions and also flagged 7.8% of extinctions.
- On 252 tests, burning-rate MAE was 0.045 mm²/s and R² was 0.732. The measured
  rates had a standard deviation of 0.138 mm²/s.
- Keeping each fuel and gas mixture together in the same evaluation fold gave AUC
  0.9005 and burning-rate R² 0.724 (`model/per_fuel/comparison.json`).
- In row-held-out predictions, 2.6% of the rows assigned a completion chance below
  10% completed. The share was 33% for predictions from 30% to below 65%, and 92.5%
  at 65% or above. These are averages across repeated splits of the same rows.
- With the tests themselves resampled, the 95% interval of the AUC is 0.83 to 0.96
  (heptane 0.82 to 0.98, methanol 0.64 to 0.97: methanol has 8 completions).
- The disruption formula, held out on all 252 tests: AUC 0.892, Brier score 0.101
  against 0.166 for no model. When it said under 10%, 3.4% of those tests were
  disrupted. At 65% or above, 82%.
- By fuel the burning rate is uneven: heptane R² 0.62 (MAE 0.069 mm²/s), methanol
  R² 0.87 (MAE 0.026). For the 27 completions, the page's time to consume the
  droplet is a median 1.18 times NASA's burn time (middle half 0.94 to 1.42).
- The earlier pooled-slope model reached AUC 0.813. Its independent five-seed
  audit found 23.7% completion recall at 50% and 61.4% balanced accuracy.
  The current per-fuel classifier had the lowest Brier score and log loss of the
  eight candidates in the row-split comparison.

**Limits we know about.**

- The fitted predictions cover FLEX. The Oxygen map compares atmosphere records
  across seven investigations. The Saffire-II and BASS-II activities expose selected
  recorded burn lengths and gas concentrations alongside those atmosphere records.
- The Mars base setting is an assumption, as the page says. Ignite shows the model's
  odds, not physics.
- The physical Legion Go reached the PC over Tailscale. After a controller CSV
  export, the PC’s `/tests.csv` returned 252 rows. The PC's destination folder
  was not opened. The team did not test a direct Wi-Fi address or stop the PC
  mid-session to check the disconnect banner.
- The project's 0 to 3 relevance scale interprets PSI descriptions for the four
  safety topics. NASA supplies the investigation records.
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
- Only 8 of the 124 clear methanol outcomes completed. Bootstrap refits disagree
  on the direction of the methanol diameter and CO₂ effects. When the model put a
  methanol test between 30% and 65%, 14% completed, on about five tests per split.
  Smaller and more heavily penalised methanol models were tried and scored worse
  held out, so the model stays and the range on screen is wide there.
- At a 50% cutoff the model misses about half the recorded completions.
- In-scope pressures cluster near 0.7 and 1.0 atm. The direction of the pressure
  effect is unstable for both fuels. At 0.7 atm nearly every clear outcome comes with
  carbon dioxide or helium: only 2 heptane and 4 methanol tests are plain oxygen and
  nitrogen, which is the Moon Base preset's mix.
- We selected the model family and evaluated it on the same FLEX dataset. No
  independent flight or external test set was used.
- At the default heptane droplet size the Moon Base preset gives a very high
  fitted completion chance. All three nearby measured outcomes were disruptions.
  The disruption formula puts that chance at 98%, so the 99% describes a rare case.
  Its range (98% to 99%) is narrow only because the range covers which tests were
  run, not how far the formula is stretched.
- NASA's table does not say what a disruption is. We report how often it was
  recorded, not what it means for a fire.
- The range shows sampling uncertainty only. The tested range on screen is pooled
  over both fuels: methanol was never run below 1.61 mm, heptane never above 45%
  carbon dioxide. A methanol droplet of 1.3 mm still reads "Inside the tested range".
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
that matter for their question and explore individual tests, compare readings and see where evidence is sparse.

**Tools and languages.** Python (pandas, NumPy, scikit-learn, matplotlib) for
cleaning, training and the chart, and the Python standard library for the local
server. HTML, CSS and plain JavaScript with the browser Gamepad API for the
dashboard, including the drawings (inline SVG), the sound effects (Web Audio) and the
voice (the browser's speech synthesis). Node.js for the test that runs the page's
prediction code outside a browser. Ollama running the open Gemma 4 12B model on
an NVIDIA RTX 5080 for Ember. We tested the dashboard on a Lenovo Legion Go.
The captioned demo was captured in desktop Edge.

## 6. NASA data

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
  The NASA research page uses these records.
- Together with FLEX, six other investigations supply the nine Oxygen map tables
  downloaded from PSI on Nov 14, 2026: CFI, PSI-39, DOI 10.60555/m6pj-a914. ACME CFI-G, PSI-159,
  DOI 10.60555/cyt1-kh64. ACME Flame Design, PSI-10, DOI 10.60555/w4zy-bt45.
  BASS-II, PSI-25, DOI 10.60555/4qc4-de67. Saffire-I, PSI-98, DOI 10.60555/0t15-1z43.
  Saffire-II, PSI-99, DOI 10.60555/2chp-m469. The BASS-II gas endpoint columns
  and Saffire-II Earth/orbit burn lengths also supply the two reveal activities.
  The manifest lists the 25 downloaded tables. [Table manifest](https://github.com/jeerun/flame-in-freefall/blob/main/data/raw/psi_tables/MANIFEST.json)

NASA pages and documents used for the wording on screen are listed below. The source
notes identify what each contributed. [Full source notes](https://github.com/jeerun/flame-in-freefall/blob/main/docs/sources.md)

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

NASA images and video shown in the dashboard include the following.

- Cabin-air buttons: the Apollo 17 Blue Marble photograph AS17-148-22727, the Galileo
  Moon mosaic PIA00405 and the Viking Orbiter 1 Valles Marineris mosaic PIA04304.
- Evidence lab: NASA clips of FLEX (SVS release 11318), FLEX-2 (SVS release 11640),
  SoFIE-GEL, Saffire-I, Saffire-V and Saffire-VI, and two stills taken from the FLEX clip.

## 7. Space Agency Partner Data and Other References

The project uses NASA data and did not use data from another space agency.
NASA supplied the source experiment footage and planetary photographs. The team
captured the dashboard screenshots and demonstration.

- Software: Python with pandas, NumPy, scikit-learn and matplotlib (cleaning, training,
  the chart, the local server). Pillow and imageio-ffmpeg (preparing frames of the FLEX
  clip). Node.js and Playwright with Microsoft Edge (tests).
- Ember uses the Gemma 4 12B and `gemma4:e2b` models from Google through local
  [Ollama](https://ollama.com) servers.
- The dashboard loads no third-party JavaScript or CSS library and no web font.

## 8. Use of Super Intelligence (SI)
