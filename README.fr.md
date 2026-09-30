# Global Lead Intelligence

*Open evidence on lead contamination in consumer products*

**Explorer les données : https://a1ex092.github.io/global-lead-intelligence/**
**Citer : [10.5281/zenodo.23065083](https://doi.org/10.5281/zenodo.23065083)**

> **Contamination, pas exposition.** Ce projet documente la **teneur en plomb de produits**. Il ne mesure pas l'exposition des personnes, qui dépend de la quantité consommée, de la fréquence, de la voie d'absorption et de la biodisponibilité. Aucune conclusion sanitaire individuelle ne peut en être tirée.

Rassemble et harmonise des données publiques de tests de plomb dans les produits de consommation (épices, ustensiles, cosmétiques, jouets, peintures…), avec un tableau de bord local pour les explorer.

Prototype exploratoire (19/09/2026). Voir l'idée n°6 de `../projets futurs.md`.

Licences et attribution complètes de toutes les sources (dont RASFF, FDA, CPSC) : voir `SOURCES.md`.

## Lancer

```bash
cd global-lead-intelligence
python3 -m venv .venv && .venv/bin/pip install pandas openpyxl pycountry certifi
.venv/bin/python scripts/fetch.py            # télécharge les sources dans data/raw/
.venv/bin/python scripts/harmonize.py        # → data/harmonized.csv
.venv/bin/python scripts/build_countries.py   # → data/countries.csv (contexte par pays)
.venv/bin/python scripts/fetch_rasff.py       # alertes UE (long : parcourt 32 000+ notifications)
.venv/bin/python scripts/build_recalls.py     # → data/recalls.csv (rappels et alertes)
.venv/bin/python scripts/build_dashboard.py  # → dashboard/index.html
python3 -m http.server 8765 --directory dashboard   # puis http://localhost:8765
```

## Sources intégrées

| Source | Lignes (plomb) | Méthode | Licence |
|---|---|---|---|
| Pure Earth, Rapid Market Screening — 25 pays à faibles et moyens revenus, 2021-2023 ([Zenodo 10444602](https://zenodo.org/records/10444602)) | 5 153 | XRF sur le terrain | CC-BY 4.0 |
| NYC Health Department, Metal Content of Consumer Products ([da9u-wz3r](https://data.cityofnewyork.us/resource/da9u-wz3r.json)), 2011-2025 | 7 795 | Laboratoire (majorité), XRF | Open data de la ville, réutilisation libre (Local Law 11 de 2012) |
| Public Health Seattle & King County ([i6sy-ckp7](https://data.kingcounty.gov/resource/i6sy-ckp7.json)) | 2 211 | XRF, laboratoire | Domaine public |
| **Total mesures** | **15 159** | | |

### Contexte par pays (`data/countries.csv`, granularité différente : une ligne = un pays)

| Source | Contenu | Couverture |
|---|---|---|
| Études IPEN sur la peinture, compilées par [Our World in Data](https://ourworldindata.org/lead-paint) | Part des peintures décoratives dépassant 90, 600 et 10 000 ppm | 59 pays |
| Suivi OMS/PNUE des lois sur la peinture au plomb (via Our World in Data) | Loi contraignante oui/non (2023) | 164 pays, dont **71 sans loi** |

### Rappels et alertes officiels (`data/recalls.csv`, une ligne = un rappel ou une alerte)

| Source | Contenu | Volume |
|---|---|---|
| FDA, rappels alimentaires (openFDA) | Produits alimentaires rappelés pour cause de plomb | 253 |
| CPSC, rappels de produits de consommation | Jouets, bijoux, peintures… | 381 |
| RASFF, alertes alimentaires de l'UE | Notifications mentionnant le plomb, avec pays d'origine | 270 |
| **Total** | 1976-2026 | **904** |

Ces rappels **nomment les produits** (et l'entreprise pour la FDA et la CPSC) mais ne donnent pas de concentration. Pays d'origine : **Chine 345, Inde 35, Italie 24, Allemagne 22, Royaume-Uni 21**. Catégories dominantes : jouets et articles pour enfants (254), épices (110), peintures (82), vaisselle et contenants (60).

RASFF fait apparaître deux familles absentes des autres sources : les **aliments pour animaux** (33) et le **gibier** (21), contaminé par les munitions au plomb. L'API RASFF ne sait pas filtrer par danger : `fetch_rasff.py` parcourt les 32 597 notifications publiques et retient celles dont le sujet mentionne le plomb, en cinq langues.

IPEN ne publie que des PDF par pays : la compilation d'Our World in Data (plus de 100 études, plus de 4 000 peintures) évite d'avoir à les extraire un par un. Extraire les PDF reste possible plus tard pour retrouver le détail par marque.

## Schéma commun

Une ligne = une mesure. Colonnes : `source`, `source_id`, `category`, `category_raw`, `product_name`, `brand`, `manufacturer`, `origin_country`, `origin_inferred`, `origin_raw`, `sampled_country`, `sampled_region`, `year`, `method`, `unit`, `lead_value`, `lead_ppm`, `non_detect`, `reference_ppm`, `above_reference`. Le détail figure en tête de `scripts/harmonize.py`.

## Comparer deux chiffres : lire d'abord `sampling_strategy`

C'est la colonne la plus importante du jeu de données. **41 % des mesures (6 185) proviennent d'enquêtes menées après une intoxication** : ce sont des produits déjà suspects, sélectionnés parce qu'un enfant était malade. Les comparer à des achats systématiques sur un marché (5 153 mesures de Pure Earth) revient à comparer un service d'urgences à un dépistage de population.

| Stratégie | Mesures | Ce que ça implique |
|---|---|---|
| `case_investigation` | 6 185 | Produits saisis après une intoxication — fortement biaisé vers le haut |
| `market_screening` | 5 153 | Achats systématiques sur les marchés — la base la plus proche d'un échantillon représentatif |
| `community_event` | 1 344 | Objets apportés spontanément par des habitants — auto-sélection |
| `store_survey` | 1 188 | Relevé en magasin |
| `unknown` | 798 | Non documenté par la source |
| `research` | 491 | Protocole de recherche |

Un taux de dépassement calculé toutes stratégies confondues **n'a pas de sens**. Le tableau de bord expose ce filtre en évidence.

## Trois statuts à ne jamais confondre

- **`result_status`** : `detected`, `non_detected`, `missing`. Une valeur absente n'est pas un « zéro » : 888 mesures sont dans ce cas, et elles étaient auparavant comptées comme non détectées.
- **Valeurs censurées** : un résultat « < 5 ppm » conserve 5 dans `lead_value` (c'est la limite de détection) et laisse `lead_ppm` vide. Ce n'est jamais un zéro.
- **`origin_status`** et **`origin_confidence`** : `declared` (1.0, « Made in India »), `inferred_region` (0.8, « East Java » → Indonésie), `assumed_local` (0.35, lieu inconnu dans le pays d'achat), `unknown`. Filtrer sur `origin_confidence >= 0.8` pour ne garder que les origines solides.

## Choix techniques (réversibles)

- **Catégories** : 15 catégories communes. Les correspondances sont dans `harmonize.py`. « Vaisselle (matière inconnue) » regroupe la vaisselle de New York et de King County, où la matière (céramique ou métal) n'est pas précisée.
- **Non détecté** : `-1` chez New York, `<` ou `<LOD` chez King County, `0` chez Pure Earth.
- **Unités** : les ppb sont convertis en ppm. Les mg/cm² (peintures et surfaces testées au XRF) et les mg/l sont conservés tels quels, mais exclus des comparaisons en ppm.
- **Seuils de référence** : ceux de l'étude Pure Earth, par catégorie, repris dans la colonne `reference_basis`. Ils sont **indicatifs, pas légaux** : ils ne dépendent ni de la juridiction, ni de la date, ni de la population concernée. Une couche réglementaire par pays reste à construire. Contrôle : 917 mesures Pure Earth au-dessus du seuil selon nos calculs, contre 913 selon le fichier d'origine.
- **Pays d'origine** : normalisés en noms ISO grâce à pycountry, avec des alias et une recherche du nom de pays dans le texte. Les régions sont résolues via les subdivisions ISO (« East Java » → Indonésie, « Morelos » → Mexique) ; une région ambiguë (Punjab) n'est tranchée que si elle appartient au pays de prélèvement. Un lieu non identifié qui ne dit pas « importé » est rattaché au pays de prélèvement (produit local). Ces cas sont marqués `origin_inferred = True`. Résultat : **70 %** des lignes ont un pays (65 % déclaré, 6 % déduit).

## Limites à garder en tête

- **RASFF n'est filtré que sur le sujet de la notification**, en cinq langues. Une alerte où le plomb n'apparaît que dans un autre champ est manquée. Le chiffre de 270 est donc un plancher, pas un total.
- **Ce jeu de données dérivé n'est ni validé ni approuvé par le NYC DOHMH**, qui autorise les travaux dérivés à condition qu'ils ne soient pas trompeurs et n'impliquent aucune caution de sa part.

- **Biais d'échantillonnage** : New York et King County testent surtout des produits suspects ou liés à des enfants intoxiqués. Les taux sont donc biaisés vers le haut. Pure Earth fait des achats plus systématiques sur les marchés.
- **Précision des méthodes** : le XRF de terrain (limite de détection de quelques ppm) n'a pas la précision d'une analyse en laboratoire.
- **Pas de date par échantillon** chez Pure Earth (seulement la période 2021-2023).

## Public visé

**Autorités et ONG des pays touchés d'abord** : la question à laquelle le tableau de bord doit répondre est « quelles catégories et quels pays contrôler en priorité ». Les données restent ouvertes et citables pour les chercheurs. Pas de classement public « pire marque » : un seul test ne suffit pas à condamner un produit.

## Pistes suivantes

- RASFF, alertes de l'UE : accès à vérifier. Utile pour les produits qui circulent hors des États-Unis.
- PDF IPEN par pays : détail par marque, si le besoin se confirme.
