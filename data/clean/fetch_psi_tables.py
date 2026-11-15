"""Download the Experimental Table of every combustion investigation in NASA PSI, as PSI publishes it.

    py data/clean/fetch_psi_tables.py

For each investigation in data/raw/psi_search/combustion_investigations.json this asks PSI's own web service
(the one its pages use) for the investigation record, and saves each file listed under "Experimental table" to
data/raw/psi_tables/ unchanged. A file that is already there is never overwritten. MANIFEST.json records, for every
file: investigation, PSI version, DOI, licence, size, SHA-256 and the day it was fetched.

Needs only the Python standard library and an internet connection. Nothing else in the repo needs the internet.
"""
import datetime
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEARCH = ROOT / "data" / "raw" / "psi_search" / "combustion_investigations.json"
OUT = ROOT / "data" / "raw" / "psi_tables"
API = "https://psi.nasa.gov/geode-py/ws"
AGENT = {"User-Agent": "space-apps-student-project"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=AGENT), timeout=60) as resp:
        return resp.read()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_file = OUT / "MANIFEST.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8")) if manifest_file.is_file() else {}
    ids = [hit["_source"]["Accession"] for hit in json.loads(SEARCH.read_text(encoding="utf-8"))["hits"]["hits"]]
    for psi in sorted(ids, key=lambda s: int(s.split("-")[1])):
        record = json.loads(get(f"{API}/repo/investigations/{psi}"))
        tables = record.get("experimentalTable") or []
        if not tables:
            print(f"{psi}: no Experimental Table")
            continue
        for table in tables:
            name = table["file_name"]
            target = OUT / name
            if target.is_file():
                print(f"{psi}: {name} already here")
                continue
            query = urllib.parse.urlencode({"file": name, "version": record["version"], "redirect": "false"}, quote_via=urllib.parse.quote)
            link = get(f"{API}/studies/{psi}/download?{query}").decode("utf-8").strip()      # PSI answers with a short-lived link to the file
            data = get(link)
            target.write_bytes(data)
            manifest[name] = {
                "investigation": psi, "acronym": record.get("investigationAcronym") or "", "title": record.get("title") or "",
                "psi_version": record.get("version"), "doi": record.get("doi") or "", "licence": record.get("licenseIdentifier") or "not stated",
                "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest().upper(), "fetched": datetime.date.today().isoformat(),
                "page": f"https://psi.nasa.gov/physci/repo/data/investigations/{psi}",
            }
            print(f"{psi}: {name}, {len(data)} bytes")
    manifest_file.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(manifest)} files listed in {manifest_file}")


if __name__ == "__main__":
    main()
