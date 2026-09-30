"""Construit data/countries.csv : contexte par pays (peintures + réglementation).

Granularité différente du fichier de mesures : ici une ligne = un pays.
Source : Our World in Data, qui compile les études IPEN (plus de 100 études,
59 pays, plus de 4 000 peintures) et le suivi OMS/PNUE des lois sur la peinture.
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
    """Lois sur la peinture au plomb selon l'OMS (GHO, indicateur LEADCONTROL).

    Une ligne par pays : le statut (Yes / No / No data) et, pour les pays dotés
    d'une loi, l'année d'entrée en vigueur. Source de référence ici, car elle
    couvre 195 pays contre 164 dans la reprise d'Our World in Data, et elle
    porte la profondeur historique (premières lois dès 1977).
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
    print(f"{len(out)} pays → {OUT.relative_to(ROOT)}")
    tested = out["paint_over_90ppm_pct"].notna()
    print(f"{tested.sum()} pays avec des tests de peinture")
    if "lead_paint_law" in out:
        print(f"OMS : {int(out['lead_paint_law'].eq(True).sum())} pays avec une loi, "
              f"{int(out['lead_paint_law'].eq(False).sum())} sans, "
              f"{int(out['lead_paint_law'].isna().sum())} sans donnée")
        years = out["lead_paint_law_year"].dropna()
        print(f"Années d'entrée en vigueur : {years.min()}-{years.max()}, médiane {int(years.median())}")
    worst = out[tested].nlargest(8, "paint_over_90ppm_pct")[["country", "paint_over_90ppm_pct", "paint_over_10000ppm_pct", "lead_paint_law"]]
    print(worst.to_string(index=False))


if __name__ == "__main__":
    main()
