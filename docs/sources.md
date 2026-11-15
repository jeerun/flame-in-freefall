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

What is in it and what we used:

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

## Claims shown in the console, and where each comes from

Wording in quotes is the text on screen. "Our model" means the two regressions in
`model/train.py`, trained only on the PSI-69 table.

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
| "... pushes toward going out early" and "... pushes toward burning until the fuel is gone" | The sign and size of our model's coefficients. Not a NASA statement. Three directions agree with the FLEX documents: more oxygen favours burning to completion, larger droplets favour (radiative) extinction, CO2 and helium act as suppressants. The pressure direction rests on only two pressure levels. |
| "Nearby real tests disagree with the model" | Our rule: most nearby PSI-69 tests with a clear outcome ended the other way. |
| "Checked on tests held out of training: AUC 0.81 ... burning rate off by 0.048 mm²/s on average" | `model/metrics.json`: 5-fold cross-validation repeated 20 times. |
| ""Goes out" means the visible flame: FLEX found that fuel can keep reacting after it, in a cool flame." | NASA "Studying Combustion and Fire Safety". The PSI-69 column is named "Visible flame extinction diameter". |
| "This is a model reading for study and planning, not a crew procedure." | Our own statement. |

## What we do not claim

- That every row is a space experiment. The PSI-69 page says the investigation used
  both space-based data and ground-based tests, and the table has no column that
  tells them apart.
- That the model is physics. It is two straight-line fits to 252 tests.
- That a flame that "goes out" is safe. The outcome is about the visible flame.
- Anything outside the tested ranges. The console marks those readings as unknown.
