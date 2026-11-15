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

Cleaning rules: the empty last row is dropped; blank cells stay blank; cells the
source shows as an unreadable character become blank and are flagged; pressure 0
(test 114) becomes blank and is flagged. No row is removed and no value is guessed.
