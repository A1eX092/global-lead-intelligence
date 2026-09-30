"""Harmonise the three measurement sources into one schema → data/harmonized.csv

Schema (one row = one lead measurement on one product):
  source              pure_earth_rms | nyc_doh | king_county
  source_id           identifier within the source (when available)
  category            harmonised category (see CATEGORIES)
  category_raw        the source's own category label
  product_name        product description
  brand               brand (when available)
  manufacturer        manufacturer (when available)
  origin_country      country of manufacture / origin (ISO English name), empty if unknown
  origin_status       declared | inferred_region | assumed_local | unknown
  origin_confidence   1.0 declared, 0.8 region identified, 0.35 assumed local, else empty
  origin_raw          the origin value before normalisation
  sampled_country     country where the product was bought or collected
  sampled_region      region / city of collection (when available)
  year                year of collection (when available)
  method              xrf | laboratory
  unit                ppm | mg/cm2 | mg/l
  lead_value          measured value in its own unit (for "< X" results, X is the detection limit)
  lead_ppm            value in ppm where the unit allows it (ppm, ppb)
  non_detect          True when below the detection limit
  result_status       detected | non_detected | missing — "missing" is NOT "non-detected"
  sampling_strategy   how the sample was obtained (see SAMPLING): decisive before any comparison
  sampling_raw        the source's own wording for that strategy, kept verbatim
  reference_ppm       INDICATIVE reference threshold for the category (from Pure Earth RMS)
  reference_basis     where the threshold comes from — never a legal limit, see REFERENCE_BASIS
  above_reference     True/False when comparable, empty otherwise
"""
from pathlib import Path
import re
import unicodedata

import pandas as pd
import pycountry

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "harmonized.csv"

# Indicative reference thresholds (ppm), taken from the Pure Earth RMS study ("Coding" sheet).
# These are not uniform legal limits: they only support a first triage.
REFERENCE_PPM = {
    "spices": 2,
    "ceramic_tableware": 100,
    "metal_cookware": 100,
    "plastic_foodware": 100,
    "tableware": 100,
    "medicines": 10,
    "cosmetics": 2,
    "sweets": 0.1,
    "toys_children": 100,
    "paint": 90,
    "staple_food": 0.2,
}

REFERENCE_BASIS = "Pure Earth RMS (indicative, not a legal limit)"

# Sampling strategy: without it, comparing two countries is meaningless.
# A health department testing the belongings of poisoned children will
# mechanically find more lead than a buyer sweeping through a market.
SAMPLING = {
    "market_screening": "systematic market purchases (Pure Earth)",
    "case_investigation": "products seized after a poisoning — strongly biased upward",
    "store_survey": "collected in shops",
    "community_event": "items brought in by residents — self-selected",
    "research": "research protocol",
    "unknown": "not documented by the source",
}

CATEGORIES = [
    "spices", "staple_food", "food_other", "sweets", "medicines", "cosmetics",
    "religious_powder", "ceramic_tableware", "metal_cookware", "plastic_foodware",
    "tableware", "toys_children", "jewelry", "paint", "animal_feed", "game_meat", "other",
]

# ---------- countries ----------
ALIASES = {
    "usa": "United States", "us": "United States", "u.s.a.": "United States", "u.s.": "United States",
    "united states of america": "United States", "america": "United States",
    "uk": "United Kingdom", "england": "United Kingdom", "great britain": "United Kingdom",
    "chine": "China", "prc": "China", "hong kong": "Hong Kong",
    "viet nam": "Viet Nam", "turkey": "Türkiye", "turkiye": "Türkiye",
    "russia": "Russian Federation", "korea": "Korea, Republic of", "south korea": "Korea, Republic of",
    "iran": "Iran, Islamic Republic of", "syria": "Syrian Arab Republic", "tanzania": "Tanzania, United Republic of",
    "bolivia": "Bolivia, Plurinational State of", "laos": "Lao People's Democratic Republic",
    "ivory coast": "Côte d'Ivoire", "cote d'ivoire": "Côte d'Ivoire", "taiwan": "Taiwan, Province of China",
    "dubai": "United Arab Emirates", "uae": "United Arab Emirates", "burma": "Myanmar",
    "czech republic": "Czechia", "holland": "Netherlands", "moldova": "Moldova, Republic of",
    "palestine": "Palestine, State of", "vietnam": "Viet Nam", "venezuela": "Venezuela, Bolivarian Republic of",
    "kyrgyzstan": "Kyrgyzstan", "egypte": "Egypt", "inde": "India", "maroc": "Morocco", "tunisie": "Tunisia",
    "allemagne": "Germany", "italie": "Italy", "espagne": "Spain", "turquie": "Türkiye",
}
# Short display names
DISPLAY = {
    "Tanzania, United Republic of": "Tanzania", "Viet Nam": "Vietnam", "Russian Federation": "Russia",
    "Korea, Republic of": "South Korea", "Taiwan, Province of China": "Taiwan", "Moldova, Republic of": "Moldova",
    "Lao People's Democratic Republic": "Laos", "Syrian Arab Republic": "Syria", "Palestine, State of": "Palestine",
}
_country_cache = {}


