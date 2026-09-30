# Sources et licences — Global Lead Intelligence

*Open evidence on lead contamination in consumer products*

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

## New York : vérifié le 29/09/2026

Aucune ambiguïté : la **Local Law 11 de 2012** impose que les jeux de données publiés par la ville soient disponibles « sans obligation d'enregistrement, sans licence et sans restriction d'usage », ce que confirme la FAQ du portail NYC Open Data (« no restrictions on the use of Open Data »). Les conditions générales de nyc.gov ne concernent que le site lui-même, pas les données — d'où l'absence de licence affichée sur la page du jeu de données.

Réutilisation et redistribution sont donc libres, et **l'attribution n'est pas juridiquement exigée** : celle que porte ce dépôt est volontaire.

## Mention exigée par New York

Le DOHMH autorise les jeux de données dérivés « so long as it is done in a manner that is not misleading and does not imply endorsement of such datasets by DOHMH ». Toute publication doit donc préciser que **ce travail n'est ni validé ni approuvé par le DOHMH**.

## Règle générale
- Garder la colonne `source` sur chaque ligne du jeu de données harmonisé : c'est ce qui rend l'attribution vérifiable.
- Ne jamais publier de classement « pire marque » à partir d'un test unique.
- Garder les avertissements méthodologiques (biais d'échantillonnage, précision XRF vs laboratoire) visibles sur le tableau de bord public.
