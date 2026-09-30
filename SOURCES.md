# Sources and licences — Global Lead Intelligence

*Open evidence on lead contamination in consumer products*

One row per source. Matches the `source` column of the harmonised schema (see [README.md](README.md)). *(Version française : [SOURCES.fr.md](SOURCES.fr.md).)*

| Source | Licence | Attribution to display | Changes made |
|---|---|---|---|
| Pure Earth, Rapid Market Screening ([Zenodo 10444602](https://zenodo.org/records/10444602)) | CC-BY 4.0 | "Pure Earth, Rapid Market Screening dataset, Zenodo, 2024" | Categories harmonised, countries normalised to ISO, threshold flag recomputed and cross-checked against the original |
| NYC Health Department, Metal Content of Consumer Products ([da9u-wz3r](https://data.cityofnewyork.us/resource/da9u-wz3r.json)) | Free reuse under NYC Local Law 11 of 2012 (verified 2026-09-29) | "NYC Department of Health and Mental Hygiene, Metal Content of Consumer Products" | Categories harmonised, origin country parsed and normalised (sometimes inferred — see `origin_status`), non-detects recoded |
| Public Health Seattle & King County ([i6sy-ckp7](https://data.kingcounty.gov/resource/i6sy-ckp7.json)) | Public domain | "Public Health – Seattle & King County, Lead Content of Consumer Products" | Same |
| IPEN lead paint studies, compiled by Our World in Data | CC-BY for the OWID compilation; underlying data belongs to IPEN | "IPEN lead paint studies, via Our World in Data" — **cite IPEN explicitly, not only OWID** | None, used as published |
| WHO Global Health Observatory, indicator `LEADCONTROL` | WHO open data | "World Health Organization, Global Health Observatory (LEADCONTROL)" | Yes/No mapped to boolean; year of entry into force kept |
| WHO/UNEP lead paint law tracker, via Our World in Data | CC-BY for the OWID compilation | "WHO/UNEP Global Lead Paint Law Tracker, via Our World in Data" | Kept as a cross-check against the WHO indicator |
| FDA food enforcement (openFDA) | Public domain (US government work) | "U.S. Food and Drug Administration, openFDA" | Filtered on the word "lead" |
| CPSC recalls (SaferProducts.gov) | Public domain (US government work) | "U.S. Consumer Product Safety Commission" | Filtered on the word "lead" |
| RASFF, EU food alerts | CC-BY 4.0 (Commission Decision 2011/833/EU) | "European Commission, RASFF Window" | Filtered on lead in five languages |

## New York: verified 2026-09-29

No ambiguity. **Local Law 11 of 2012** requires datasets published by the City to be available "without registration requirement, license requirement, or usage restrictions", which the NYC Open Data FAQ confirms ("no restrictions on the use of Open Data"). The nyc.gov terms of use cover the website itself, not the data — which is why no licence appears on the dataset page.

Reuse and redistribution are therefore free, and **attribution is not legally required**: the attribution in this repository is voluntary.

## Statement required by New York

DOHMH permits derivative datasets "so long as it is done in a manner that is not misleading and does not imply endorsement of such datasets by DOHMH". Any publication must therefore state that **this work is neither validated nor endorsed by DOHMH**.

## Standing rules

- Keep the `source` column on every row of the harmonised dataset: it is what makes attribution verifiable.
- Never publish a "worst brand" ranking built on a single test.
- Keep the methodological warnings (sampling bias, XRF vs laboratory precision) visible on the public dashboard.
