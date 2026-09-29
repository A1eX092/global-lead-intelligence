"""Construit data/countries.csv : contexte par pays (peintures + réglementation).

Granularité différente du fichier de mesures : ici une ligne = un pays.
Source : Our World in Data, qui compile les études IPEN (plus de 100 études,
59 pays, plus de 4 000 peintures) et le suivi OMS/PNUE des lois sur la peinture.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "ipen"
OUT = ROOT / "data" / "countries.csv"

FILES = {
    "paint_over_90ppm_pct": ("lead-paint-over-90ppm.csv", "share_paints_exceeding_90ppm_lead"),
    "paint_over_600ppm_pct": ("lead-paint-over-600ppm.csv", "share_paints_exceeding_600ppm_lead"),
    "paint_over_10000ppm_pct": ("lead-paint-over-10000ppm.csv", "share_paints_exceeding_10000ppm_lead"),
    "lead_paint_law": ("legal-controls-lead-paint.csv", "lead_paint_regulation"),
}


def main():
    out = None
    for field, (name, column) in FILES.items():
        d = pd.read_csv(RAW / name).rename(columns={"entity": "country", "code": "iso3", column: field})
        d = d.rename(columns={"year": f"{field}_year"})[["country", "iso3", field, f"{field}_year"]]
        out = d if out is None else out.merge(d, on=["country", "iso3"], how="outer")
    out["lead_paint_law"] = out["lead_paint_law"].map({"Yes": True, "No": False})
    out = out.sort_values("country")
    out.to_csv(OUT, index=False)
    print(f"{len(out)} pays → {OUT.relative_to(ROOT)}")
    tested = out["paint_over_90ppm_pct"].notna()
    print(f"{tested.sum()} pays avec des tests de peinture ; {int(out['lead_paint_law'].eq(False).sum())} pays sans loi sur la peinture au plomb")
    worst = out[tested].nlargest(8, "paint_over_90ppm_pct")[["country", "paint_over_90ppm_pct", "paint_over_10000ppm_pct", "lead_paint_law"]]
    print(worst.to_string(index=False))


if __name__ == "__main__":
    main()
