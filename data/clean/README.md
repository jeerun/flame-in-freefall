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
relevance score for prevention, detection, suppression and cabin air (how much the
tests say about oxygen level and pressure). The notes interpret the objectives and
approach recorded in `data/raw/psi_search/combustion_investigations.json`.
A line-by-line review of the notes is still pending.
The score scale is described at the top of the file.

`build_research.py` joins those notes with the facts in the raw PSI file (title,
project type, hardware) and writes `console/research.js`. It stops if a combustion
investigation in the PSI file has no note, or a note has no PSI record. Two of the 26
search results are left out because PSI lists them under other research areas
(PSI-108 fluid physics, PSI-181 materials science).

## PSI test tables

`build_tables.py` reads nine of the tables in `data/raw/psi_tables/` and takes one
thing from each row: the oxygen level of the test and, where the table has it, the
pressure. It writes `console/tables.js` for the Oxygen map and
`psi_tables_summary.json`, the same counts as sentences, for the local AI. Which
column is read from which table, and what its oxygen value means, is listed at the
top of the script. Nothing is filled in: a row whose oxygen cell is not a number
("RAMP", "LOW O2", blank) is counted as unread and not plotted, a cell such as
"21.5 - 21.7" is read as its middle, and a pressure of 0 (FLEX test 114) is treated
as no pressure. For inverse gas flames the oxygen is the burner flow, so those two
tables are marked `burner` and kept out of the Moon Base counts.

Counts on Nov 14, 2026: 887 rows with the oxygen of the surrounding gas, 746 of them
with pressure too, 20 at 30 % oxygen or more and 10.2 psi or less (all CFI-G normal
flames), 17 more between 10.2 and 10.5 psi (all FLEX).

## FLEX table

Cleaning rules: the empty last row is dropped; blank cells stay blank; cells the
source shows as an unreadable character become blank and are flagged; pressure 0
(test 114) becomes blank and is flagged. No row is removed and no value is guessed.