def to_country(value):
    """Normalise a free-text country name to its ISO 3166 English name. None if unrecognised."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    raw = str(value).strip()
    if not raw or raw.lower() in {"not available", "unknown or not stated", "unknown", "n/a", "na", "-", "local"}:
        return None
    if raw in _country_cache:
        return _country_cache[raw]
    result = None
    for part in re.split(r"[/,;()\-]", raw):
        key = part.strip().lower()
        if not key:
            continue
        name = ALIASES.get(key, key)
        try:
            c = pycountry.countries.lookup(name)
            result = DISPLAY.get(c.name, getattr(c, "common_name", None) or c.name)
            break
        except LookupError:
            continue
    if result is None:
        # Fallback: a country named inside the text ("Made in China", "India tamilnadu"...)
        text = raw.lower()
        for pattern, name in _country_patterns():
            if pattern.search(text):
                result = name
                break
    _country_cache[raw] = result
    return result


def strip_accents(text):
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


# Regions whose common name differs from the ISO name, or that are not ISO subdivisions
REGION_TO_COUNTRY = {
    "east java": "Indonesia", "west java": "Indonesia", "central java": "Indonesia", "java": "Indonesia",
    "north sumatra": "Indonesia", "south sumatra": "Indonesia", "west sumatra": "Indonesia",
    "south sulawesi": "Indonesia", "north sulawesi": "Indonesia", "bali": "Indonesia",
    "zanzibar": "Tanzania", "pemba": "Tanzania",
    "punjab": None,  # ambiguous: India and Pakistan
}

_subdiv_index = None


def _subdivisions():
    """Index of { normalised region name: country name }, ambiguous names dropped."""
    global _subdiv_index
    if _subdiv_index is None:
        index = {}
        for s in pycountry.subdivisions:
            key = strip_accents(s.name).lower()
            country = pycountry.countries.get(alpha_2=s.country_code)
            if not country or len(key) < 4:
                continue
            name = DISPLAY.get(country.name, getattr(country, "common_name", None) or country.name)
            if key in index and index[key] != name:
                index[key] = None  # same name in two countries: leave unassigned
            else:
                index.setdefault(key, name)
        for key, name in REGION_TO_COUNTRY.items():
            index[key] = name
        _subdiv_index = index
    return _subdiv_index


def to_region_country(value, sampled_country=None):
    """Infer the country from a region name ("East Java" → Indonesia).

    When a region name exists in several countries, it is only resolved if it
    belongs to the country where the product was collected.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = strip_accents(str(value)).lower().strip()
    if not text:
        return None
    index = _subdivisions()
    for part in re.split(r"[/,;()]", text):
        part = part.strip()
        if part in index and index[part]:
            return index[part]
    if sampled_country:
        code = pycountry.countries.lookup(sampled_country).alpha_2
        for s in pycountry.subdivisions.get(country_code=code) or []:
            if re.search(rf"\b{re.escape(strip_accents(s.name).lower())}\b", text):
                return sampled_country
    return None


NON_PLACES = re.compile(
    r"import|abroad|unknown|not provided|^nd$|^na$|^n/a$|^-$|not available|not stated|no label|foreign", re.I)


