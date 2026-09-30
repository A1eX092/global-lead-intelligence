# Global Lead Intelligence

*Open evidence on lead contamination in consumer products*

> **Contamination, not exposure.** This project documents the **lead content of products**. It does not measure human exposure, which depends on how much is consumed, how often, by which route, and on bioavailability. No individual health conclusion can be drawn from it.

Six public sources, harmonised into one schema, with a local dashboard to explore them. Exploratory prototype, started 19 September 2026. *(Version française : [README.fr.md](README.fr.md).)*

## Run it

```bash
python3 -m venv .venv && .venv/bin/pip install pandas openpyxl pycountry certifi
.venv/bin/python scripts/fetch.py            # raw sources → data/raw/
.venv/bin/python scripts/fetch_rasff.py      # EU alerts (slow: scans 32,000+ notifications)
.venv/bin/python scripts/harmonize.py        # → data/harmonized.csv
.venv/bin/python scripts/build_countries.py  # → data/countries.csv
.venv/bin/python scripts/build_recalls.py    # → data/recalls.csv
.venv/bin/python scripts/build_dashboard.py  # → dashboard/index.html
python3 -m http.server 8765 --directory dashboard
```

## What's in it

### Measurements (`data/harmonized.csv` — one row per lead measurement)

| Source | Rows | Method | Licence |
|---|---|---|---|
| Pure Earth, Rapid Market Screening — 25 low- and middle-income countries, 2021-2023 ([Zenodo 10444602](https://zenodo.org/records/10444602)) | 5,153 | Field XRF | CC-BY 4.0 |
| NYC Health Department, Metal Content of Consumer Products ([da9u-wz3r](https://data.cityofnewyork.us/resource/da9u-wz3r.json)), 2011-2025 | 7,795 | Mostly laboratory, some XRF | Free reuse (NYC Local Law 11 of 2012) |
| Public Health Seattle & King County ([i6sy-ckp7](https://data.kingcounty.gov/resource/i6sy-ckp7.json)) | 2,211 | XRF and laboratory | Public domain |
| **Total** | **15,159** | | |

### Country context (`data/countries.csv` — one row per country)

| Source | Content | Coverage |
|---|---|---|
| WHO Global Health Observatory, `LEADCONTROL` | Binding lead paint law, **with the year it came into force** | 195 countries, 1977-2024 — 94 with a law, 70 without, 33 with no data |
| IPEN paint studies, compiled by [Our World in Data](https://ourworldindata.org/lead-paint) | Share of decorative paints above 90, 600 and 10,000 ppm | 59 countries |

IPEN publishes only country PDFs; the Our World in Data compilation (100+ studies, 4,000+ paints) avoids extracting them one by one. WHO's own indicator is used as the reference for laws — it covers more countries and carries the year — with the OWID version kept alongside as a cross-check. The two disagree on **1 country out of 163**.

### Recalls and alerts (`data/recalls.csv` — one row per recall or alert)

| Source | Content | Rows |
|---|---|---|
| FDA food enforcement (openFDA) | Food recalled for lead | 253 |
| CPSC recalls | Toys, jewellery, paint — with country of manufacture | 381 |
| RASFF (EU) | Notifications mentioning lead, with country of origin | 270 |
| **Total** | 1976-2026 | **904** |

These name the products (and the company, for FDA and CPSC) but carry no measured concentration. Countries of origin: China 345, India 35, Italy 24, Germany 22, UK 21. RASFF surfaces two families the US sources miss entirely: **animal feed** (33) and **game meat** (21), contaminated by lead ammunition.

## Read `sampling_strategy` before comparing anything

This is the most important column in the dataset. **41% of measurements (6,185) come from investigations opened after a child was poisoned**: products already under suspicion. Comparing them with systematic market purchases (5,153 Pure Earth rows) is like comparing an emergency room with a population screening.

| Strategy | Rows | What it implies |
|---|---|---|
| `case_investigation` | 6,185 | Seized after a poisoning — strongly biased upward |
| `market_screening` | 5,153 | Systematic market purchases — closest to a representative sample |
| `community_event` | 1,344 | Items brought in by residents — self-selected |
| `store_survey` | 1,188 | Collected in shops |
| `unknown` | 798 | Not documented by the source |
| `research` | 491 | Research protocol |

A detection rate computed across all strategies at once **means nothing**. The dashboard exposes this filter prominently.

## Three statuses never to conflate

- **`result_status`**: `detected`, `non_detected`, `missing`. A missing value is not a zero — 888 rows are in this state, and they were previously counted as non-detects.
- **Censored values**: a "< 5 ppm" result keeps 5 in `lead_value` (that is the detection limit) and leaves `lead_ppm` empty. It is never a zero.
- **`origin_status`** and **`origin_confidence`**: `declared` (1.0, "Made in India"), `inferred_region` (0.8, "East Java" → Indonesia), `assumed_local` (0.35, unidentified place in the country of purchase), `unknown`. Filter on `origin_confidence >= 0.8` to keep only solid origins.

## Schema

One row per measurement: `schema_version`, `source`, `source_id`, `category`, `category_raw`, `product_name`, `brand`, `manufacturer`, `origin_country`, `origin_status`, `origin_confidence`, `origin_raw`, `sampled_country`, `sampled_region`, `year`, `method`, `unit`, `lead_value`, `measurement_operator`, `detection_limit`, `original_value`, `original_unit`, `lead_ppm`, `non_detect`, `result_status`, `sampling_strategy`, `sampling_raw`, `reference_ppm`, `reference_basis`. Full definitions at the top of [`scripts/harmonize.py`](scripts/harmonize.py).

## Design decisions (all reversible)

- **Categories**: 15 shared categories; the mappings live in `harmonize.py`. "Tableware (material unknown)" covers NYC and King County rows where ceramic and metal are not distinguished.
- **Units**: ppb converted to ppm. mg/cm² (paint and surfaces tested by XRF) and mg/L are kept as they are and excluded from ppm comparisons.
- **Reference thresholds**: taken from the Pure Earth study, per category, recorded in `reference_basis`. They are **indicative, not legal**: they carry no jurisdiction, no date, no target population. A proper regulatory layer remains to be built. Cross-check: 917 Pure Earth rows above threshold by our computation, against 913 in their own file.
- **Countries**: normalised to ISO names with pycountry, plus aliases and a country-name search inside free text. Regions are resolved through ISO subdivisions ("East Java" → Indonesia, "Morelos" → Mexico); an ambiguous region such as Punjab is only resolved when it belongs to the country of purchase. **70%** of rows carry a country (65% declared, 6% inferred).

## Known limits

- **Sampling bias**: NYC and King County mostly test suspect products or items linked to poisoned children. Pure Earth buys more systematically on markets.
- **Method precision**: field XRF (detection limit of a few ppm) is not laboratory analysis.
- **No per-sample date** in the Pure Earth data — only the 2021-2023 window.
- **RASFF is filtered on notification subject only**, in five languages. An alert where lead appears solely in another field is missed. The 270 figure is a floor, not a total.
- **This derivative dataset is neither validated nor endorsed by NYC DOHMH**, which permits derivative work provided it is not misleading and implies no endorsement.

## Who it is for

**Regulators and NGOs in affected countries first**: the question the dashboard answers is "which product categories and which countries should be screened first". The data stays open and citable for researchers. No public "worst brands" ranking — a single test cannot condemn a product.

## Mapping the ecosystem

[`ecosystem/`](ecosystem/) catalogues who publishes what on lead worldwide, under which licence, at which granularity — and where the holes are. First finding: WHO's own blood lead indicators (`LEAD_1` to `LEAD_10`) contain **8 rows, all from 2004**. We know better which country passed a law than which country has lead in its children's blood.

## Design decisions

What the project does, what it deliberately does not do, and why: [DECISIONS.md](DECISIONS.md). Schema version 0.2.

## Licences

Code under MIT, data under CC-BY 4.0. Per-source attribution and terms: [SOURCES.md](SOURCES.md).
