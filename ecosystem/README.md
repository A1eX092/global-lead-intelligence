# Mapping the global lead data ecosystem

*Version 0, 30 September 2026. Inventory in progress: 16 sources verified one by one, each with the date it was checked. `sources.csv` is the machine-readable version. (Version française : [README.fr.md](README.fr.md).)*

The goal is not to collect more data. It is to answer a question nobody documents publicly: **who publishes what on lead, under which licence, at which granularity — and above all, where the holes are.**

## What verification has already shown

**1. Global blood lead data is not published.** WHO exposes dedicated indicators in its API (`LEAD_1` to `LEAD_10`: share of children above 5 µg/dL, attributable deaths, DALYs). They contain **8 rows in total, all dated 2004**. The figures everyone cites — one child in three, 1.5 million deaths — come from modelled estimates (IHME, literature reviews), not from an open country-by-country record. This is the widest hole in the ecosystem.

**2. What is well maintained is the law, not the measurement.** The same GHO exposes `LEADCONTROL`: 195 countries, 1977 to 2024. **We know better which country passed a law than which country has lead in its children's blood.**

*Integrated 2026-09-30.* This source now replaces the Our World in Data version for laws: 197 countries against 164, and above all **the year the law came into force** (United States 1977, Cuba 1984, Costa Rica 1995; global median 2008). The two sources disagree on **1 country out of 163**, which is reassuring about both. Totals: **94 countries with a law, 70 without, 33 with no data.**

**3. Continuous measurement exists mainly where it supports enforcement.** Recalls and alerts (FDA, CPSC, RASFF) are continuous, structured and served by APIs. Measurement campaigns are one-off: Pure Earth published a 2021-2023 campaign, with no indication it will be repeated.

**4. The most useful data sits locked in PDFs.** IPEN has tested more than 5,000 paints across some 60 countries since 2007 — all published as country PDFs. Without the Our World in Data compilation, that evidence would be unusable at scale.

**5. Two doors are closed.** Safety Gate, the EU alert system for non-food products (toys, jewellery, cosmetics), refuses API access from outside its own interface. Canadian recalls are published without product names.

## Layers and their state

| Layer | State | Comment |
|---|---|---|
| Consumer products | partial | 15,159 measurements, but only 3 sources, 2 of them American |
| Recalls and alerts | good | 3 continuous APIs, 904 events |
| Regulation | good for paint, absent elsewhere | Nothing on spices, tableware, cosmetics |
| Paint | usable but captive | IPEN PDFs, dependence on the OWID compilation |
| Contaminated sites | to assess | Pure Earth TSIP, ~1,500 lead sites |
| Blood lead | **major hole** | Nothing global and open; United States only, and partly restricted |
| Water, soil, dust | not explored | |
| Occupational exposure | not explored | Battery recycling, informal smelting |
| Interventions and outcomes | non-existent | Nobody documents what worked after a detection |

## Method

A source enters `sources.csv` only after direct verification: calling the API, reading the licence, counting the rows. The `verifie_le` column carries that date. Unverified sources are marked "to assess" or "to verify" — never presented as established.

## Next checks

- IHME / Global Burden of Disease: access to modelled blood lead estimates by country
- Drinking water: US databases (SDWIS, ECHO) and European reporting
- Occupational exposure: ABLES in the United States, ILO data
- Humanitarian Data Exchange (HDX) and national portals
- ICSMS, the EU market surveillance database — a possible way around Safety Gate