def resolve_regions(origin, origin_raw, sampled_country):
    """Fill in missing origins from region names.

    Returns (origin, status, confidence). Three cases, in order:
      1. the region is identifiable ("East Java" → Indonesia, "Morelos" → Mexico);
      2. the region belongs to the country of collection ("Erode" in India);
      3. the text is an unidentified place that does not say "imported": the
         country of collection is used (local product), flagged as inferred.
    """
    origin = origin.copy()
    status = pd.Series("unknown", index=origin.index, dtype="object")
    status[origin.notna()] = "declared"
    confidence = pd.Series(pd.NA, index=origin.index, dtype="Float64")
    confidence[origin.notna()] = 1.0
    missing = origin.isna() & origin_raw.notna()
    for i in origin.index[missing]:
        raw = str(origin_raw[i]).strip()
        if not raw:
            continue
        says_imported = bool(NON_PLACES.search(raw))
        sampled = sampled_country[i] if pd.notna(sampled_country[i]) else None
        # a named region is still usable inside "Imported from Zanzibar"
        found = to_region_country(raw, None if says_imported else sampled)
        found_status, found_confidence = "inferred_region", 0.8
        if found is None and not says_imported and sampled and re.search(r"[a-zA-Z]{3}", raw):
            # unidentified place in the country of collection → probably a local product
            found, found_status, found_confidence = sampled, "assumed_local", 0.35
        if found:
            origin[i] = found
            status[i] = found_status
            confidence[i] = found_confidence
    return origin, status, confidence


_patterns = None


def _country_patterns():
    global _patterns
    if _patterns is None:
        names = {}
        for c in pycountry.countries:
            display = DISPLAY.get(c.name, getattr(c, "common_name", None) or c.name)
            for n in {c.name, getattr(c, "common_name", None), display}:
                if n and len(n) > 3:
                    names[n.lower()] = display
        for alias, target in ALIASES.items():
            if len(alias) > 3:
                c = pycountry.countries.lookup(target)
                names[alias] = DISPLAY.get(c.name, getattr(c, "common_name", None) or c.name)
        _patterns = [(re.compile(rf"\b{re.escape(k)}\b"), v) for k, v in sorted(names.items(), key=lambda kv: -len(kv[0]))]
    return _patterns


# ---------- Pure Earth RMS ----------
RMS_COUNTRY = {
    1: ("Ghana", None), 3: ("India", "Maharashtra"), 4: ("India", "Uttar Pradesh"), 6: ("India", "Tamil Nadu"),
    7: ("Indonesia", None), 8: ("Bangladesh", None), 9: ("Philippines", None), 10: ("Colombia", None),
    11: ("Tajikistan", None), 12: ("Kyrgyzstan", None), 13: ("Kazakhstan", None), 14: ("Georgia", None),
    15: ("Armenia", None), 16: ("Mexico", None), 17: ("Peru", None), 18: ("Tanzania", None), 19: ("Bolivia", None),
    20: ("Egypt", None), 22: ("Kenya", None), 23: ("Tunisia", None), 24: ("Nigeria", None), 25: ("Uganda", None),
    26: ("Pakistan", None), 27: ("Nepal", None), 28: ("Azerbaijan", None), 29: ("Vietnam", None), 30: ("Turkey", None),
}
RMS_CATEGORY = {
    1: "spices", 2: "ceramic_tableware", 3: "metal_cookware", 4: "plastic_foodware", 5: "medicines",
    6: "cosmetics", 7: "sweets", 8: "toys_children", 9: "paint", 10: "staple_food", 11: "food_other",
    12: "other", 13: "paint", 14: "paint", 15: "paint",
}
RMS_CATEGORY_LABEL = {
    1: "Spices", 2: "Ceramic foodware", 3: "Metallic cookware", 4: "Plastic foodware", 5: "Medicines",
    6: "Cosmetics", 7: "Sweets", 8: "Toys", 9: "Paints", 10: "Main starch", 11: "Other food",
    12: "Other non-food item", 13: "Paint craft/art", 14: "Paint colorant/pigment", 15: "Paint - unclassified",
}


