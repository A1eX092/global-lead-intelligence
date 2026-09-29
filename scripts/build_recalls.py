"""Construit data/recalls.csv : produits rappelés pour cause de plomb.

Granularité différente des mesures : une ligne = un rappel officiel, avec le nom
commercial du produit et l'entreprise, mais sans concentration mesurée.

Sources :
  - FDA (États-Unis), rappels alimentaires, via l'API openFDA (domaine public)
  - CPSC (États-Unis), rappels de produits de consommation (domaine public)
  - RASFF (Union européenne), alertes alimentaires, via l'API publique de RASFF Window

C'est la seule famille de sources publiques qui nomme les produits (et, pour la
FDA et la CPSC, les entreprises). Une grande partie des produits rappelés est
fabriquée dans les pays touchés.
"""
from pathlib import Path
import json
import re

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "recalls"
RASFF_RAW = ROOT / "data" / "raw" / "rasff"
OUT = ROOT / "data" / "recalls.csv"

# « lead » comme mot isolé : évite « leading », « leaded glass » reste pertinent
LEAD = re.compile(r"\blead(ed)?\b", re.I)

CPSC_CATEGORY = [
    (r"toy|doll|puzzle|children|infant|crib|stroller|rattle", "toys_children"),
    (r"jewel|necklace|bracelet|earring|pendant|charm", "jewelry"),
    (r"cookware|pot\b|pan\b|kettle|mug|cup|tumbler|dish|bowl|plate|utensil|pitcher|straw", "tableware"),
    (r"paint|coating", "paint"),
    (r"cosmetic|lipstick|kohl|kajal|makeup", "cosmetics"),
    (r"candy|sweet|chocolate", "sweets"),
    (r"spice|seasoning|turmeric|chili|cinnamon", "spices"),
    (r"supplement|remedy|medicine|ayurvedic", "medicines"),
]
FDA_CATEGORY = [
    (r"turmeric|spice|masala|chili|cinnamon|paprika|curry|seasoning|pepper", "spices"),
    (r"candy|chocolate|sweet|lollipop|tamarind", "sweets"),
    (r"supplement|capsule|ayurvedic|herbal|remedy", "medicines"),
    (r"applesauce|apple sauce|puree|cinnamon apple|baby food|infant", "food_other"),
]


def categorize(text, rules):
    text = (text or "").lower()
    for pattern, category in rules:
        if re.search(pattern, text):
            return category
    return "other"


def load_fda():
    payload = json.loads((RAW / "fda.json").read_text())
    rows = []
    for r in payload["results"]:
        reason = r.get("reason_for_recall", "")
        if not LEAD.search(reason):
            continue
        description = r.get("product_description", "")
        rows.append({
            "source": "fda_food",
            "recall_id": r.get("recall_number"),
            "date": r.get("recall_initiation_date"),
            "product": description[:200],
            "firm": r.get("recalling_firm"),
            "origin_country": None,  # la FDA donne le pays de l'entreprise qui rappelle, pas l'origine
            "firm_country": r.get("country"),
            "category": categorize(description, FDA_CATEGORY),
            "reason": reason[:300],
            "severity": r.get("classification"),
            "url": None,
        })
    return pd.DataFrame(rows)


def load_cpsc():
    payload = json.loads((RAW / "cpsc.json").read_text())
    rows = []
    for r in payload:
        title = r.get("Title", "")
        hazards = " ".join(h.get("Name", "") for h in r.get("Hazards", []))
        if not (LEAD.search(title) or LEAD.search(hazards)):
            continue
        products = r.get("Products") or [{}]
        countries = [c.get("Country") for c in r.get("ManufacturerCountries", []) if c.get("Country")]
        firms = [m.get("Name", "") for m in r.get("Manufacturers", [])]
        product_text = " ".join(filter(None, [products[0].get("Name"), products[0].get("Type"), title]))
        rows.append({
            "source": "cpsc",
            "recall_id": r.get("RecallNumber") or r.get("RecallID"),
            "date": (r.get("RecallDate") or "")[:10].replace("-", ""),
            "product": (products[0].get("Name") or title)[:200],
            "firm": (firms[0] if firms else None),
            "origin_country": countries[0] if countries else None,
            "firm_country": None,
            "category": categorize(product_text, CPSC_CATEGORY),
            "reason": (hazards or title)[:300],
            "severity": None,
            "url": r.get("URL"),
        })
    return pd.DataFrame(rows)


