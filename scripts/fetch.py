"""Download the raw source files into data/raw/."""
from pathlib import Path
import shutil
import ssl
from urllib.request import Request, urlopen

import certifi

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

SOURCES = {
    # Pure Earth, Rapid Market Screening (CC-BY 4.0) — https://zenodo.org/records/10444602
    "rms.xlsx": "https://zenodo.org/records/10444602/files/RMS%20XRF%20dataset%20(20240106).xlsx?download=1",
    # NYC Health Department, Metal Content of Consumer Products — dataset da9u-wz3r
    "nyc.json": "https://data.cityofnewyork.us/resource/da9u-wz3r.json?$limit=100000",
    # Public Health Seattle & King County (public domain) — dataset i6sy-ckp7
    "kingcounty.json": "https://data.kingcounty.gov/resource/i6sy-ckp7.json?$limit=100000",
    # Our World in Data: IPEN paint studies + the WHO/UNEP law tracker
    "ipen/lead-paint-over-90ppm.csv": "https://ourworldindata.org/grapher/lead-paint-over-90ppm.csv?csvType=full&useColumnShortNames=true",
    "ipen/lead-paint-over-600ppm.csv": "https://ourworldindata.org/grapher/lead-paint-over-600ppm.csv?csvType=full&useColumnShortNames=true",
    "ipen/lead-paint-over-10000ppm.csv": "https://ourworldindata.org/grapher/lead-paint-over-10000ppm.csv?csvType=full&useColumnShortNames=true",
    "ipen/legal-controls-lead-paint.csv": "https://ourworldindata.org/grapher/legal-controls-lead-paint.csv?csvType=full&useColumnShortNames=true",
    # WHO (Global Health Observatory): lead paint laws for 195 countries, with the
    # year each came into force — more complete than the Our World in Data version
    "who/leadcontrol.json": "https://ghoapi.azureedge.net/api/LEADCONTROL",
    # Official recalls (public domain): FDA (food) and CPSC (consumer products)
    "recalls/fda.json": 'https://api.fda.gov/food/enforcement.json?search=reason_for_recall:"lead"&limit=1000',
    "recalls/cpsc.json": "https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallTitle=lead",
}


# RASFF (EU food alerts): see fetch_rasff.py — its API forces a scan of all
# 32,000+ notifications, so it lives in a separate script.


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    context = ssl.create_default_context(cafile=certifi.where())
    for name, url in SOURCES.items():
        print(f"→ {name}")
        (RAW / name).parent.mkdir(parents=True, exist_ok=True)
        # some servers (Our World in Data) reject requests without a User-Agent
        request = Request(url, headers={"User-Agent": "lead-project/0.1 (open data harmonisation)"})
        with urlopen(request, context=context) as response, open(RAW / name, "wb") as out:
            shutil.copyfileobj(response, out)


if __name__ == "__main__":
    main()
