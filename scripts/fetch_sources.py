#!/usr/bin/env python3
"""Download public source files into data/raw/.

Direct files (urllib):
  TECH Clean California contractor project workbook
  Mass Save Heat Pump Installer Network workbook
  Minnesota DLI mechanical contractor bond CSV
  NYS Clean Heat residential heat-pump contractors (the finder's public JSON API)

Browser steps (optional Playwright + installed Chrome):
  CSLB C-20 and C-36 classification workbooks
  Efficiency Maine heat pump vendor locator results

The Mass Save file is the spreadsheet linked as "Download the spreadsheet"
on the public finder. masssave.com robots.txt disallows /-/media/ for
crawlers. This script requests that one published export, not the media library.

Re-run, then:
  python3 scripts/build_listings.py
  python3 scripts/build_site.py
"""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

from common import RAW

AS_OF = "2026-11-03"
UA = "ElectrifyRadarDataBot/1.0 (public roster rebuild; hello@electrifyradar.com)"

DIRECT = {
    "ContractorProjectData_2026-10-20.xlsx": "https://techcleanca.com/documents/5792/ContractorProjectData_2026-10-20.xlsx",
    "hpin-contractors.xlsx": "https://www.masssave.com/-/media/Files/PDFs/Contractor-Lists/hpin-contractors.xlsx",
    "mn-mechanical-contractor-bond.csv": "https://secure.doli.state.mn.us/ccld/data/MNDLILicRegCertExport_Mechanical_Contractor_Bond.csv",
}


def download(url: str, dest: Path):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=180) as response:
        dest.write_bytes(response.read())
    print(f"saved {dest.name} ({dest.stat().st_size} bytes)")


def fetch_nys():
    base = "https://nyscleanheat-findacontractor.icfsightline.com"
    services = ["ASHP Installer", "AWHP Installer", "GSHP Installer", "HPWH Installer"]
    by_id = {}

    def post(body):
        raw = json.dumps(body).encode()
        req = urllib.request.Request(
            base + "/api/contractor/search",
            data=raw,
            headers={"User-Agent": UA, "Accept": "application/json", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=90) as response:
            return json.loads(response.read().decode())

    for service in services:
        page = 0
        while True:
            payload = post({
                "page": page,
                "programParticipationFlags": [],
                "name": None,
                "origin": None,
                "radius": 500,
                "products": [],
                "services": [service],
                "territories": [],
                "sectors": ["Residential"],
                "programs": [],
                "energyProgramFilters": [],
            })
            results = payload.get("results") or []
            print(f"NYS {service} page {page} ({len(results)})")
            for item in results:
                result = item["result"]
                rec = by_id.setdefault(result["id"], {"services": []})
                # Drop the contact email before anything is written to disk.
                contact = dict(result.get("contact") or {})
                contact.pop("email", None)
                result = dict(result)
                result["contact"] = contact
                rec["result"] = result
                if service not in rec["services"]:
                    rec["services"].append(service)
            if page + 1 >= (payload.get("totalPages") or 1) or not results:
                break
            page += 1
            time.sleep(0.25)
    dest = RAW / "nys-contractors.json"
    dest.write_text(json.dumps({"retrieved": AS_OF, "count": len(by_id), "contractors": list(by_id.values())}), encoding="utf-8")
    print(f"saved nys-contractors.json ({len(by_id)} contractors)")


def fetch_browser():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright is not installed. CSLB and Efficiency Maine files were not refreshed.")
        print("Install Playwright, or place these files in data/raw/ yourself:")
        print("  cslb-c20.xlsx  cslb-c36.xlsx  eme-heat-pumps.html")
        return

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.goto("https://www.cslb.ca.gov/onlineservices/dataportal/ListByClassification.aspx", wait_until="domcontentloaded", timeout=90000)
        for code, filename in (("C-20", "cslb-c20.xlsx"), ("C-36", "cslb-c36.xlsx")):
            page.evaluate(
                """(code) => {
                  const sel = document.querySelector('#lbClassification');
                  for (const opt of sel.options) opt.selected = opt.value === code;
                }""",
                code,
            )
            with page.expect_download(timeout=180000) as download_info:
                page.evaluate("() => document.querySelector('#btnSearch').click()")
            download = download_info.value
            target = RAW / filename
            download.save_as(str(target))
            print(f"saved {filename} ({target.stat().st_size} bytes)")
            page.goto("https://www.cslb.ca.gov/onlineservices/dataportal/ListByClassification.aspx", wait_until="domcontentloaded", timeout=90000)

        page.goto("https://www.efficiencymaine.com/at-home/vendor-locator/", wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(1000)
        page.evaluate(
            """() => {
              const sel = document.querySelector('#service-area');
              for (const opt of sel.options) opt.selected = opt.value === '4';
              document.querySelector('#zipcode').value = '04101';
              document.querySelector('#distance').value = '10';
              document.querySelector('#sorting').value = '3';
            }"""
        )
        page.click("form.loc18__form input[type=submit]")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_selector(".results18__item", timeout=60000)
        html_doc = page.content()
        (RAW / "eme-heat-pumps.html").write_text(html_doc, encoding="utf-8")
        print(f"saved eme-heat-pumps.html ({len(html_doc)} chars)")
        browser.close()


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in DIRECT.items():
        download(url, RAW / name)
    fetch_nys()
    fetch_browser()


if __name__ == "__main__":
    main()