RASFF_CATEGORY = [
    (r"feed|petfood|pet food|barf|fodder|hay\b|forage", "animal_feed"),
    (r"game|venison|deer|boar|pheasant|partridge|hunter|wild bird|carne de caza", "game_meat"),
    (r"spice|turmeric|chili|paprika|cumin|curry|masala|seasoning|pepper|garlic|ginger|herb|lovage|czosn", "spices"),
    (r"potato|rice|flour|cereal|starch|maize|wheat", "staple_food"),
    (r"candy|confection|chocolate|liquorice|\bsweets\b", "sweets"),
    (r"supplement|herbal|ayurvedic|medicine|remedy", "medicines"),
    (r"ceramic|pottery|glaze|porcelain|earthenware", "ceramic_tableware"),
    (r"cookware|pot\b|pan\b|kettle|utensil|jug|mug|cup|glass|dish|tableware|kitchenware", "tableware"),
    (r"cosmetic|kohl|kajal|lipstick", "cosmetics"),
    (r"toy|children", "toys_children"),
    (r"paint|pigment|colorant", "paint"),
    (r"rice|flour|cereal|starch|potato", "staple_food"),
    (r"strainer|coffee machine|kettle|bottle|packaging|pizza box|container|migration", "tableware"),
    (r"olive|avocado|tea\b|cocoa|coffee|honey|oil\b|fish|seafood|mushroom|fruit|vegetable|meat|sausage|psyllium|husk|supplement|burger|seed", "food_other"),
]


def load_rasff():
    path = RASFF_RAW / "rasff.json"
    if not path.exists():
        return pd.DataFrame()
    payload = json.loads(path.read_text())
    rows = []
    for n in payload["notifications"]:
        subject = n.get("subject") or ""
        origins = [c.get("organizationName") for c in (n.get("originCountries") or []) if c.get("organizationName")]
        category_text = " ".join(filter(None, [subject, (n.get("productCategory") or {}).get("description")]))
        date = (n.get("ecValidationDate") or "")[:10]  # format JJ-MM-AAAA
        day, month, year = (date.split("-") + ["", "", ""])[:3]
        rows.append({
            "source": "rasff",
            "recall_id": n.get("reference"),
            "date": f"{year}{month}{day}" if year else None,
            "product": subject[:200],
            "firm": None,  # RASFF public ne nomme pas l'entreprise
            "origin_country": origins[0] if origins else None,
            "firm_country": (n.get("notifyingCountry") or {}).get("organizationName"),
            "category": categorize(category_text, RASFF_CATEGORY),
            "reason": ((n.get("notificationClassification") or {}).get("description", "") + " — "
                       + (n.get("riskDecision") or {}).get("description", ""))[:300],
            "severity": (n.get("riskDecision") or {}).get("description"),
            "url": f"https://webgate.ec.europa.eu/rasff-window/screen/notification/{n.get('notifId')}",
        })
    return pd.DataFrame(rows)


def main():
    from harmonize import to_country  # même normalisation des pays que pour les mesures

    df = pd.concat([load_fda(), load_cpsc(), load_rasff()], ignore_index=True)
    df["origin_country"] = df["origin_country"].map(to_country)
    df["firm_country"] = df["firm_country"].map(to_country)
    df["year"] = pd.to_numeric(df["date"].str[:4], errors="coerce").astype("Int64")
    df = df.sort_values("date", ascending=False)
    df.to_csv(OUT, index=False)

    print(f"{len(df)} rappels → {OUT.relative_to(ROOT)}")
    print(df.groupby("source").size().to_string())
    print(f"Période : {df['year'].min()}-{df['year'].max()}")
    print("Pays d'origine :")
    print(df["origin_country"].value_counts().head(8).to_string())
    print("Catégories :")
    print(df["category"].value_counts().to_string())


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
