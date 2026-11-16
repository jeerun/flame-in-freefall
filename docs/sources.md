# Sources

This guide connects the console’s scientific claims, model outputs and evidence
activities to their source records or calculation.

## NASA data

| Dataset | Identifier | Link | Downloaded on | What we used it for |
|---|---|---|---|---|
| Flame Extinguishment Experiment (FLEX), Experimental Table, version 5. NASA Physical Sciences Informatics (PSI). | PSI-69. DOI 10.60555/mbq8-0451. Licence listed on the page: CC0-1.0. | https://psi.nasa.gov/physci/repo/data/investigations/PSI-69 | Nov 14, 2026 | The only data behind the two models and the list of real tests the console shows. |

What the PSI-69 page says about the investigation (read Nov 14, 2026): proposal
title "Droplet Flame Extinguishment in Microgravity"; flight platform International
Space Station; NASA Glenn Research Center; research area Combustion Science,
sub-area Spacecraft Fire Safety; hardware Combustion Integrated Rack and Multi-user
Droplet Combustion Apparatus; submitted 31 Jul 2016.

The modelling pipeline reads `data/raw/psi69_flex_experimental_table.tsv`.
The team transcribed the displayed PSI table across three pages and recorded
per-page SHA-256 checks. The official downloadable CSV is also in the repo as
`data/raw/psi_tables/PSI-69_Experimental table_FLEX.csv` and feeds the Oxygen map.

