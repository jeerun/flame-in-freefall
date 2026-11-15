# Clean data

`flex_clean.csv` is built from `data/raw/` by `build_clean.py`. One row per test, 274 rows.

| Column | Meaning |
|---|---|
| test, flex_id, date, gmt | As in the source |
| fuel | `methanol` or `heptane` |
| pressure_atm | Ambient pressure, converted from mmHg (divide by 760) |
| o2_pct, n2_pct, co2_pct, he_pct | Initial gas mix, mole fraction times 100 |
| d0_mm | Initial droplet diameter |
| ext_diameter_mm | Droplet diameter when the visible flame went out |
| burn_rate_mm2_s | Burning-rate constant K |
| burn_time_s | Burn time. "~6" and "~9" in the source are stored as 6 and 9 and flagged |
| test_end | `Extinction`, `Completion` or `Disruption` |
| flags | Anything unusual about the row |

## Research notes

`research_notes.json` holds the plain-language notes behind the NASA research page:
for each of the 24 combustion investigations a short name, the kind of fuel, a
summary, what varied between tests, why it matters for fire safety, and a 0 to 3
relevance score for prevention, detection and suppression. An AI model (Claude) wrote
them on Nov 14, 2026 from the objectives and approach text in
`data/raw/psi_search/combustion_investigations.json`. They are a reading of NASA's
text, not NASA's words, and nobody on the team has reviewed them line by line yet.
The score scale is described at the top of the file.

`build_research.py` joins those notes with the facts in the raw PSI file (title,
project type, hardware) and writes `console/research.js`. It stops if a combustion
investigation in the PSI file has no note, or a note has no PSI record. Two of the 26
search results are left out because PSI lists them under other research areas
(PSI-108 fluid physics, PSI-181 materials science).

## FLEX table

Cleaning rules: the empty last row is dropped; blank cells stay blank; cells the
source shows as an unreadable character become blank and are flagged; pressure 0
(test 114) becomes blank and is flagged. No row is removed and no value is guessed.
