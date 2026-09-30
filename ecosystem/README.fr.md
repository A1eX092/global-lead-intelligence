# Cartographie de l'écosystème mondial des données sur le plomb

*Version 0, 30 septembre 2026. Inventaire en cours : 16 sources vérifiées une par une, avec la date de vérification. `sources.csv` est la version exploitable par machine.*

L'objectif n'est pas de collecter davantage de données, mais de répondre à une question que personne ne documente publiquement : **qui publie quoi sur le plomb, sous quelle licence, à quelle granularité — et surtout, où sont les trous.**

## Ce que la vérification a déjà montré

**1. La plombémie mondiale n'est pas publiée.** L'OMS expose dans son API des indicateurs dédiés (`LEAD_1` à `LEAD_10` : pourcentage d'enfants au-dessus de 5 µg/dL, décès et années de vie en bonne santé perdues). Ils contiennent **8 lignes au total, toutes datées de 2004**. Les chiffres que tout le monde cite — 1 enfant sur 3, 1,5 million de décès — viennent d'estimations modélisées (IHME, revues de littérature), pas d'un suivi ouvert pays par pays. C'est le trou le plus large de l'écosystème.

**2. Ce qui est bien alimenté, ce sont les lois, pas les mesures.** Le même GHO expose `LEADCONTROL` : 195 pays, de 1977 à 2024. On sait mieux quel pays a voté une loi que quel pays a du plomb dans le sang de ses enfants.

*Intégré le 30/09/2026.* Cette source remplace désormais la reprise d'Our World in Data pour les lois : 197 pays contre 164, et surtout **l'année d'entrée en vigueur** (États-Unis 1977, Cuba 1984, Costa Rica 1995 ; médiane mondiale 2008). Les deux sources ne divergent que sur **1 pays sur 163**, ce qui confirme la fiabilité des deux. Bilan : **94 pays dotés d'une loi, 70 sans, 33 sans donnée.**

**3. Les mesures existent surtout là où elles servent à poursuivre.** Rappels et alertes (FDA, CPSC, RASFF) sont continus, structurés, dotés d'API. Les campagnes de mesure, elles, sont ponctuelles : Pure Earth a publié une campagne 2021-2023, et rien n'indique qu'elle sera renouvelée.

**4. Les données les plus utiles sont enfermées dans des PDF.** IPEN a testé plus de 5 000 peintures dans une soixantaine de pays depuis 2007 : tout est en PDF, un par pays. Sans la compilation d'Our World in Data, ces données seraient inexploitables.

**5. Deux portes sont fermées.** Safety Gate, le système d'alerte européen pour les produits non alimentaires — jouets, bijoux, cosmétiques — refuse l'accès à son API hors de son interface. Les rappels canadiens sont publiés sans nom de produit.

## Les couches et leur état

| Couche | État | Commentaire |
|---|---|---|
| Produits de consommation | partiel | 15 159 mesures, mais 3 sources seulement, dont 2 américaines |
| Rappels et alertes | bon | 3 API continues, 904 événements |
| Réglementation | bon pour la peinture, inexistant ailleurs | Rien sur les épices, la vaisselle, les cosmétiques |
| Peintures | correct mais captif | PDF IPEN, dépendance à la compilation OWID |
| Sites pollués | à évaluer | Pure Earth TSIP, ~1 500 sites au plomb |
| Plombémie | **trou majeur** | Rien de global et d'ouvert ; États-Unis seulement, et partiellement restreint |
| Eau, sols, poussières | non exploré | |
| Exposition professionnelle | non exploré | Recyclage des batteries, ateliers de fonderie |
| Interventions et résultats | inexistant | Personne ne documente ce qui a marché après une détection |

## Méthode

Une source n'entre dans `sources.csv` qu'après vérification directe : appel de l'API, lecture de la licence, comptage des lignes. La colonne `verifie_le` porte la date. Les sources non vérifiées sont marquées « à évaluer » ou « à vérifier », jamais présentées comme acquises.

## Prochaines vérifications

- IHME / Global Burden of Disease : accès aux estimations de plombémie par pays
- Eau potable : bases américaines (SDWIS, ECHO) et rapports européens
- Exposition professionnelle : ABLES aux États-Unis, données de l'OIT
- Humanitarian Data Exchange (HDX) et portails nationaux
- ICSMS, la base européenne de surveillance du marché — contournement possible de Safety Gate
