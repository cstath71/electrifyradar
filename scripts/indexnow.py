#!/usr/bin/env python3
"""Submit ElectrifyRadar URLs to IndexNow.

The Pages workflow runs this after a successful deploy:

    python3 scripts/indexnow.py --after-deploy --state .indexnow/state.json

The first run (no saved state) submits the homepage, state hubs, guides, the
other sitemap page URLs, and city pages, largest cities first, up to 10,000
URLs. Later runs submit URLs whose sitemap lastmod changed, then new URLs,
capped at the same limit. Installer profiles are included only when their
lastmod changes after the first run.

The key file is written into dist/ at build time and must be reachable at
https://electrifyradar.com/<key>.txt before a live ping will succeed.

Manual full submission (every sitemap URL, in batches of 10,000):

    python3 scripts/build_site.py
    python3 scripts/indexnow.py --dry-run
    python3 scripts/indexnow.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import load_json  # noqa: E402

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
INDEXNOW = "https://api.indexnow.org/indexnow"
BATCH = 10000
LIMIT = 10000


def locs(path: Path):
    return [url for url, _lastmod in url_entries(path)]


def url_entries(path: Path) -> list[tuple[str, str]]:
    tree = ET.parse(path)
    root = tree.getroot()
    rows = []
    for node in root.findall("sm:url", NS):
        loc = node.find("sm:loc", NS)
        last = node.find("sm:lastmod", NS)
        if loc is None or not loc.text:
            continue
        lastmod = last.text.strip() if last is not None and last.text else ""
        rows.append((loc.text.strip(), lastmod))
    if rows:
        return rows
    # Sitemap index files have <sitemap><loc>, not <url><loc>.
    for node in root.findall(".//sm:loc", NS):
        if node.text:
            rows.append((node.text.strip(), ""))
    return rows


def load_sitemap_groups(dist: Path) -> dict[str, list[tuple[str, str]]]:
    index = dist / "sitemap.xml"
    if not index.exists():
        raise SystemExit("dist/sitemap.xml is missing. Run python3 scripts/build_site.py first.")
    groups = {"pages": [], "cities": [], "installers": []}
    for url, _lastmod in url_entries(index):
        name = Path(url).name
        child = dist / name
        if name == "sitemap.xml":
            continue
        if not child.exists():
            raise SystemExit(f"Missing {child}")
        if "cities" in name:
            key = "cities"
        elif "installers" in name:
            key = "installers"
        else:
            key = "pages"
        groups[key].extend(url_entries(child))
    return groups


def lastmod_map(groups: dict[str, list[tuple[str, str]]]) -> dict[str, str]:
    found = {}
    for rows in groups.values():
        for url, lastmod in rows:
            found[url] = lastmod
    return found


def city_counts(listings, origin: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    origin = origin.rstrip("/")
    for row in listings:
        url = f"{origin}/us/{row['admin1_slug']}/{row['city_slug']}/"
        counts[url] = counts.get(url, 0) + 1
    return counts


def select_urls(groups, counts, previous, first_run: bool, limit: int = LIMIT) -> list[str]:
    """Pick the IndexNow urlList.

    First run: page URLs (homepage, state hubs, guides, and the other
    indexable pages), then city pages with the most listings. Installer
    profiles wait until a later run changes their lastmod.
    Later runs: URLs whose lastmod differs from the saved map, pages first,
    then larger cities, then installer profiles.
    """
    counts = counts or {}

    def rank(url: str):
        return (-counts.get(url, 0), url)

    chosen = []
    seen = set()

    def add(urls):
        for url in urls:
            if url in seen:
                continue
            seen.add(url)
            chosen.append(url)
            if len(chosen) >= limit:
                return True
        return False

    if first_run:
        pages = [url for url, _lastmod in groups.get("pages") or []]
        cities = sorted((url for url, _lastmod in groups.get("cities") or []), key=rank)
        add(pages)
        if len(chosen) < limit:
            add(cities)
        return chosen

    previous = previous or {}

    def changed(rows):
        return [url for url, lastmod in rows if previous.get(url) != lastmod]

    pages = changed(groups.get("pages") or [])
    cities = sorted(changed(groups.get("cities") or []), key=rank)
    installers = changed(groups.get("installers") or [])
    add(pages)
    if len(chosen) < limit:
        add(cities)
    if len(chosen) < limit:
        add(installers)
    return chosen


def page_urls(dist: Path):
    groups = load_sitemap_groups(dist)
    seen = set()
    ordered = []
    for key in ("pages", "cities", "installers"):
        for url, _lastmod in groups[key]:
            if url in seen or url.endswith(".xml"):
                continue
            seen.add(url)
            ordered.append(url)
    return ordered


def key_is_live(origin: str, key: str, attempts: int = 8, delay: float = 5) -> bool:
    url = f"{origin.rstrip('/')}/{key}.txt"
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                body = response.read().decode("utf-8", "replace").strip()
            if body == key:
                print(f"key file live at {url}")
                return True
            print(f"key file mismatch at {url} on attempt {attempt}")
        except Exception as exc:
            print(f"key file not ready ({exc}) attempt {attempt}")
        if attempt < attempts:
            time.sleep(delay)
    return False


def post_urls(origin: str, host: str, key: str, urls: list[str]) -> int:
    if not urls:
        print("IndexNow skipped, 0 URLs")
        return 0
    status = 0
    for start in range(0, len(urls), BATCH):
        chunk = urls[start:start + BATCH]
        payload = {
            "host": host,
            "key": key,
            "keyLocation": f"{origin.rstrip('/')}/{key}.txt",
            "urlList": chunk,
        }
        request = urllib.request.Request(
            INDEXNOW,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "ElectrifyRadarIndexNow/1.0"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                status = response.status
                body = response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            print(f"IndexNow {exc.code} for {len(chunk)} URLs {body[:500]}")
            raise SystemExit(1) from exc
        print(f"IndexNow {status} for {len(chunk)} URLs {body[:200]}")
        if status not in (200, 202):
            raise SystemExit(1)
    return status


def load_listings():
    payload = load_json(ROOT / "data" / "listings.json")
    if isinstance(payload, dict):
        return payload.get("listings") or []
    return payload


def after_deploy(dist: Path, state_path: Path, dry_run: bool) -> int:
    site = load_json(ROOT / "config" / "site.json")
    key = (site.get("indexnow_key") or "").strip()
    origin = site["canonical_origin"].rstrip("/")
    host = origin.split("://", 1)[-1]
    if not key:
        raise SystemExit("config/site.json indexnow_key is empty")
    state = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8") or "{}")
    previous = state.get("lastmods") or {}
    first_run = not previous
    groups = load_sitemap_groups(dist)
    urls = select_urls(groups, city_counts(load_listings(), origin), previous, first_run, LIMIT)
    mode = "first" if first_run else "changed"
    print(f"mode={mode}")
    print(f"{len(urls)} URLs, host {host}")
    if dry_run:
        if urls:
            print(urls[0])
            print(urls[-1])
        return 0
    if not urls:
        print("IndexNow skipped, 0 URLs")
        return 0
    if not key_is_live(origin, key):
        raise SystemExit(f"IndexNow key file is not live at {origin}/{key}.txt")
    status = post_urls(origin, host, key, urls)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "lastmods": lastmod_map(groups),
                "last_status": status,
                "last_count": len(urls),
                "last_mode": mode,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return status


def main():
    parser = argparse.ArgumentParser(description="Ping IndexNow with sitemap URLs")
    parser.add_argument("--dry-run", action="store_true", help="Print the payload size and do not send it")
    parser.add_argument("--url", action="append", default=[], help="Submit only these absolute URLs")
    parser.add_argument(
        "--after-deploy",
        action="store_true",
        help="Submit the first-run hub set, or URLs whose lastmod changed since --state",
    )
    parser.add_argument(
        "--state",
        default=str(ROOT / ".indexnow" / "state.json"),
        help="JSON file of URL lastmods from the previous successful submission",
    )
    args = parser.parse_args()
    if args.after_deploy:
        after_deploy(ROOT / "dist", Path(args.state), args.dry_run)
        return
    site = load_json(ROOT / "config" / "site.json")
    key = (site.get("indexnow_key") or "").strip()
    origin = site["canonical_origin"].rstrip("/")
    host = origin.split("://", 1)[-1]
    if not key:
        raise SystemExit("config/site.json indexnow_key is empty")
    urls = args.url or page_urls(ROOT / "dist")
    print(f"{len(urls)} URLs, host {host}")
    if args.dry_run:
        if urls:
            print(urls[0])
            print(urls[-1])
        return
    if not key_is_live(origin, key):
        raise SystemExit(f"IndexNow key file is not live at {origin}/{key}.txt")
    post_urls(origin, host, key, urls)


if __name__ == "__main__":
    main()
