#!/usr/bin/env python3
"""Submit ElectrifyRadar sitemap URLs to IndexNow.

Not run by CI. Run it after a deploy is live:

    python3 scripts/indexnow.py
    python3 scripts/indexnow.py --dry-run

The key file is written into dist/ at build time and must be reachable at
https://electrifyradar.com/<key>.txt before a live ping will succeed.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import load_json  # noqa: E402

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
INDEXNOW = "https://api.indexnow.org/indexnow"
BATCH = 10000


def locs(path: Path):
    tree = ET.parse(path)
    root = tree.getroot()
    return [node.text.strip() for node in root.findall(".//sm:loc", NS) if node.text]


def page_urls(dist: Path):
    index = dist / "sitemap.xml"
    if not index.exists():
        raise SystemExit("dist/sitemap.xml is missing. Run python3 scripts/build_site.py first.")
    urls = []
    # Child sitemaps are the page lists. The index only points at those files.
    children = [dist / Path(url).name for url in locs(index)]
    if not children:
        children = [index]
    for child in children:
        if child.name == "sitemap.xml":
            continue
        if not child.exists():
            raise SystemExit(f"Missing {child}")
        urls.extend(locs(child))
    # Drop duplicates, keep order.
    seen = set()
    ordered = []
    for url in urls:
        if url in seen or url.endswith(".xml"):
            continue
        seen.add(url)
        ordered.append(url)
    return ordered


def main():
    parser = argparse.ArgumentParser(description="Ping IndexNow with sitemap URLs")
    parser.add_argument("--dry-run", action="store_true", help="Print the payload size and do not send it")
    parser.add_argument("--url", action="append", default=[], help="Submit only these absolute URLs")
    args = parser.parse_args()
    site = load_json(ROOT / "config" / "site.json")
    key = (site.get("indexnow_key") or "").strip()
    origin = site["canonical_origin"].rstrip("/")
    host = origin.split("://", 1)[-1]
    if not key:
        raise SystemExit("config/site.json indexnow_key is empty")
    urls = args.url or page_urls(ROOT / "dist")
    print(f"{len(urls)} URLs, host {host}")
    if args.dry_run:
        print(urls[0])
        print(urls[-1])
        return
    for start in range(0, len(urls), BATCH):
        chunk = urls[start:start + BATCH]
        payload = {
            "host": host,
            "key": key,
            "keyLocation": f"{origin}/{key}.txt",
            "urlList": chunk,
        }
        request = urllib.request.Request(
            INDEXNOW,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "ElectrifyRadarIndexNow/1.0"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8", "replace")
            print(f"IndexNow {response.status} for {len(chunk)} URLs {body[:200]}")


if __name__ == "__main__":
    main()
