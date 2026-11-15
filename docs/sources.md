# Sources

Every dataset and source the project uses, and where each sentence on the console
screen comes from. The submission form asks for this.

## NASA data

| Dataset | Identifier | Link | Downloaded on | What we used it for |
|---|---|---|---|---|
| Flame Extinguishment Experiment (FLEX), Experimental Table, version 5. NASA Physical Sciences Informatics (PSI). | PSI-69. DOI 10.60555/mbq8-0451. Licence listed on the page: CC0-1.0. | https://psi.nasa.gov/physci/repo/data/investigations/PSI-69 | Nov 14, 2026 | The only data behind the two models and the list of real tests the console shows. |

What the PSI-69 page says about the investigation (read Nov 14, 2026): proposal
title "Droplet Flame Extinguishment in Microgravity"; flight platform International
Space Station; NASA Glenn Research Center; research area Combustion Science,
sub-area Spacecraft Fire Safety; hardware Combustion Integrated Rack and Multi-user
Droplet Combustion Apparatus; submitted 31 Jul 2016.

How we got the table: we did not fetch the downloadable CSV. We read the
Experimental Table shown on the page (three pages of 100 rows), saved it as
tab-separated text in `data/raw/`, and checked each page with SHA-256 against a hash
computed inside the browser. If someone downloads the official CSV, compare the two
and keep the official one.

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

| Experimental Tables of the combustion investigations in PSI: 25 CSV files, saved unchanged in `data/raw/psi_tables/`. Nine of them are read for the Oxygen map. | FLEX PSI-69 (10.60555/mbq8-0451), CFI PSI-39 (10.60555/m6pj-a914), ACME CFI-G PSI-159 (10.60555/cyt1-kh64, two tables), ACME Flame Design PSI-10 (10.60555/w4zy-bt45, two tables), BASS-II PSI-25 (10.60555/4qc4-de67), Saffire-I PSI-98 (10.60555/0t15-1z43), Saffire-II PSI-99 (10.60555/2chp-m469). PSI lists CC0-1.0 for all of these except PSI-10, where the licence field is empty. Version, DOI, licence and SHA-256 of every file: `data/raw/psi_tables/MANIFEST.json`. | https://psi.nasa.gov/physci/repo/data/investigations/PSI-39 (replace the id for the others) | Nov 14, 2026, with `data/clean/fetch_psi_tables.py` | The oxygen level of each test and, where the table has one, the pressure: the Oxygen map and the counts given to Ember. Nothing else from these tables is used. |

