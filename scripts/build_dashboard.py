"""Build dashboard/index.html (a self-contained, offline page) from data/harmonized.csv."""
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "harmonized.csv"
OUT = ROOT / "dashboard" / "index.html"
ARTIFACT = ROOT / "dashboard" / "artifact.html"
TEMPLATE = Path(__file__).resolve().parent / "dashboard_template.html"


def recalls():
    """Official recalls (FDA, CPSC, RASFF): no concentrations, but named products."""
    path = ROOT / "data" / "recalls.csv"
    if not path.exists():
        return []
    r = pd.read_csv(path)
    r = r[["source", "year", "product", "firm", "origin_country", "category", "reason", "url"]]
    r = r.where(pd.notna(r), None)
    return json.loads(r.to_json(orient="records"))


def country_context(names):
    """Per-country context (IPEN paints + law), keyed by the country name used here.

    Joined on ISO3 codes: names differ between sources ("Türkiye" here,
    "Turkey" in Our World in Data).
    """
    import pycountry

    ctx = pd.read_csv(ROOT / "data" / "countries.csv").set_index("iso3")
    out = {}
    for name in sorted(set(names)):
        try:
            iso3 = pycountry.countries.lookup(name).alpha_3
        except LookupError:
            continue
        if iso3 not in ctx.index:
            continue
        row = ctx.loc[iso3]
        entry = {
            "p90": none_if_nan(row["paint_over_90ppm_pct"]),
            "p10k": none_if_nan(row["paint_over_10000ppm_pct"]),
            "year": none_if_nan(row["paint_over_90ppm_pct_year"]),
            "law": None if pd.isna(row["lead_paint_law"]) else bool(row["lead_paint_law"]),
            "law_year": none_if_nan(row.get("lead_paint_law_year")),
        }
        if any(v is not None for v in entry.values()):
            out[name] = entry
    return out


def none_if_nan(value):
    return None if pd.isna(value) else (int(value) if float(value).is_integer() else float(value))


def main():
    d = pd.read_csv(SRC, low_memory=False)
    dims = {}

    def encode(col):
        values = sorted(d[col].dropna().astype(str).unique())
        dims[col] = values
        index = {v: i for i, v in enumerate(values)}
        return d[col].map(lambda x: index.get(str(x)) if pd.notna(x) else None)

    rows = pd.DataFrame({
        "s": encode("source"),
        "c": encode("category"),
        "o": encode("origin_country"),
        "k": encode("sampled_country"),
        "m": encode("method"),
        "g": encode("sampling_strategy"),
        "u": encode("unit"),
        "p": d["product_name"].fillna("").astype(str).str.slice(0, 80),
        "b": d["brand"].fillna(d["manufacturer"]).fillna("").astype(str).str.slice(0, 50),
        "y": d["year"],
        "v": d["lead_value"].round(2),
        "n": d["non_detect"].astype(bool).astype(int),
        "a": d["above_reference"].map({True: 1, False: 0, "True": 1, "False": 0}),
        "r": d["reference_ppm"],
    })
    records = json.loads(rows.to_json(orient="values"))
    payload = {"cols": list(rows.columns), "rows": records, "dims": dims,
               "countries": country_context(dims["sampled_country"] + dims["origin_country"]),
               "recalls": recalls(),
               "generated": pd.Timestamp.now().strftime("%Y-%m-%d")}
    html = TEMPLATE.read_text(encoding="utf-8").replace("__DATA__", json.dumps(payload, ensure_ascii=False))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"{len(records)} rows → {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.1f} Mo)")

    # Artifact build: the platform supplies its own <html>/<head>/<body>
    # skeleton, so keep only the title, the style block and the body content.
    head = html.split("<title>", 1)[1]
    title, rest = head.split("</title>", 1)
    style = "<style>" + rest.split("<style>", 1)[1].split("</style>", 1)[0] + "</style>"
    body = html.split("<body>", 1)[1].rsplit("</body>", 1)[0]
    ARTIFACT.write_text(f"<title>{title}</title>\n{style}\n{body}", encoding="utf-8")
    print(f"Artifact build → {ARTIFACT.relative_to(ROOT)} ({ARTIFACT.stat().st_size / 1e6:.1f} Mo)")


if __name__ == "__main__":
    main()
