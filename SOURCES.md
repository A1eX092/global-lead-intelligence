# Sources et licences

Une ligne = une source. Colonne `source` du schéma harmonisé (voir `README.md`).

| Source | Licence | Attribution à afficher | Modifications faites |
|---|---|---|---|
| Pure Earth, Rapid Market Screening ([Zenodo 10444602](https://zenodo.org/records/10444602)) | CC-BY 4.0 | « Pure Earth, Rapid Market Screening dataset, Zenodo, 2024 » | Catégories harmonisées, pays normalisés (ISO), seuil de référence recalculé et comparé à l'original |
| NYC Health Department, Metal Content of Consumer Products ([da9u-wz3r](https://data.cityofnewyork.us/resource/da9u-wz3r.json)) | Open data NYC — voir conditions générales nyc.gov/main/terms-of-use (à confirmer, aucune licence explicite publiée) | « NYC Department of Health and Mental Hygiene, Metal Content of Consumer Products » | Catégories harmonisées, pays d'origine extrait/normalisé (parfois déduit, marqué `origin_inferred`), non-détectés recodés |
| Public Health Seattle & King County ([i6sy-ckp7](https://data.kingcounty.gov/resource/i6sy-ckp7.json)) | Domaine public | « Public Health – Seattle & King County, Lead Content of Consumer Products » | Idem |
| Études IPEN sur la peinture, compilation Our World in Data | CC-BY (compilation OWID) — données sous-jacentes appartenant à IPEN | « IPEN lead paint studies, via Our World in Data » (citer IPEN explicitement, pas seulement OWID) | Aucune, reprises telles quelles |
| Suivi OMS/PNUE des lois sur la peinture au plomb, via Our World in Data | CC-BY (compilation OWID) | « WHO/UNEP Global Lead Paint Law Tracker, via Our World in Data » | Aucune |
| FDA, rappels alimentaires (openFDA) | Domaine public (œuvre du gouvernement américain) | « U.S. Food and Drug Administration, openFDA » | Filtré sur mention « lead » |
| CPSC, rappels de produits (SaferProducts.gov) | Domaine public (œuvre du gouvernement américain) | « U.S. Consumer Product Safety Commission » | Filtré sur mention « lead » |
| RASFF, alertes alimentaires UE | CC-BY 4.0 (décision 2011/833/UE) | « European Commission, RASFF Window » | Filtré sur mention plomb, 5 langues |

## Point non tranché
NYC Open Data ne publie pas de licence explicite sur cette page. Vérifier nyc.gov/main/terms-of-use avant publication GitHub ; si ambigu, contacter data.cityofnewyork.us ou citer prudemment sans revendiquer de droit de réutilisation au-delà de l'attribution.

## Règle générale
- Garder la colonne `source` sur chaque ligne du jeu de données harmonisé : c'est ce qui rend l'attribution vérifiable.
- Ne jamais publier de classement « pire marque » à partir d'un test unique.
- Garder les avertissements méthodologiques (biais d'échantillonnage, précision XRF vs laboratoire) visibles sur le tableau de bord public.
