"""Fetch the RASFF notifications (EU food alerts) that concern lead.

The public RASFF Window API cannot filter by hazard, so this walks every
notification (100 per page) and keeps those whose subject mentions lead, in
five languages. The result is written to data/raw/rasff/rasff.json.
"""
from pathlib import Path
import json
import re
import ssl
import time
from urllib.request import Request, urlopen

import certifi

OUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "rasff" / "rasff.json"
URL = "https://webgate.ec.europa.eu/rasff-window/backend/public/notification/search/consolidated/en/"
LEAD = re.compile(r"\blead\b|\bplomb\b|\bblei\b|\bpiombo\b|\bplomo\b", re.I)
PAGE_SIZE = 100  # the maximum the API accepts


def page(number, context):
    body = json.dumps({"parameters": {"pageNumber": number, "itemsPerPage": PAGE_SIZE}}).encode()
    request = Request(URL, data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": "lead-project/0.1 (open data harmonisation)",
    })
    with urlopen(request, context=context) as response:
        return json.load(response)


def main():
    context = ssl.create_default_context(cafile=certifi.where())
    first = page(1, context)
    total_pages, total = first["totalPages"], first["totalElements"]
    print(f"{total} RASFF notifications, {total_pages} pages")

    matches, scanned = [], 0
    for number in range(1, total_pages + 1):
        data = first if number == 1 else page(number, context)
        notifications = data.get("notifications", [])
        scanned += len(notifications)
        matches += [n for n in notifications if LEAD.search(n.get("subject") or "")]
        if number % 25 == 0 or number == total_pages:
            print(f"  page {number}/{total_pages} — {scanned} read, {len(matches)} about lead")
        time.sleep(0.2)  # stay polite with the server

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"scanned": scanned, "total": total, "notifications": matches}, ensure_ascii=False))
    print(f"{len(matches)} notifications kept → {OUT}")


if __name__ == "__main__":
    main()