def load_rms():
    d = pd.read_excel(RAW / "rms.xlsx", sheet_name="Data")
    sampled = d["Country"].map(lambda c: RMS_COUNTRY.get(c, (None, None)))
    sampled_country = sampled.map(lambda t: to_country(t[0]))
    region = sampled.map(lambda t: t[1])
    region = region.where(region.notna(), d["City"].astype("string").str.title())
    origin_raw = d["Country/region of origin"]
    origin = origin_raw.map(to_country)
    # "local" = a product from the country of collection
    is_local = origin_raw.astype("string").str.strip().str.lower().eq("local")
    origin = origin.where(~is_local, sampled_country)
    origin, origin_status, origin_confidence = resolve_regions(origin, origin_raw, sampled_country)
    value = d["Highest XRF reading"]
    return pd.DataFrame({
        "source": "pure_earth_rms",
        "source_id": d["Item ID"].astype("string"),
        "category": d["Sample type category"].map(RMS_CATEGORY),
        "category_raw": d["Sample type category"].map(RMS_CATEGORY_LABEL),
        "product_name": d["Sample description"].astype("string").str.strip().str.capitalize(),
        "brand": None,
        "manufacturer": None,
        "origin_country": origin,
        "origin_status": origin_status,
        "origin_confidence": origin_confidence,
        "origin_raw": origin_raw,
        "sampled_country": sampled_country,
        "sampled_region": region,
        "year": pd.NA,  # collected 2021-2023, no per-sample date
        "method": "xrf",
        "unit": "ppm",
        "lead_value": value,
        "lead_ppm": value,
        # 0 = below the XRF detection limit; an absent value stays "missing"
        # and must never be read as "non-detected"
        "non_detect": value.notna() & value.le(0),
        "result_status": value.map(lambda v: "missing" if pd.isna(v) else ("non_detected" if v <= 0 else "detected")),
        "sampling_strategy": "market_screening",
        "sampling_raw": "Rapid Market Screening",
    })


# ---------- NYC ----------
NYC_CATEGORY = {
    "Food-Spice": "spices", "Dietary Supplement/Medications/Remedy": "medicines", "Food Other": "food_other",
    "Cosmetics": "cosmetics", "Tableware/Pottery": "tableware", "Toys/Children's Products": "toys_children",
    "Food-Candy": "sweets", "Religious powder": "religious_powder", "Other": "other", "Jewelry": "jewelry",
    "Paint Supplies": "paint",
}


# "How the product was obtained" (investigation_type in the NYC dataset).
# The city does not document what "A" means, so it is left as unknown.
NYC_SAMPLING = {"C": "case_investigation", "S": "store_survey", "A": "unknown"}


def load_nyc():
    n = pd.read_json(RAW / "nyc.json")
    n = n[(n["metal"] == "Lead") & (n["product_type"] != "QA/QC - Lab test")].copy()
    conc = pd.to_numeric(n["concentration"], errors="coerce")
    non_detect = conc < 0  # -1 means non-detected in this source
    is_ppb = n["units"] == "ppb"
    value = conc.where(~non_detect)
    value = value.where(~is_ppb, value / 1000)  # ppb → ppm
    unit = n["units"].replace({"mg/cm^2": "mg/cm2", "ppb": "ppm"})
    ppm = value.where(unit == "ppm")
    return pd.DataFrame({
        "source": "nyc_doh",
        "source_id": n["row_id"].astype("string"),
        "category": n["product_type"].map(NYC_CATEGORY),
        "category_raw": n["product_type"],
        "product_name": n["product_name"].astype("string").str.strip(),
        "brand": None,
        "manufacturer": n["manufacturer"].where(n["manufacturer"] != "UNKNOWN OR NOT STATED"),
        "origin_country": n["made_in_country"].map(to_country),
        "origin_status": n["made_in_country"].map(lambda v: "declared" if to_country(v) else "unknown"),
        "origin_confidence": n["made_in_country"].map(lambda v: 1.0 if to_country(v) else None),
        "origin_raw": n["made_in_country"],
        "sampled_country": n["purchase_country"].map(to_country),
        "sampled_region": None,
        "year": pd.to_datetime(n["collection_date"], errors="coerce").dt.year,
        "method": n["analysis_type"].str.lower().replace({"laboratory": "laboratory", "xrf": "xrf"}),
        "unit": unit,
        "lead_value": value,
        "lead_ppm": ppm,
        "non_detect": non_detect,
        "result_status": conc.map(lambda v: "missing" if pd.isna(v) else ("non_detected" if v < 0 else "detected")),
        "sampling_strategy": n["investigation_type"].map(NYC_SAMPLING).fillna("unknown"),
        "sampling_raw": n["investigation_type"],
    })


