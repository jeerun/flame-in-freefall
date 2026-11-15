# Raw data

`psi69_flex_experimental_table.tsv`: the Experimental Table of NASA PSI-69,
Flame Extinguishment Experiment (FLEX), version 5.
https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
DOI 10.60555/mbq8-0451. Licence listed on the page: CC0-1.0.

Read on Nov 14, 2026 from the table shown on that page (three pages of 100 rows),
saved as tab-separated text, and checked page by page with SHA-256 against hashes
computed in the browser. It is not the downloadable CSV file. Column names are as
the page shows them, so the gas columns read "O", "N", "CO" (for O2, N2, CO2) and
the burning rate unit reads "mm" (it is mm^2/s).

`psi_search/combustion_investigations.json`: the answer of the PSI repository's own
search service for "combustion", limited to PSI investigations. It is what the page
https://psi.nasa.gov/physci/repo/search?q=combustion loads:
`https://psi.nasa.gov/geode-py/ws/repo/search?term=combustion&source=psi&type=investigation&sort=Public%20Release%20Date&order=desc&size=100`
Downloaded Nov 14, 2026. 26 records, each with the title, project type, flight
platform, hardware, keywords, objectives and approach text shown on the
investigation's PSI page. 195,005 bytes as downloaded, SHA-256
`692423C2F1FC3EFE2C405B0614D275220FA4285C54BE2597CDC9B370241113DD`.
PSI asks users to cite investigations by their DOI, shown under "Cite this
Investigation" on each PSI page.

Do not edit files in this folder.