Second PSI source, for the NASA research page: the repository's search for
"combustion" (https://psi.nasa.gov/physci/repo/search?q=combustion), downloaded
Nov 14, 2026 as the JSON the page itself loads and kept unchanged in
`data/raw/psi_search/`. It returns 26 investigation records; 24 are listed under
combustion science and are shown. Each record carries the title, project type,
hardware, keywords, objectives and approach text of the investigation's PSI page.

What is in the FLEX table and what we used:

- 274 tests (methanol 157, heptane 117), run between March 2009 and December 2011.
- Columns used as model inputs: fuel, ambient pressure, initial O2, CO2 and He mole
  fractions, initial droplet diameter. All are known before ignition.
- Columns used as model targets: "Test end" and "Burning rate".
- Columns never used as inputs: burn time, visible flame extinction diameter.
- 252 tests are in scope (pressure at or below 1.1 atm and a known droplet size):
  methanol 146, heptane 106. Left out: 9 tests at 2 to 3 atm, 1 with pressure
  recorded as 0, 12 with no droplet diameter.
- The flame-outcome model uses 199 of them (172 "Extinction", 27 "Completion").
  The 53 "Disruption" tests are left out of that model and kept for burning rate.

The November 14, 2026 search yielded 25 Experimental Table CSV downloads, including
three from two records outside combustion science. The manifest records investigation,
version, DOI, licence, size and SHA-256 for each download. Git can normalize line
endings in a checkout. Run `python data/clean/fetch_psi_tables.py --verify` to
check the original download hashes offline, restoring CRLF in memory where necessary.

Nine tables from seven investigations supply the Oxygen map. They are FLEX
(PSI-69, 10.60555/mbq8-0451), CFI (PSI-39, 10.60555/m6pj-a914), two CFI-G tables
(PSI-159, 10.60555/cyt1-kh64), two Flame Design tables (PSI-10, 10.60555/w4zy-bt45),
BASS-II (PSI-25, 10.60555/4qc4-de67), Saffire-I (PSI-98, 10.60555/0t15-1z43) and
Saffire-II (PSI-99, 10.60555/2chp-m469). PSI lists CC0-1.0 for these except PSI-10,
whose licence field is empty. The BASS-II and Saffire-II tables also supply the
gas sensor and burn-length activities. [Download manifest](../data/raw/psi_tables/MANIFEST.json)

### Source rows for the Moon evidence check

Four of the nine mapped tables supply 746 published rows with measured ambient
oxygen and positive pressure. The filter compares values before rounding. All
20 rows at or above 30% oxygen and at or below 10.2 psi come from CFI-G normal
flames (PSI-159). For example, test 21106A4 on CSV line 32 records an oxygen
fraction of 0.3926 and approximate pressure of 0.50665 bar. The activity
preserves both original cells and the physical CSV line for each match.
[NASA investigation](https://doi.org/10.60555/cyt1-kh64) ·
[Original CSV](../data/raw/psi_tables/PSI-159_Experimental%20table_CFI-G_Normal%20Flames.csv) ·
[Row exporter](../data/clean/build_moon_evidence.py)

Every matching row describes a gas flame. The CFI-G table provides no per-test
gravity measurement, and the three mapped solid-material tables provide no
pressure column. These rows alone cannot establish how a solid panel burns in
lunar gravity. [Table definitions and units](../data/clean/build_tables.py)

## Other sources (papers, NASA pages)

The cabin-air buttons use locally bundled NASA images. Earth shows the Apollo 17
crew's Blue Marble photograph, AS17-148-22727 (NASA Johnson Space Center).
The Moon shows Galileo's PIA00405 mosaic (NASA/JPL/USGS). Mars shows the
Viking Orbiter 1 Valles Marineris mosaic, PIA04304 (NASA/JPL-Caltech).
[Earth](https://svs.gsfc.nasa.gov/30613/) · [Moon](https://science.nasa.gov/photojournal/earths-moon/) · [Mars](https://science.nasa.gov/resource/valles-marineris-the-grand-canyon-of-mars/) · [NASA media usage guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/)

The evidence lab plays the unmodified FLEX experiment clip from NASA SVS release 11318.
Credit: Science@NASA and NASA's Goddard Space Flight Center. The JPEG stills come from this
movie. Times shown on the player are seconds from the start of the clip. A proposed frame
pair describes the visibility of the flame rim. The public clip is linked at the investigation
level because its release page gives no experimental-table test ID. [NASA video and credits](https://svs.gsfc.nasa.gov/11318/)

For Saffire-I, the lab includes NASA’s camera sequence of a cotton–fiberglass
sample aboard Cygnus on June 14, 2016. Green LEDs illuminated the smoke. The
bundled WebM preserves the timing of NASA's 574-frame GIF (22.96 seconds).
The 0:02 and 0:22 buttons refer to the compilation clock. Credit: NASA.
[NASA experiment and caption](https://www.nasa.gov/centers-and-facilities/glenn/nasa-ignites-fire-experiment-aboard-space-cargo-ship/) · [Original NASA sequence](https://www.nasa.gov/wp-content/uploads/2016/06/saffire-1-burn.gif)

The additional offline clips retain the timing of the selected NASA footage. Cue
times on the player are relative to the bundled clip and may differ from time
elapsed in the experiment.

| Clip | Footage, edits and credit |
| --- | --- |
| FLEX-2 | A silent excerpt from 02:08–02:40 of *Spherical Flames*. NASA's on-screen annotations identify soot. Credit: Science@NASA and NASA’s Goddard Space Flight Center. [NASA release](https://svs.gsfc.nasa.gov/11640/) |
| SoFIE-GEL | The complete 46-second published sequence, transcoded to WebM. Blue patches appear to move around the sample as the visible flame fades. The camera records the changing light pattern. Credit: NASA Johnson Space Center. [NASA archive record](https://images.nasa.gov/details/SoFIE-GEL) |
| Saffire-V | The complete published video of ribbed PMMA (acrylic) aboard Cygnus, transcoded to 24 fps. The 76-second player clock follows the release. NASA identifies the thinner ribs and thicker material on the right of the sample. Credit: NASA Glenn Research Center, GRC-2021-CN-00008. [NASA archive record](https://images.nasa.gov/details/GRC-2021-CN-00008) |
| Saffire-VI | NASA's complete front and edge camera comparison of PMMA aboard Cygnus, transcoded without audio. The one-minute release shows the experiment at 20× speed and retains the original annotations. Credit: NASA. [NASA release](https://www.nasa.gov/centers-and-facilities/glenn/flame-burns-out-on-nasas-long-running-spacecraft-fire-experiment/) · [Source movie](https://www.nasa.gov/wp-content/uploads/2024/02/saf-vi-s8c3c4-1-sided-pmma-unmapped-jpeg-20x-plus-text-2.mp4) |

Two related videos are available online. NASA Johnson’s FLEX-2 recording shows an
opening in the flame shell appearing and closing repeatedly. NASA Glenn’s
Saffire-IV video shows glowing char behind a flame spreading across cotton–fiberglass
fabric. [NASA Johnson’s FLEX-2 recording](https://www.youtube.com/watch?v=qQQ1OHW1_F4) · [NASA Glenn’s Saffire-IV footage and caption](https://www.nasa.gov/humans-in-space/the-flame-of-discovery-grows-as-saffire-sets-new-fires-in-space/)

The checked-in result from `gemma4:12b` compares 24 one-second samples. It marks 0:08 and
0:09 as a candidate transition. Use `python server/analyze_flex_clip.py` with Ollama, Pillow
and imageio-ffmpeg to regenerate the input crops, saved candidate frames and model metadata.

The lab’s BASS-II answers come from the [original PSI-25 table](../data/raw/psi_tables/PSI-25_Experimental%20table_BASS-II.csv).
Reported oxygen and carbon dioxide concentrations are volume percentages. Carbon monoxide is
in ppm. Direction filters compare the recorded initial and final values of the requested gases.
Rows with a missing or nonnumeric reading for a requested comparison are counted separately.
Opening a result shows the original cells and CSV line. Run `python server/table_questions.py`
to regenerate the three offline questions from the source table.

The research home image is NASA’s colorized composite of a heptane droplet burning
in microgravity. The yellow trace follows the droplet and the surrounding structures
show soot. Image credit: NASA. The dashboard includes a resized WebP copy for offline
viewing. [Burning in Microgravity, May 25, 2011](https://www.nasa.gov/image-article/burning-microgravity/)

| Title | Link | What we took from it |
|---|---|---|
| NASA Space Apps Challenge 2026, challenge brief "Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data" (read Nov 14, 2026) | https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/ | What the challenge asks for. The three parts of spacecraft fire safety: prevention, detection, suppression. The Moon Base atmosphere: oxygen likely 30% or greater at 10.2 psi or less, against 14.7 psi at sea level on Earth. |
| PSI-69 investigation page, Description (Objectives, Approach) | https://psi.nasa.gov/physci/repo/data/investigations/PSI-69 | FLEX maps flammability limits of liquid fuels in microgravity and measures gaseous suppressants such as CO2 and He. A droplet either burns to completion or its flame goes out at a finite droplet size. The investigation used space-based data and ground-based tests. |
| F. A. Williams et al., "Research Requirements Document: Droplet Flame Extinguishment in Microgravity (FLEX)", Nov 4, 2005 (NASA Glenn) | https://www1.grc.nasa.gov/wp-content/uploads/FLEX_EIRD_v4.pdf | Two ways a droplet flame goes out: diffusive extinction for small droplets, radiative extinction for large ones. At high oxygen, droplets burn to completion instead. Planned pressures 0.5 to 1.5 atm. Mean burning rate falls as the initial droplet gets larger. CO2 is the suppressant in the US modules of the ISS. Without buoyancy, fires and suppressants behave differently than on Earth. |
| V. Nayagam, D. L. Dietrich, M. C. Hicks, F. A. Williams, "Methanol Droplet Combustion in Oxygen-Inert Environments in Microgravity", 2013, NASA NTRS 20130014061 | https://ntrs.nasa.gov/citations/20130014061 | FLEX methanol tests on the ISS: droplets of 1.5 to 4 mm, oxygen from 30% down to 12%, nitrogen with CO2 or helium, at 0.7 and 1 atm. Matches the ranges we see in the table. |
| NASA, "Studying Combustion and Fire Safety", Dec 26, 2023 | https://www.nasa.gov/missions/station/iss-research/studying-combustion-and-fire-safety/ | In microgravity there is no buoyant flow, so slow flames are rounded or spherical. FLEX studied suppressants and found cool flames: fuel kept reacting after the visible flame went out. |
| NASA Astronomy Picture of the Day, "Fire in Space", Aug 10, 2021 | https://science.nasa.gov/image-article/apod-2021-august-10-fire-in-space/ | On Earth flames are teardrop shaped because heated air rises. On the ISS flames are spheres. |
| C. K. Law, "Mechanisms of droplet combustion", 1982, NASA NTRS 19820015551 | https://ntrs.nasa.gov/citations/19820015551 | The classical d-squared law of droplet burning: the droplet diameter squared falls at a steady rate, the burning-rate constant. |

## Software and models that are not ours

| What | Link | Used for |
|---|---|---|
| Ollama 0.40 | https://ollama.com | Runs the language model on the team's PC and GPU. |
| Gemma 4, 12B (`gemma4:12b`, 8.0 GB, 4-bit), an open model from Google | https://ollama.com/library/gemma4 | The model behind "Ask the AI". Check its licence terms on that page before reusing it. |
| Python, pandas, NumPy, scikit-learn, matplotlib | https://www.python.org | Cleaning, training, the chart, the local server. |

## Claims shown in the console, and where each comes from

Wording in quotes is the text on screen. "Our model" means the two regressions in
`model/train_per_fuel.py` (own slopes for each fuel; the console's model since
Nov 15, 2026), trained only on the PSI-69 table.

| Text on screen | Source |
|---|---|
| “Completion chance among flames with a clear outcome” and “Visible extinction” | The PSI-69 outcome classifier is fit to 27 completions and 172 visible extinctions. Its two probabilities are conditional on a clear outcome. The 53 in-scope disruptions have no outcome label for this fit. |
| "range 34–75%" beside the main reading, and "Refitted on resampled tests, the completion estimate falls between ..." | `extinction_draws` in the export: 300 of the 1000 refits of the outcome formula on resampled tests (`model/train_per_fuel.py`). The range is where the middle 90 % of them fall. It shows how much the estimate hangs on which tests were run, not what the formula leaves out. |
| "Disruption chance N%" and "Modelled chance that a test like this is disrupted instead, with no clear outcome" | A third formula, `disruption` in the export, fitted on all 252 in-scope PSI-69 rows: "Disruption" against the other two endings. Held out, AUC 0.892 (`model/metrics.json`). "Disruption" is NASA's label. The table does not say what it means. |
| "Elevated modelled disruption chance" (amber) and the 50% disruption warning | The fitted disruption formula gives at least 50%. The nearby observed count uses the same-fuel FLEX rows within the dashboard’s distance threshold. At FLEX test 29 settings, the model estimates 52% and 0 of 2 nearby tests ended in disruption. |
| "Where the flame went out, the droplet had already lost a median of N% of its volume." and "By then the droplet had lost about N% of its volume." | PSI-69 columns "Droplet initial diameter" and "Visible flame extinction diameter": 1 minus the cube of their ratio, for nearby tests that ended in Extinction. Measured values, no model. Methanol droplets take up water, so for methanol the volume left is not all fuel. |
| "Picture is an illustration, not a simulation." | Our own statement. The picture only scales with the model outputs. |
| "In microgravity a droplet flame forms a sphere instead of a teardrop." | NASA "Studying Combustion and Fire Safety" (no buoyant flow, spherical flames) and NASA APOD "Fire in Space" (teardrop on Earth, sphere on the ISS). |
| “Burning rate” in mm²/s | The PSI-69 table labels the column “mm”. The d-squared law implies mm²/s. Across the 158 extinction rows with both diameters, a burn time and a burning rate, the median ratio of (initial diameter squared minus final diameter squared) / (burn time × table rate) is 0.95. The dashboard predicts this rate with linear regression. |
| "Burning rate ... means the droplet's diameter squared shrinks by that much every second." | The d-squared law (Law, 1982, NASA NTRS 19820015551). |
| "Droplet gone in about ... s, if the flame lasts" | Our arithmetic from the d-squared law: initial diameter squared divided by the modelled burning rate. Not a measured value. |
| "Range the experiments actually tested", "Inside the tested range", "outside tested range, ... to ..." | Smallest and largest value of each input over the 252 in-scope PSI-69 tests. |
| "No experiment mixed carbon dioxide and helium." | Checked in the PSI-69 table: no test has both above zero. |
| "rest of the air is nitrogen" and "gases add up to ... %, over 100 %" | The PSI-69 table gives O2, N2, CO2 and He mole fractions. The balance in every test is nitrogen (the four add up to 98 to 101% in the in-scope tests). |
| "Far from any real test" | Our distance to the closest same-fuel test, each input scaled by its tested range. The limit is the 95th percentile of each test's distance to its nearest neighbour. |
| "Closest real FLEX tests with this fuel, ranked (settings, outcome, measured burning rate)" and "Of ... nearby real tests with a clear outcome, ... burned until the fuel was gone." | Rows of the PSI-69 table, shown as recorded and ordered by our distance measure, closest first. |
| “No clear outcome in nearby tests” | “Disruption” is the PSI-69 label. The project treats these observations as inconclusive for the two-outcome model. Amber appears when the neighbourhood is populated exclusively by such rows. |
| "Earth-like air" (button): oxygen 21 %, pressure 1.00 atm | Sea-level air. The challenge brief gives Earth's sea-level pressure as 14.7 psi, which is 1 atm. |
| “Moon Base (expected)” | The brief gives at least 30% oxygen and at most 10.2 psi. The preset uses 30% and 0.694 atm. No FLEX row meets both thresholds. Seventeen FLEX rows are close on the high-pressure side. The default heptane preset has three nearby rows and all three ended in disruption. |
| Fitted effect of changing a setting | `model/train_per_fuel.py` fits separate slopes for each fuel. The explanation uses the direction and size of a fitted effect. A slope sign that changes in more than one in ten of 1,000 bootstrap refits is marked uncertain. This applies to pressure for both fuels and to CO₂ and starting diameter for methanol. |
| “Nearby real tests disagree with the model” | Inside the input range, at least two clear nearby outcomes are required. A majority must contradict a completion estimate below 30% or at least 65%. |
| “Checked on tests held out of training” | `model/train_per_fuel.py` evaluates five row-level folds repeated 20 times, with classifier penalty strength selected inside each outer training fold. `model/metrics.json` gives AUC 0.902 and burning-rate MAE 0.045 mm²/s. Similar settings can occur on both sides of a row split. |
| Displayed completion and extinction percentages | The primary reading limits the fitted percentage to 1–99%. The CSV exports the fitted completion estimate to one decimal place before this display limit. In repeated row-level evaluation 2.6% of rows assigned less than a 10% chance completed (`model/per_fuel/comparison.json`). |
| Completion threshold for “Could go either way” | The team's study threshold is 30% (`meta.watch`). Across repeated row-level evaluation, 64.1% of completions and 7.8% of visible extinctions received estimates of at least 30% (`model/metrics.json`). |
| ""Goes out" means the visible flame: FLEX found that fuel can keep reacting after it, in a cool flame." | NASA "Studying Combustion and Fire Safety". The PSI-69 column is named "Visible flame extinction diameter". |
| "This is a model reading for study and planning, not a crew procedure." | Our own statement. |
| NASA research page: "Prevention", "Detection", "Suppression" | The three parts of NASA's spacecraft fire-safety work named in the Space Apps challenge brief. |
| NASA research page: investigation title, "Flight experiment" or "Ground study", "Hardware", the PSI identifier | Copied from the PSI search records in `data/raw/psi_search/` ("Title", "Project Type", "Experiment Hardware", "Accession"). Spelling is PSI's. |
| NASA research page: "What it did", "What varied", "Why it matters", the fuel label, and the ranks "Direct", "Strong", "Related" | Written by an AI model (Claude) from the "Objectives", "Approach" and "Keywords" text of each PSI record, and for two entries from the challenge brief (ACME E-FIELD Flames mimicking partial gravity; ACME CFI-G having the highest oxygen levels). Kept in `data/clean/research_notes.json`. The page says they are AI-written. Not NASA's wording and not a NASA rating. |
| NASA research page: "... other investigations are not about ..." | Count of investigations the notes score 0 for that need. |
| Start screen: "A dashboard that summarizes, ranks and interprets NASA's microgravity combustion investigations, for fire safety on the way to the Moon and Mars." | Our description of the product, in the words of the challenge brief. |
| NASA research page: "24 NASA combustion investigations: 9 on gas flames, 6 on solid materials, ..." and "19 are flight experiments, 5 are ground studies" | Counted on the page from `research.js`. The kind of fuel is our label for each investigation; flight or ground is PSI's "Project Type" ("Microgravity Investigation" or "Ground Investigation"). |
| NASA research page: "Cabin air: oxygen and pressure" | A fourth ranking question, ours. It follows the challenge brief's section on spacesuits and oxygen (Moon Base air: 30% oxygen or more at 10.2 psi or less). Its 0 to 3 scores are AI-written from whether each PSI record says the tests varied oxygen and pressure. |
| Orbit view: rings "direct", "strong", "related", "not about this"; the numbers; the four fuel pictures | The same AI-written scores and ranks as the list, drawn as a picture. The pictures (sheet, sphere, flame, smoke puff) are our own drawings. |
| Star map: each star, its colour and shape, its size, "N real heptane tests, one star each" | One PSI-69 test per star, at its recorded oxygen and droplet diameter. Colour and shape show the recorded "Test end"; size follows the recorded "Burning rate". The stars are drawings, not images of anything. |
| Star map: "FLEX test N: ..., went out before the fuel was gone" for a picked star | That row of the PSI-69 table, as recorded. |
| Replay of a FLEX test | “Droplet initial diameter”, “Burn time” and “Visible flame extinction diameter” come from PSI-69. The animation interpolates diameter squared over measured burn time. If a completion has no end diameter, zero depicts depletion and the caption identifies that convention. Missing time or a missing required diameter prevents replay. |
| Fire drill: the settings shown, "It burned until the fuel was gone." or "It went out before the fuel was gone.", "This was FLEX test ..., measured burning rate ..." | One row of the PSI-69 table per round, shown as recorded: its inputs, its "Test end" ("Completion" or "Extinction") and its "Burning rate". Ten rows are drawn at random, five of each outcome. |
| Fire drill model score and predicted answer | `console/index.html` compares the fitted probability of completion among clear outcomes to 0.5 before rounding the displayed percentage. These same rows trained the model. The drill score measures performance on its game rounds. |
| Flame picture that pulses, grows, fades, or becomes a question mark; controller buzz | Our own illustration and effects. The pulse speeds up with the modelled burning rate. Not a simulation or a recording. |
| Fire drill: "Streak", "Best on this device", "Rank: Cadet / Crew member / Flight engineer / Fire marshal" | Game scoring, ours. The best score is kept in the browser on that device only. |
| Fire drill: "Ember, the team's on-board AI, thinks: ..." | One sentence written at run time by the local language model from that test's row and the PSI-69 record. It is a guess at a reason, labelled as the AI's, not NASA's explanation. |
| "Ask Ember": the preset questions | Our own wording. The Moon Base question uses the oxygen and pressure figures from the challenge brief. |
| “Ask Ember” answers | Ollama generates answers at runtime. For research questions, `server/serve.py` builds a prompt from the catalogue, retrieved PSI records, any applicable dashboard ranking, the table summary and challenge context. Reading questions use the current dashboard text and FLEX record. A citation is a model output to check against PSI. |
| Ember model label, voice and elapsed time | The server supplies the answering model and hardware label. The browser measures elapsed time. `console/index.html` selects an English speech voice only when the browser reports `localService === true`. If none is available the answer stays on screen. |
| Oxygen map: every mark; "N rows in its PSI table, N with a readable oxygen value. Oxygen ... to ... %. Pressure ... to ... atm." | One mark per row of that investigation's PSI Experimental Table, read by `data/clean/build_tables.py`. Oxygen columns: FLEX "O initial ambient composition" (the table drops the subscript 2), CFI "Oxygen", CFI-G normal flames "XO2 before test", Flame Design normal flames "XO2 (init)", BASS-II "Calibrated initial O2 % by vol", Saffire "Percent O2" (a cell such as "21.5 - 21.7" is read as its middle). Pressure: FLEX mmHg / 760, CFI atm, CFI-G bar / 1.01325, Flame Design "pinit (atm)". |
| Oxygen map headline of 746 rows, 20 matching, 17 near | `data/clean/build_tables.py` counts ambient oxygen and valid pressure rows from FLEX, CFI, normal CFI-G and normal Flame Design tables. Twenty CFI-G rows meet ≥30% oxygen and ≤10.2 psi. No FLEX row meets both limits. Seventeen FLEX rows have ≥30% oxygen and >10.2 to ≤10.5 psi. The upper limit of 10.5 is the project’s comparison band. FLEX test 114 has invalid zero pressure. The published CFI table repeats eight rows. The denominator counts published rows and FLEX has no row-level flight/ground label. |
| “Moon Base thresholds”, “Spacesuit: 100 % oxygen at 4.3 psi”, “Earth at sea level” | The Space Apps brief gives the Moon Base and spacesuit references. The Earth marker uses 21% oxygen at one atmosphere. The oxygen-only view marks the oxygen threshold, while the pressure view can show both thresholds. |
| Oxygen map: "This is the oxygen in the burner flow of an inverse flame ... It is not a cabin atmosphere" and the hollow marks | The CFI-G and Flame Design "Inverse" tables give XO2 for the gas flowing from the burner; the challenge brief describes these inside-out flames (up to 85 % oxygen from the burner into nitrogen and fuel). |
| "Mars base (assumed)" (button) and "Cabin air for a Mars base is an assumption ..." | Ours. The challenge brief names bases on the Martian surface but gives cabin air only for the Moon Base and pressurized rovers, so the same air is used and labelled as assumed. |
| Background scene: the Earth, the Moon or Mars | Our own drawing. It follows the cabin-air button and carries no data. |
| Zoomed star map: test numbers, grid, and the dashed lines "model 25 %", "model 50 %", "model 75 %" | Test numbers are the PSI-69 "FLEX Test #". The dashed lines are our outcome model solved for those chances at the pressure, carbon dioxide and helium set now. They are not NASA's. |
| Ignite outcome, stopping diameter and tally | The droplet follows the d-squared law at the fitted burning rate. The model samples a clear outcome. For extinction, it draws from up to eight nearby same-fuel PSI-69 extinction rows with a recorded endpoint and applies the end-to-start diameter ratio, capped at 0.95, to the simulated droplet. With no eligible endpoint it labels an assumed ratio of 0.5. |
| Ignite picture: igniter wires, thin spherical flame, soot shell in a heptane flame, faint haze after a heptane flame goes out, "illustration, not footage" | Our own drawing, made to resemble FLEX footage. The haze stands for the cool flame FLEX found (NASA "Studying Combustion and Fire Safety"); it is not modelled. |
| “Outside the FLEX model range”, “Back within the FLEX input ranges”, “All nearby FLEX outcomes are inconclusive” and the disagreement banner | These messages follow the input-range, neighbourhood and disagreement rules in `console/index.html`. A completion estimate describes a liquid droplet outcome and does not quantify overall cabin fire risk. |
| "Download tests (CSV)", "Send to base", "Sent N real FLEX tests to ..." | The file holds the 252 in-scope PSI-69 tests as recorded, with three extra columns that are ours (the model's chance of burning all the fuel, its chance of a disruption, and its burning rate) and a source column naming PSI-69 and its DOI. |
| Ember’s table-count answers | `data/clean/psi_tables_summary.json` supplies counts from the PSI tables as context. The 18 saved answers passed a smoke test of numeric token overlap and name fragments near bracketed PSI IDs. Human scientific review of that set remains pending. |
| Explanation panel prediction | The two percentages cover only completion and visible extinction. Beyond the model’s input range the panel substitutes “Outside the tested conditions. Do not rely on this prediction.” for the numbers. |
| Explanation panel: "Real-test evidence", "N nearby test(s): ... burned to completion, ... went out early, ... had no clear outcome.", "Closest: FLEX test N ... Even this test is far from the current settings." | Counts over the nearby PSI-69 tests, the same ones as in the confidence box. |
| Explanation panel: "Limitations": "Experimental coverage does not guarantee accuracy for this exact combination.", "There is no close experimental match for these conditions.", "Nearby tests have no clear flame outcome, so they cannot confirm this prediction.", "Nearby real tests disagree with the model. Give the experimental evidence priority.", "These conditions are near the edge of the tested range.", "Mars cabin air is an assumed scenario, not a Mars-gravity validation." | Our own statements, each tied to the same rule as the confidence box (range, distance to the closest test, outcomes of nearby tests, the Mars button). |
| Explanation panel: "Visible flame extinction does not establish safety; cool-flame reactions may continue." | NASA "Studying Combustion and Fire Safety" (cool flames found in FLEX). The safety wording is ours. |
| Comparison: "Baseline A", "Current B", "+... pp vs A", "+... mm²/s vs A", "Data support" | Our model's outputs for two sets of settings, and their difference. "pp" is percentage points. Not a measurement. |
| Comparison: "Delta withheld: unsupported conditions" and "Differences are model estimates, not a ranking of overall fire safety." | Our rule: when either set of settings is outside the tested range no difference is shown. The second sentence is our own statement. |
| NASA research page: "Fire safety for the Moon and Mars, from NASA's microgravity experiments" | Our description of the product. The Moon and Mars are the destinations the challenge brief names. |
| "What would put this flame out?": "Lower oxygen to N %", "Add carbon dioxide to N %", "Add helium to N %", the percentage beside each, "under the watch level", "not enough alone", "(the most FLEX tested)" | Our outcome model, read at other settings (`console/advisor.js`). One gas is moved in slider steps through the range the 252 in-scope PSI-69 tests cover while every other setting is held. The value shown is the first at which the displayed completion estimate is under the team's 30 % study threshold (`meta.watch`), or the end of the tested range when none is. A model estimate, not a measurement and not a suppression method. |
| "What would put this flame out?": "Nearby real tests: N of M with a clear outcome went out.", "One nearby real test has a clear outcome: ...", "Nearby real tests: N. All ended in disruption, with no clear outcome.", "No real test is close to these settings, so the model is filling a gap." | Counts over the same-fuel PSI-69 rows within the dashboard's distance threshold of the changed settings, the rule the confidence box uses. |
| "What would put this flame out?": "... is left out: for methanol the tests do not settle which way it pushes.", "... no FLEX test mixed it with ...", "Pressure is not offered: the tests sat at two pressures, about 0.7 and 1 atm, so its direction is not known." | The same rule as the explanation: a slope whose sign changes in more than one in ten of 1,000 bootstrap refits is not used (pressure for both fuels, carbon dioxide for methanol). No PSI-69 test has carbon dioxide and helium both above zero. The in-scope pressures run from 0.693 to 1.019 atm in two groups. |
| "What would put this flame out?": "under the 30 % oxygen of Moon Base (expected) air" | The challenge brief gives the Moon Base cabin air as 30 % oxygen or more. |
| "What would put this flame out?": "It looks only at the flame: it does not check that the changed air is safe to breathe.", "Not a crew procedure." | Our own statements. The dashboard holds no data on what air a crew can breathe. |
| "What would put this flame out?": "It reads how FLEX tests with such settings ended. It is not a proven effect of making the change." | Ours. The model is fitted to the tests NASA ran, in which pressure and the gas mix were not varied independently (`docs/model-design-audit.md`, holes 6 and 11). |
| "What would put this flame out?": "Under the watch level is not "out": held out of training, 22 % of the tests the model rated 20 to 30 % still burned all their fuel." | `model/per_fuel/comparison.json`, `calibration_held_out`: 0.22 for estimates from 0.2 to 0.3, about 15 tests per repeat, five row-level folds repeated 20 times. `tests/test_advisor.cjs` checks the figure against that file. |
| Explanation panel, Moon Base preset: "This is Moon Base cabin air only, not a lunar-gravity validation." and "The FLEX records shown here do not establish a lunar-gravity outcome." | Ours. The preset sets oxygen and pressure only. The model has no gravity input and the PSI-69 table has no gravity column. |
| Tour: the nine cards | Our own description of the dashboard. "24 ... investigations" is counted from `research.js`, "199 real FLEX tests" is `meta.rows` in the export, "Ten real FLEX tests" is the number of drill rounds. The cards say the research ranking is AI-rated. |
| Fire drill: "Rounds played", each line "FLEX N · fuel · oxygen · droplet size", "Burned all its fuel" or "Went out first", "You ✓/✕", "Model ✓/✕" | The PSI-69 row of each round already played, as recorded, with whether the player's answer and the model's answer matched its "Test end". |

## Sources for the three evidence activities

| Activity | Source observations and calculation |
|---|---|
| Earth or orbit? | Saffire-II, PSI-99, DOI 10.60555/2chp-m469. Samples 2-2, 2-5, 2-3 and 2-1 supply paired 1-g and flight burn lengths and the flight conditions. “Complete” is drawn to the full recorded specimen length and “~ 0” is displayed as approximately zero. |
| Read the sensors / What did oxygen miss? | BASS-II, PSI-25, DOI 10.60555/4qc4-de67. Tests B18, T2, F2 and B17 supply initial and final calibrated O₂ and CO₂ volume percentages and CO in ppm. The answer compares the recorded initial and final CO readings. |
| Find the counterexample | FLEX, PSI-69, DOI 10.60555/mbq8-0451. The search requires identical fuel, oxygen, CO₂ and helium and the opposite clear outcome. Among eligible rows, it minimizes the Euclidean distance in pressure and initial diameter after scaling each by its observed range. The panel labels both odds as estimates from a model fitted on these rows. |

The first two activities show their original CSV line for each record. The offline
exporter reads the selected columns directly from the downloaded files. [Case exporter](../data/clean/build_evidence.py) · [FLEX matching code](../console/counterexample.js)

## What we do not claim

- That every row is a space experiment. The PSI-69 page says the investigation used
  both space-based data and ground-based tests, and the table has no column that
  tells them apart.
- That all completions can be predicted from the starting conditions. The current
  per-fuel classifier found 52.4% of completions at a 50% cutoff
  (`model/metrics.json`). The earlier pooled model's five-seed audit reported 23.7%.
- The outcome regression is fitted on 199 clear outcomes and the burning-rate
  regression on 252 measurements. Neither is a physical model of flame behaviour.
- That a flame that "goes out" is safe. The outcome is about the visible flame.
- Anything outside the tested ranges. The console marks those readings as unknown.
- That the Oxygen map says how flammable anything is. It shows where tests were run.
- That a Mars base will have the air of the Mars base button. That air is assumed.
- That the research summaries and ranks are NASA's. They are an AI model's reading
  of the PSI records, and the team has not yet reviewed them line by line.