# ---------- King County ----------
KC_CATEGORY = {
    "Cookware/pressure cooker": "metal_cookware", "Other": "other", "Cosmetics - eye": "cosmetics",
    "Seasoning": "spices", "Jewelry": "jewelry", "Toys/Children's Products": "toys_children",
    "Dishware/Utensils": "tableware", "Dishware/utensils": "tableware", "Cosmetics": "cosmetics", "Food": "food_other",
    "Cosmetics - lip": "cosmetics", "Cosmetics - other": "cosmetics", "Dietary Supplement/Medications": "medicines",
    "Candy": "sweets", "Incense": "other",
}


KC_SAMPLING = {
    "Community product testing event": "community_event",
    "Research Project": "research",
    "Case Investigation": "case_investigation",
}


def load_king_county():
    k = pd.read_json(RAW / "kingcounty.json")
    k = k[k["product_type"] != "Soil"].copy()
    value = pd.to_numeric(k["lead_concentration_ppm"], errors="coerce")
    non_detect = k["qualifier"].fillna("").str.startswith("<")
    brand = k["brand_name"].where(k["brand_name"] != "Not available")
    manufacturer = k["manufacturer"].where(k["manufacturer"] != "Not available")
    return pd.DataFrame({
        "source": "king_county",
        "source_id": None,
        "category": k["product_type"].map(KC_CATEGORY),
        "category_raw": k["product_type"],
        "product_name": k["product_name"].astype("string").str.strip(),
        "brand": brand,
        "manufacturer": manufacturer,
        "origin_country": k["made_in_country"].map(to_country),
        "origin_status": k["made_in_country"].map(lambda v: "declared" if to_country(v) else "unknown"),
        "origin_confidence": k["made_in_country"].map(lambda v: 1.0 if to_country(v) else None),
        "origin_raw": k["made_in_country"],
        "sampled_country": "United States",
        "sampled_region": "King County, WA",
        "year": pd.to_numeric(k["year_tested"], errors="coerce"),
        "method": k["test_method"].str.lower(),
        "unit": "ppm",
        "lead_value": value,  # for "<" results this is the detection limit
        "lead_ppm": value.where(~non_detect),
        "non_detect": non_detect,
        "result_status": pd.Series(
            ["missing" if pd.isna(v) else ("non_detected" if nd else "detected")
             for v, nd in zip(value, non_detect)], index=k.index),
        "sampling_strategy": k["data_source"].map(KC_SAMPLING).fillna("unknown"),
        "sampling_raw": k["data_source"],
    })


def clean_text(df):
    """Clean broken characters inherited from the sources (encoding lost upstream).

    Example: King County publishes "The cr<?> me shop" for "The crème shop".
    The U+FFFD replacement character is mapped to its most likely accented form,
    or removed when no mapping applies.
    """
    fixes = {"cr�me": "crème", "saut�": "sauté", "caf�": "café"}
    for column in ("product_name", "brand", "manufacturer", "origin_raw", "sampled_region"):
        if column not in df:
            continue
        values = df[column].astype("string")
        for wrong, right in fixes.items():
            values = values.str.replace(wrong, right, case=False, regex=False)
        df[column] = values.str.replace("�", "", regex=False)
    return df


def main():
    df = pd.concat([load_rms(), load_nyc(), load_king_county()], ignore_index=True)
    df = clean_text(df)
    df["category"] = df["category"].fillna("other")
    df["reference_ppm"] = df["category"].map(REFERENCE_PPM)
    df["reference_basis"] = REFERENCE_BASIS
    comparable = df["reference_ppm"].notna() & (df["lead_ppm"].notna() | df["non_detect"])
    above = (df["lead_ppm"].fillna(0) > df["reference_ppm"]) & ~df["non_detect"]
    df["above_reference"] = above.where(comparable)
    df["year"] = df["year"].astype("Int64")
    df.to_csv(OUT, index=False)

    # Quick quality check
    print(f"{len(df)} measurements → {OUT.relative_to(ROOT)}")
    print(df.groupby("source").size().to_string())
    print("\nSampling strategy:")
    print(df["sampling_strategy"].value_counts().to_string())
    print("\nResult status:")
    print(df["result_status"].value_counts().to_string())
    print("\nOrigin:")
    print(df["origin_status"].value_counts().to_string())
    unmatched = df.loc[df["origin_country"].isna() & df["origin_raw"].notna(), "origin_raw"].astype(str)
    unmatched = unmatched[~unmatched.str.lower().isin(["not available", "unknown or not stated", "local"])]
    print("Most frequent unrecognised origins:")
    print(unmatched.value_counts().head(15).to_string())


if __name__ == "__main__":
    main()
