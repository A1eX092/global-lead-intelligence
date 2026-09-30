# Design decisions

What this project deliberately does, and deliberately does not do. Written down so that anyone auditing it — or reusing it — can see where the boundaries are, rather than inferring them from silence.

## Taken (schema version 0.2, 30 September 2026)

| Decision | Why |
|---|---|
| `sampling_strategy` on every row | 41% of measurements come from poisoning investigations. Without this column, comparing two countries is meaningless. |
| `result_status` separates `missing` from `non_detected` | 888 rows were previously counted as non-detects while they were simply missing. |
| `measurement_operator` and `detection_limit` | "< 5 ppm" is not a measurement of 5 ppm. The operator makes the censoring explicit rather than implied. |
| `original_value` and `original_unit` | Nothing published by a source is lost to our conversions. |
| `origin_status` and `origin_confidence` | A declared origin ("Made in India"), an inferred region ("East Java") and an assumed local product are three different claims. Filter on `origin_confidence >= 0.8` for solid origins only. |
| `data/raw/manifest.json` | Every download records its URL, timestamp, size and SHA-256. Sources change under your feet — NYC updates continuously — so a published number is only reproducible if the snapshot is identified. |
| `match_type` and `completeness` on recalls | RASFF can only be matched on the subject line, so its 270 alerts are a floor. FDA and CPSC matches are confirmed. The dataset says so itself. |
| The dashboard refuses a single combined detection rate | With no sampling strategy selected, it shows rates per strategy instead. A combined figure would look scientific and mean nothing. |
| `schema_version` on every row | So that a citation can name exactly what it used. |

## Deliberately deferred

These were considered and set aside. They are not oversights.

| Not done | Why not, for now |
|---|---|
| Entity resolution (`product_id`, `brand_id`) | Merging "Turmeric Powder 100g" with "Brand X Turmeric" on name similarity creates false certainty. It needs a curated ground truth this project does not have. |
| Multilingual product ontology (turmeric / haldi / curcuma) | Real value, real cost. Worth doing once someone actually queries the dataset in several languages. |
| Knowledge graph and natural-language querying | An interface layer on top of a dataset that is still thin. The evidence has to be worth traversing first. |
| Risk scoring | A risk score computed from contamination alone would be exactly the false precision this project tries to avoid. Evidence quality first, scoring later, if ever. |
| Environmental layers (water, soil, dust), blood lead, supply chain | Each is a project in itself, and most already have institutional owners (WHO, IHME, Pure Earth TSIP, World Bank). This project's contribution is the layer nobody assembles: product contamination. |
| Field-level data lineage | The row carries its source, its raw origin value and the schema version. Full per-field lineage is warranted when several contributors transform the same row. |
| Parquet files or a query API | 15,159 rows fit comfortably in a single page. Revisit past ~100,000 rows. |
| Category hierarchy (food → spices → turmeric) | The flat list of 17 categories still holds. Revisit when `other` grows past a few percent. |

## Standing rules

- No public "worst brand" ranking from a single test.
- Methodological warnings stay visible on the public dashboard, not buried in documentation.
- A source enters the ecosystem catalogue only after direct verification, with the date recorded.
- "Contamination", never "exposure", unless human exposure is genuinely being measured.