## Other sources (papers, NASA pages)

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
| "Chance the flame burns until the fuel is gone" and "Chance it goes out before the fuel is gone" | Our logistic model of the PSI-69 "Test end" column: "Completion" against "Extinction". The meaning of the two outcomes is from the PSI-69 Approach text and the FLEX requirements document. |
| "Picture is an illustration, not a simulation." | Our own statement. The picture only scales with the model outputs. |
| "In microgravity a droplet flame forms a sphere instead of a teardrop." | NASA "Studying Combustion and Fire Safety" (no buoyant flow, spherical flames) and NASA APOD "Fire in Space" (teardrop on Earth, sphere on the ISS). |
| "Burning rate ... mm²/s" | Our linear model of the PSI-69 "Burning rate" column. The page prints the unit as "mm"; we read it as mm²/s. Check: for 158 tests, (initial diameter squared minus extinction diameter squared) divided by burn time comes to a median of 0.95 times the table value. |
| "Burning rate ... means the droplet's diameter squared shrinks by that much every second." | The d-squared law (Law, 1982, NASA NTRS 19820015551). |
| "Droplet gone in about ... s, if the flame lasts" | Our arithmetic from the d-squared law: initial diameter squared divided by the modelled burning rate. Not a measured value. |
| "Range the experiments actually tested", "Inside the tested range", "outside tested range, ... to ..." | Smallest and largest value of each input over the 252 in-scope PSI-69 tests. |
| "No experiment mixed carbon dioxide and helium." | Checked in the PSI-69 table: no test has both above zero. |
| "rest of the air is nitrogen" and "gases add up to ... %, over 100 %" | The PSI-69 table gives O2, N2, CO2 and He mole fractions. The balance in every test is nitrogen (the four add up to 98 to 101% in the in-scope tests). |
| "Far from any real test" | Our distance to the closest same-fuel test, each input scaled by its tested range. The limit is the 95th percentile of each test's distance to its nearest neighbour. |
| "Closest real FLEX tests with this fuel, ranked (settings, outcome, measured burning rate)" and "Of ... nearby real tests with a clear outcome, ... burned until the fuel was gone." | Rows of the PSI-69 table, shown as recorded and ordered by our distance measure, closest first. |
| "Disruption, no clear outcome." and "But the ... nearby real tests had no clear outcome, so the percentage leans on tests farther away." | "Disruption" is a value of the PSI-69 "Test end" column. The page has no Read Me that defines it. Treating it as "no clear outcome" is our reading. |
| "Earth-like air" (button): oxygen 21 %, pressure 1.00 atm | Sea-level air. The challenge brief gives Earth's sea-level pressure as 14.7 psi, which is 1 atm. |
| "Moon Base (expected)" (button) and "Cabin air is the Moon Base case from the challenge brief: oxygen 30 % or more at 10.2 psi (0.69 atm) or less." | The Space Apps challenge brief, section on spacesuits and oxygen concentration. The button sets oxygen 30 % and 10.2 psi, which is 0.694 atm and is shown as 0.69. FLEX ran tests at that pressure and oxygen level. |
| "... pushes toward going out early" and "... pushes toward burning until the fuel is gone" | The sign and size of our model's coefficients for the chosen fuel. Not a NASA statement. For heptane the directions agree with the FLEX documents: more oxygen favours burning to completion, larger droplets favour (radiative) extinction, CO2 and helium act as suppressants. For methanol only the oxygen and helium directions are settled by the tests. Pressure rests on two levels and is settled for neither fuel. Where a direction is not settled the page says so (see the row on that sentence). |
| "Nearby real tests disagree with the model" | Our rule: most nearby PSI-69 tests with a clear outcome ended the other way. |
| "Checked on tests held out of training: AUC 0.90 ... burning rate off by 0.045 mm²/s on average" | `model/metrics.json`, written by `model/train_per_fuel.py`: 5-fold cross-validation repeated 20 times, with the penalty strength picked inside each training fold. |
| "No chance is shown below 1 % or above 99 %: 199 tests cannot support more certainty than that." | Our display rule. The model itself can come out at 0.1 % or 99.9 %; held out, 3 % of the tests it put under 10 % did burn to completion (`model/per_fuel/comparison.json`). The CSV file keeps the model's unrounded output. |
| "The tests do not settle which way this setting pushes for methanol, so do not lean on this line." (or "for heptane") | `meta.unsure` in the export: the settings whose slope changes sign in more than one in ten of 1000 refits on resampled tests (`model/train_per_fuel.py`). Pressure for both fuels; droplet size and carbon dioxide for methanol. |
| "Watch: this flame has a real chance of burning all its fuel." and "Could go either way ..." from 30 % | `meta.watch` in the export, 0.30, our threshold. Held out, 64 % of the tests that burned to completion and about 8 % of those that went out sit at or above it (`model/metrics.json`). |
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
| Replay: "Replay of FLEX test N, ...x speed: ... s, droplet ... mm" and "FLEX test N burned for ... s. Then the flame went out with the droplet at ... mm." | Start diameter, burn time and end diameter are the PSI-69 values for that test ("Droplet initial diameter", "Burn time", "Visible flame extinction diameter"). Between them the diameter squared falls in a straight line, which is the d-squared law (Law, 1982). Where the record has no end diameter for an extinction test, it is worked out from the recorded burning rate and marked "about". The glow is an illustration. |
| Fire drill: the settings shown, "It burned until the fuel was gone." or "It went out before the fuel was gone.", "This was FLEX test ..., measured burning rate ..." | One row of the PSI-69 table per round, shown as recorded: its inputs, its "Test end" ("Completion" or "Extinction") and its "Burning rate". Ten rows are drawn at random, five of each outcome. |
| Fire drill: "The model gave it ... % to burn all its fuel, so it answered ...", the score rows "You" and "Model", "Final score ..." | Our model's output for that test's settings, counted as "burned all its fuel" at 50 % or more. The model was trained on these same tests, as the page says, so this score is a game score and not an accuracy figure. |
| Flame picture that pulses, grows, fades, or becomes a question mark; controller buzz | Our own illustration and effects. The pulse speeds up with the modelled burning rate. Not a simulation or a recording. |
| Fire drill: "Streak", "Best on this device", "Rank: Cadet / Crew member / Flight engineer / Fire marshal" | Game scoring, ours. The best score is kept in the browser on that device only. |
| Fire drill: "Ember, the team's on-board AI, thinks: ..." | One sentence written at run time by the local language model from that test's row and the PSI-69 record. It is a guess at a reason, labelled as the AI's, not NASA's explanation. |
| "Ask Ember": the preset questions | Our own wording. The Moon Base question uses the oxygen and pressure figures from the challenge brief. |
| "Ask Ember": the answers, on screen and read aloud | Written at run time by a language model (Gemma 4 12B, run with Ollama on the team's PC). The voice is the browser's own speech synthesis reading the same text. `server/serve.py` gives it only: the one-line catalogue from `research_notes.json`, the PSI "Objectives", "Approach", "Keywords" and hardware text of the four records that share the most words with the question, three facts from the challenge brief, or, on the Flame console page, the text of the reading on screen plus the PSI-69 record. It is told to cite PSI ids and not to guess. Its wording is not NASA's and can be wrong; the panel says so. |
| "Ask Ember": "the on-board AI: gemma4:12b on this team's NVIDIA GeForce RTX 5080. No internet needed: nothing leaves the local network.", "Ember thinks on: Auto / ..." and "Answered in ... s by Ember (gemma4:12b on this team's NVIDIA GeForce RTX 5080)" | Reported by the server: the model name it was started with, the graphics card name from `nvidia-smi`, and the time measured in the browser. |

| Oxygen map: every mark; "N rows in its PSI table, N with a readable oxygen value. Oxygen ... to ... %. Pressure ... to ... atm." | One mark per row of that investigation's PSI Experimental Table, read by `data/clean/build_tables.py`. Oxygen columns: FLEX "O initial ambient composition" (the table drops the subscript 2), CFI "Oxygen", CFI-G normal flames "XO2 before test", Flame Design normal flames "XO2 (init)", BASS-II "Calibrated initial O2 % by vol", Saffire "Percent O2" (a cell such as "21.5 - 21.7" is read as its middle). Pressure: FLEX mmHg / 760, CFI atm, CFI-G bar / 1.01325, Flame Design "pinit (atm)". |
| Oxygen map: "Of 746 microgravity tests whose NASA table records both the oxygen and the pressure of the surrounding gas, 20 were run in Moon Base air (CFI-G, normal flames). 17 more sit just above its pressure line, at 10.2 to 10.5 psi (FLEX)." | Counted by `build_tables.py` over FLEX, CFI, CFI-G normal flames and Flame Design normal flames: rows with oxygen at or above 30 % and pressure at or below 10.2 psi (0.694 atm), and rows with that oxygen between 10.2 and 10.5 psi. The 10.5 psi band is ours: FLEX chamber pressures aimed at 10.2 psi were recorded as 10.3 to 10.5 psi. FLEX test 114 has pressure 0 in the table and is left out of the pressure count. |
| Oxygen map: "Moon Base air: 30 % oxygen or more at 10.2 psi or less", "Spacesuit: 100 % oxygen at 4.3 psi", "Earth at sea level", "Earth air, 21 %" | The Space Apps challenge brief (spacesuits and oxygen concentration). 21 % is sea-level air. |
| Oxygen map: "This is the oxygen in the burner flow of an inverse flame ... It is not a cabin atmosphere" and the hollow marks | The CFI-G and Flame Design "Inverse" tables give XO2 for the gas flowing from the burner; the challenge brief describes these inside-out flames (up to 85 % oxygen from the burner into nitrogen and fuel). |
| "Mars base (assumed)" (button) and "Cabin air for a Mars base is an assumption ..." | Ours. The challenge brief names bases on the Martian surface but gives cabin air only for the Moon Base and pressurized rovers, so the same air is used and labelled as assumed. |
| Background scene: the Earth, the Moon or Mars | Our own drawing. It follows the cabin-air button and carries no data. |
| Zoomed star map: test numbers, grid, and the dashed lines "model 25 %", "model 50 %", "model 75 %" | Test numbers are the PSI-69 "FLEX Test #". The dashed lines are our outcome model solved for those chances at the pressure, carbon dioxide and helium set now. They are not NASA's. |
| Ignite: "This run: the flame went out after ... s, with the droplet at ... mm (stopping size borrowed from real FLEX test N)", "it burned all its fuel in ... s", the tally | Our model: the droplet follows the d-squared law at the modelled burning rate, the outcome of a run is drawn at random with the modelled chance, and the stopping size is the end-to-start diameter ratio of one of the eight closest real PSI-69 tests that went out. A run of the model, not a measurement. |
| Ignite picture: igniter wires, thin spherical flame, soot shell in a heptane flame, faint haze after a heptane flame goes out, "illustration, not footage" | Our own drawing, made to resemble FLEX footage. The haze stands for the cool flame FLEX found (NASA "Studying Combustion and Fire Safety"); it is not modelled. |
| Banners: "Outside what NASA tested. Treat the fire risk as unknown.", "Back inside what NASA tested.", "High fire risk: this flame is likely to burn all its fuel.", "Real tests nearby disagree with the model. Trust the tests." | The same rules as the confidence box. "High" is our threshold: a modelled chance of 65 % or more to burn all the fuel. Held out, 93 % of the tests the model put there did burn to completion (`model/per_fuel/comparison.json`). |
| "Download tests (CSV)", "Send to base", "Sent N real FLEX tests to ..." | The file holds the 252 in-scope PSI-69 tests as recorded, with two extra columns that are ours (the model's chance and burning rate) and a source column naming PSI-69 and its DOI. |
| "Ask Ember": answers that quote counts such as "20 test rows that match the Moon Base air" | The counts `build_tables.py` made from the PSI test tables, which the server gives the model as text (`data/clean/psi_tables_summary.json`). |

| Explanation panel: "Prediction", "... % estimated chance of burning until the fuel is gone; ... % of going out first. Burning rate: ... mm²/s.", "Outside the tested conditions. Do not rely on this prediction." | The same model outputs as the main reading. Outside the tested range the numbers are replaced by the warning. |
| Explanation panel: "Real-test evidence", "N nearby test(s): ... burned to completion, ... went out early, ... had no clear outcome.", "Closest: FLEX test N ... Even this test is far from the current settings." | Counts over the nearby PSI-69 tests, the same ones as in the confidence box. |
| Explanation panel: "Limitations": "Experimental coverage does not guarantee accuracy for this exact combination.", "There is no close experimental match for these conditions.", "Nearby tests have no clear flame outcome, so they cannot confirm this prediction.", "Nearby real tests disagree with the model. Give the experimental evidence priority.", "These conditions are near the edge of the tested range.", "Mars cabin air is an assumed scenario, not a Mars-gravity validation." | Our own statements, each tied to the same rule as the confidence box (range, distance to the closest test, outcomes of nearby tests, the Mars button). |
| Explanation panel: "Visible flame extinction does not establish safety; cool-flame reactions may continue." | NASA "Studying Combustion and Fire Safety" (cool flames found in FLEX). The safety wording is ours. |
| Comparison: "Baseline A", "Current B", "+... pp vs A", "+... mm²/s vs A", "Data support" | Our model's outputs for two sets of settings, and their difference. "pp" is percentage points. Not a measurement. |
| Comparison: "Delta withheld: unsupported conditions" and "Differences are model estimates, not a ranking of overall fire safety." | Our rule: when either set of settings is outside the tested range no difference is shown. The second sentence is our own statement. |

## What we do not claim

- That every row is a space experiment. The PSI-69 page says the investigation used
  both space-based data and ground-based tests, and the table has no column that
  tells them apart.
- That the model is physics. It is two straight-line fits to 252 tests, with one set of slopes per fuel.
- That a flame that "goes out" is safe. The outcome is about the visible flame.
- Anything outside the tested ranges. The console marks those readings as unknown.
- That the Oxygen map says how flammable anything is. It shows where tests were run.
- That a Mars base will have the air of the Mars base button. That air is assumed.
- That the research summaries and ranks are NASA's. They are an AI model's reading
  of the PSI records, and the team has not yet reviewed them line by line.
