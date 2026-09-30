"""Build data/countries.csv: per-country context (paint studies + regulation).

Different granularity from the measurement file: one row per country.
Sources: Our World in Data, which compiles the IPEN paint studies (100+ studies,
59 countries, 4,000+ paints), and the WHO Global Health Observatory for laws.
"""
from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "ipen"
OUT = ROOT / "data" / "countries.csv"

FILES = {
    "paint_over_90ppm_pct": ("lead-paint-over-90ppm.csv", "share_paints_exceeding_90ppm_lead"),
    "paint_over_600ppm_pct": ("lead-paint-over-600ppm.csv", "share_paints_exceeding_600ppm_lead"),
    "paint_over_10000ppm_pct": ("lead-paint-over-10000ppm.csv", "share_paints_exceeding_10000ppm_lead"),
    "lead_paint_law_owid": ("legal-controls-lead-paint.csv", "lead_paint_regulation"),
}


def who_lead_paint_law():
    """Lead paint laws per WHO (GHO indicator LEADCONTROL).

    One row per country: the status (Yes / No / No data) and, where a law
    exists, the year it came into force. Used as the reference source here: it
    covers 195 countries against 164 in the Our World in Data version, and it
    carries the historical depth (earliest laws from 1977).
    """
    path = RAW.parent / "who" / "leadcontrol.json"
    if not path.exists():
        return None
    rows = json.loads(path.read_text())["value"]
    d = pd.DataFrame([{
        "iso3": r["SpatialDim"],
        "lead_paint_law": {"Yes": True, "No": False}.get(r["Value"]),
        "lead_paint_law_year": r["TimeDim"] if r["Value"] == "Yes" else None,
    } for r in rows if r.get("SpatialDimType") == "COUNTRY"])
    return d.astype({"lead_paint_law_year": "Int64"})


def main():
    out = None
    for field, (name, column) in FILES.items():
        d = pd.read_csv(RAW / name).rename(columns={"entity": "country", "code": "iso3", column: field})
        d = d.rename(columns={"year": f"{field}_year"})[["country", "iso3", field, f"{field}_year"]]
        out = d if out is None else out.merge(d, on=["country", "iso3"], how="outer")
    out["lead_paint_law_owid"] = out["lead_paint_law_owid"].map({"Yes": True, "No": False})
    who = who_lead_paint_law()
    if who is not None:
        out = out.merge(who, on="iso3", how="outer")
        out["country"] = out["country"].fillna(out["iso3"])
    out = out.sort_values("country")
    out.to_csv(OUT, index=False)
    print(f"{len(out)} countries → {OUT.relative_to(ROOT)}")
    tested = out["paint_over_90ppm_pct"].notna()
    print(f"{tested.sum()} countries with paint studies")
    if "lead_paint_law" in out:
        print(f"WHO: {int(out['lead_paint_law'].eq(True).sum())} countries with a law, "
              f"{int(out['lead_paint_law'].eq(False).sum())} without, "
              f"{int(out['lead_paint_law'].isna().sum())} with no data")
        years = out["lead_paint_law_year"].dropna()
        print(f"Years in force: {years.min()}-{years.max()}, median {int(years.median())}")
    worst = out[tested].nlargest(8, "paint_over_90ppm_pct")[["country", "paint_over_90ppm_pct", "paint_over_10000ppm_pct", "lead_paint_law"]]
    print(worst.to_string(index=False))


if __name__ == "__main__":
    main()
