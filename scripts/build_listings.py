#!/usr/bin/env python3
"""Rebuild data/listings.json from files in data/raw/.

Does not invent installers, phones, ratings, or counts. Ownership is
platform-owned or franchise only when the business name matches
data/ownership/platforms.json. Everyone else is ownership unverified.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl
from bs4 import BeautifulSoup

from common import (
    DATA,
    RAW,
    STATES,
    clean_phone,
    clean_url,
    load_json,
    normalize_name,
    phrase_in_name,
    slugify,
    title_place,
    zip5,
)

# USPS ZIP3 ranges. Used only to avoid filing a mailing address under the
# wrong state when a roster has a city and ZIP but no state column.
ZIP3_RANGES = [
    (10, 27, "MA"), (28, 29, "RI"), (30, 38, "NH"), (39, 49, "ME"), (50, 59, "VT"),
    (60, 69, "CT"), (70, 89, "NJ"), (100, 149, "NY"), (150, 196, "PA"),
    (197, 199, "DE"), (200, 205, "DC"), (206, 219, "MD"), (220, 246, "VA"),
    (247, 268, "WV"), (270, 289, "NC"), (290, 299, "SC"), (300, 319, "GA"),
    (320, 349, "FL"), (350, 369, "AL"), (370, 385, "TN"), (386, 397, "MS"),
    (400, 427, "KY"), (430, 459, "OH"), (460, 479, "IN"), (480, 499, "MI"),
    (500, 528, "IA"), (530, 549, "WI"), (550, 567, "MN"), (570, 577, "SD"),
    (580, 588, "ND"), (590, 599, "MT"), (600, 629, "IL"), (630, 658, "MO"),
    (660, 679, "KS"), (680, 693, "NE"), (700, 714, "LA"), (716, 729, "AR"),
    (730, 749, "OK"), (750, 799, "TX"), (800, 816, "CO"), (820, 831, "WY"),
    (832, 838, "ID"), (840, 847, "UT"), (850, 865, "AZ"), (870, 884, "NM"),
    (889, 898, "NV"), (900, 961, "CA"), (967, 968, "HI"), (970, 979, "OR"),
    (980, 994, "WA"), (995, 999, "AK"),
]


def state_from_zip(postal: str) -> str:
    digits = "".join(ch for ch in (postal or "") if ch.isdigit())
    if len(digits) < 3:
        return ""
    prefix = int(digits[:3])
    for start, end, code in ZIP3_RANGES:
        if start <= prefix <= end:
            return code
    return ""

AS_OF = "2026-11-03"


def cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def blank_listing(**kwargs):
    base = {
        "country_code": "US",
        "locale": "en-US",
        "currency": "USD",
        "category": "heat_pump",
        "heat_pump_signal": "program_roster",
        "featured": False,
        "manual_j_claimed": False,
        "manual_j_note": "Not indicated in the source used for this listing.",
        "ownership_status": "unverified",
        "ownership_label": "Ownership: unverified",
        "ownership_parent": None,
        "ownership_source_url": None,
        "ownership_source_note": None,
        "ownership_matched_term": None,
        "oem_affiliations": [],
        "license_ids": [],
        "rebate_programs": [],
        "services": [],
        "sources": [],
        "phone": "",
        "website": "",
        "street": "",
        "postal_code": "",
        "lat": None,
        "lng": None,
    }
    base.update(kwargs)
    return base


def read_xlsx_rows(path: Path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = ws.iter_rows(values_only=True)
    header = None
    data = []
    for row in rows:
        if header is None:
            if row and any(row):
                # Some workbooks put a title above the header.
                values = [cell(c) for c in row]
                if "Company Name" in values or "Contractor Name" in values or "LicenseNumber" in values or values[0] == "Project Index":
                    header = values
            continue
        if not row or not any(row):
            continue
        data.append(row)
    wb.close()
    return header, data


def load_cslb(path: Path) -> dict:
    header, rows = read_xlsx_rows(path)
    idx = {name: i for i, name in enumerate(header)}
    out = {}
    for row in rows:
        number = cell(row[idx["LicenseNumber"]])
        if not number:
            continue
        out[number] = {
            "name": cell(row[idx["BusinessName"]]),
            "street": cell(row[idx["Address"]]),
            "city": cell(row[idx["City"]]),
            "state": cell(row[idx["State"]]),
            "zip": zip5(row[idx["Zip"]]),
            "phone": clean_phone(row[idx["PhoneNumber"]]),
            "classification": cell(row[idx["Classification"]]).strip(),
            "status": cell(row[idx["Status"]]).strip(),
            "expiration": cell(row[idx["ExpirationDate"]]),
            "updated": cell(row[idx["LastUpdated"]]),
            "business_type": cell(row[idx["BusinessType"]]),
        }
    return out


def source(name, url, retrieved, note):
    return {"name": name, "url": url, "retrieved": retrieved, "note": note}


def mass_save():
    path = RAW / "hpin-contractors.xlsx"
    header, rows = read_xlsx_rows(path)
    idx = {name: i for i, name in enumerate(header)}
    listings = []
    skipped = Counter()
    for row in rows:
        name = cell(row[idx["Company Name"]])
        city = cell(row[idx["City"]])
        if not name or name == "Company Name":
            skipped["no_name"] += 1
            continue
        phone = clean_phone(row[idx["Phone"]])
        website = clean_url(row[idx["Website"]])
        if not city:
            skipped["no_city"] += 1
            continue
        if not phone and not website:
            skipped["no_contact"] += 1
            continue
        equipment = [part.strip() for part in cell(row[idx["Equipment Type(s) Installed"]]).split(";") if part.strip()]
        extra = [part.strip() for part in cell(row[idx["Additional Electric Technologies Installed"]]).split(";") if part.strip()]
        languages = [part.strip() for part in cell(row[idx["Language(s) Spoken"]]).split(";") if part.strip()]
        counties = [part.strip() for part in cell(row[idx["Counties Served"]]).split(";") if part.strip()]
        hpln = cell(row[idx["HPLN"]])
        instant = cell(row[idx["Instant Rebate"]])
        programs = [{
            "id": "mass_save_hpin",
            "name": "Mass Save Heat Pump Installer Network",
            "url": "https://www.masssave.com/residential/find-a-contractor/find-a-heat-pump-installer",
        }]
        if hpln.lower() == "active":
            programs.append({
                "id": "mass_save_hpln",
                "name": "Mass Save Heat Pump Leaders Network",
                "url": "https://www.masssave.com/residential/find-a-contractor/find-a-heat-pump-installer",
            })
        postal = zip5(row[idx["Zip"]])
        mail_state = state_from_zip(postal)
        listings.append(blank_listing(
            name=name,
            admin1="MA",
            city=title_place(city),
            address_region=mail_state or "MA",
            outside_program_state=bool(mail_state and mail_state != "MA"),
            street=title_place(cell(row[idx["Address"]])) if cell(row[idx["Address"]]).isupper() else cell(row[idx["Address"]]),
            postal_code=postal,
            phone=phone,
            website=website,
            services=equipment,
            extra={
                "counties_served": counties,
                "languages": languages,
                "additional_technologies": extra,
                "property_types": cell(row[idx["Property Type(s) Served"]]),
                "diverse_business_type": cell(row[idx["Diverse Business Type"]]),
                "instant_rebate": instant,
                "hpln": hpln,
                "mailing_state_from_zip": state_from_zip(zip5(row[idx["Zip"]])),
            },
            rebate_programs=programs,
            sources=[source(
                "Mass Save Heat Pump Installer Network spreadsheet",
                "https://www.masssave.com/-/media/Files/PDFs/Contractor-Lists/hpin-contractors.xlsx",
                AS_OF,
                "Published export linked as “Download the spreadsheet” on the Heat Pump Installer finder. File header says Revised: 10-29-2026. The finder page states participation means EPA certification, Massachusetts insurance, and heat pump installation training, and that participation is not an endorsement.",
            )],
        ))
    return listings, skipped


def maine():
    path = RAW / "eme-heat-pumps.html"
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    listings = []
    skipped = Counter()
    for item in soup.select(".results18__item"):
        name_el = item.select_one(".business-address > p")
        addr_el = item.select_one(".business-address p.small")
        if not name_el:
            skipped["no_name"] += 1
            continue
        name = name_el.get_text(strip=True)
        addr = addr_el.get_text(" ", strip=True) if addr_el else ""
        addr = addr.replace("\xa0", " ")
        match = re.search(r"^(.*?),\s*([^,]+),\s*([A-Z]{2})\s*-\s*([0-9-]+)", addr)
        street, city, region, postal = "", "", "", ""
        if match:
            street, city, region, postal = match.group(1).strip(" ,"), match.group(2).strip(), match.group(3), match.group(4)
        else:
            skipped["unparsed_address"] += 1
            continue
        phone_el = item.select_one(".tableItem__phone")
        phone = ""
        if phone_el:
            phone = clean_phone(phone_el.get_text(" ", strip=True).replace("Phone:", ""))
        website = ""
        for link in item.select("a"):
            href = link.get("href") or ""
            if href.startswith("http") and "efficiencymaine.com" not in href:
                website = clean_url(href)
                break
        services = []
        for para in item.select(".loc-service p"):
            text = para.get_text(" ", strip=True).lstrip("•").strip()
            if text:
                services.append(text)
        if "Heat Pumps" not in services and "Geothermal" not in services:
            skipped["not_heat_pump"] += 1
            continue
        if not phone and not website:
            skipped["no_contact"] += 1
            continue
        outside = region != "ME"
        listings.append(blank_listing(
            name=name,
            admin1="ME",
            city=title_place(city),
            address_region=region,
            outside_program_state=outside,
            street=street,
            postal_code=zip5(postal),
            phone=phone,
            website=website,
            services=services,
            rebate_programs=[{
                "id": "efficiency_maine_rrv_heat_pump",
                "name": "Efficiency Maine Residential Registered Vendor — heat pumps",
                "url": "https://www.efficiencymaine.com/at-home/vendor-locator/",
            }],
            sources=[source(
                "Efficiency Maine Residential Registered Vendor locator",
                "https://www.efficiencymaine.com/at-home/vendor-locator/?svc%5B%5D=4&zpc=04101&dst=10&srt=3",
                AS_OF,
                "Public locator search: service Heat Pumps, distance any, ZIP 04101 (the form requires a ZIP). Sorted by company name. The page says registered vendors are independent of Efficiency Maine and that Efficiency Maine does not endorse a provider. Email addresses shown by the locator are not republished.",
            )],
        ))
    return listings, skipped


def nys():
    payload = load_json(RAW / "nys-contractors.json")
    listings = []
    skipped = Counter()
    for row in payload["contractors"]:
        result = row["result"]
        address = result.get("address") or {}
        contact = result.get("contact") or {}
        name = (result.get("name") or "").strip()
        city = (address.get("city") or "").strip()
        region = (address.get("state") or "").strip().upper()
        phone = clean_phone(contact.get("phone"))
        website = clean_url(contact.get("website"))
        if not name or not city:
            skipped["no_name_or_city"] += 1
            continue
        if not phone and not website:
            skipped["no_contact"] += 1
            continue
        services = list(row.get("services") or [])
        loc = result.get("location") or {}
        number = (contact.get("contractorNumber") or "").strip()
        licenses = []
        if number and number.lower() != "null":
            licenses.append({"id": number, "authority": "NYS Clean Heat contractor number"})
        listings.append(blank_listing(
            name=name,
            admin1="NY",
            city=title_place(city),
            address_region=region or "NY",
            outside_program_state=region not in {"", "NY"},
            street=address.get("street") or "",
            postal_code=zip5(address.get("zip")),
            phone=phone,
            website=website,
            services=services,
            lat=loc.get("lat"),
            lng=loc.get("lng"),
            license_ids=licenses,
            extra={
                "areas_served_not_in_search_payload": True,
                "jobs_completed_last_12_months": result.get("jobsCompletedLast12Months"),
            },
            rebate_programs=[{
                "id": "nys_clean_heat",
                "name": "NYS Clean Heat participating contractor",
                "url": "https://nyscleanheat-findacontractor.icfsightline.com/",
            }],
            sources=[source(
                "NYS Clean Heat Find a Contractor",
                "https://nyscleanheat-findacontractor.icfsightline.com/",
                AS_OF,
                "Rows returned by the finder’s public /api/contractor/search for residential contractors offering ASHP Installer, AWHP Installer, GSHP Installer, or HPWH Installer. Email addresses in the API are not republished. A jobs-completed value of 0 is not shown, because the field is often zero when the finder has no count.",
            )],
        ))
        if result.get("jobsCompletedLast12Months") in (0, None, "0"):
            listings[-1]["extra"]["jobs_completed_last_12_months"] = None
    return listings, skipped


def tech(cslb_c20, cslb_c36):
    header, rows = read_xlsx_rows(RAW / "ContractorProjectData_2026-10-20.xlsx")
    idx = {name: i for i, name in enumerate(header)}
    grouped = {}
    project_rows = 0
    for row in rows:
        project_rows += 1
        name = cell(row[idx["Contractor Name"]])
        if not name:
            continue
        cslb = cell(row[idx["Contractor CSLB #"]])
        city = cell(row[idx["Contractor City"]])
        postal = zip5(row[idx["Contractor ZIP Code"]])
        key = (name.upper(), cslb, city.upper(), postal)
        rec = grouped.get(key)
        if rec is None:
            rec = grouped[key] = {
                "name": name,
                "cslb": cslb,
                "city": city,
                "zip": postal,
                "projects": 0,
                "groups": Counter(),
                "types": Counter(),
                "ducted": Counter(),
                "programs": set(),
                "latest": "",
            }
        rec["projects"] += 1
        for field, bucket in (("Product Group", "groups"), ("Product Type", "types"), ("Ducted", "ducted")):
            value = cell(row[idx[field]])
            if value:
                rec[bucket][value] += 1
        program = cell(row[idx["Program Name"]])
        if program:
            rec["programs"].add(program)
        end = cell(row[idx["Installation End Date"]])[:10]
        if end:
            rec["latest"] = max(rec["latest"], end)
    listings = []
    skipped = Counter()
    for rec in grouped.values():
        license_row = None
        license_list = None
        if rec["cslb"] and rec["cslb"] in cslb_c20:
            license_row = cslb_c20[rec["cslb"]]
            license_list = "C-20"
        elif rec["cslb"] and rec["cslb"] in cslb_c36:
            license_row = cslb_c36[rec["cslb"]]
            license_list = "C-36"
        city = rec["city"]
        if license_row and license_row["city"] and (not city or city.isdigit()):
            city = license_row["city"]
        if not city or city.isdigit():
            skipped["no_city"] += 1
            continue
        phone = license_row["phone"] if license_row else ""
        street = license_row["street"] if license_row else ""
        website = ""
        if not phone and not website:
            skipped["no_phone_after_cslb_join"] += 1
            continue
        services = []
        for group_name in rec["groups"]:
            services.append(group_name)
        for type_name in rec["types"]:
            if type_name not in services:
                services.append(type_name)
        licenses = []
        if rec["cslb"]:
            licenses.append({
                "id": rec["cslb"],
                "authority": "California CSLB",
                "classification": license_row["classification"] if license_row else "",
                "status": license_row["status"] if license_row else "",
                "list": license_list or "",
                "license_updated": license_row["updated"] if license_row else "",
            })
        sources = [source(
            "TECH Clean California ContractorProjectData_2026-10-20",
            "https://techcleanca.com/documents/5792/ContractorProjectData_2026-10-20.xlsx",
            AS_OF,
            "Public contractor project file linked from https://techcleanca.com/heat-pump-data/contractor-data/. One directory row is one contractor name + CSLB number + contractor city, aggregated from project rows. Project counts are counts of rows in that file, not a quality rating.",
        )]
        if license_row:
            sources.append(source(
                f"CSLB classification list {license_list}",
                "https://www.cslb.ca.gov/onlineservices/dataportal/ListByClassification.aspx",
                AS_OF,
                "Phone, street, and license status joined on CSLB license number from the public classification download. The full C-20 list is not published here. A C-20 license alone is not treated as evidence of heat pump work.",
            ))
        listings.append(blank_listing(
            name=rec["name"],
            admin1="CA",
            city=title_place(city),
            street=title_place(street) if street.isupper() else street,
            postal_code=rec["zip"] or (license_row["zip"] if license_row else ""),
            phone=phone,
            website=website,
            services=services,
            license_ids=licenses,
            extra={
                "tech_project_rows": rec["projects"],
                "tech_product_groups": dict(rec["groups"]),
                "tech_latest_installation_end": rec["latest"],
                "tech_programs": sorted(rec["programs"]),
                "cslb_business_type": license_row["business_type"] if license_row else "",
            },
            rebate_programs=[{
                "id": "tech_clean_california",
                "name": "TECH Clean California incentive contractor",
                "url": "https://techcleanca.com/heat-pump-data/contractor-data/",
            }],
            sources=sources,
        ))
    skipped["tech_project_rows"] = project_rows
    skipped["tech_unique_contractors"] = len(grouped)
    return listings, skipped


def minnesota():
    path = RAW / "mn-mechanical-contractor-bond.csv"
    listings = []
    skipped = Counter()
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            status = (row.get("Status") or "").strip()
            if status != "Issued":
                skipped["not_issued"] += 1
                continue
            region = (row.get("St") or "").strip().upper()
            if region != "MN":
                skipped["outside_mn"] += 1
                continue
            name = (row.get("Name") or "").strip()
            dba = (row.get("DBA_Name") or "").strip()
            city = (row.get("City") or "").strip()
            phone = clean_phone(row.get("Phone_No"))
            if not name or not city:
                skipped["no_name_or_city"] += 1
                continue
            if not phone:
                skipped["no_phone"] += 1
                continue
            display = name
            if dba and dba.upper() != name.upper():
                display = f"{name} ({dba})"
            license_number = (row.get("Lic_Number") or "").strip()
            listings.append(blank_listing(
                name=display,
                legal_name=name,
                admin1="MN",
                city=title_place(city),
                street=" ".join(part for part in [(row.get("Addr1") or "").strip(), (row.get("Addr2") or "").strip()] if part),
                postal_code=zip5(row.get("Zip")),
                phone=phone,
                heat_pump_signal="mechanical_license_only",
                services=["Minnesota DLI mechanical contractor bond (issued)"],
                license_ids=[{
                    "id": license_number,
                    "authority": "Minnesota DLI",
                    "classification": "Mechanical Contractor Bond",
                    "status": status,
                    "expires": (row.get("Exp_Date") or "").strip(),
                }],
                rebate_programs=[],
                sources=[source(
                    "Minnesota DLI Mechanical Contractor Bond export",
                    "https://secure.doli.state.mn.us/ccld/data/MNDLILicRegCertExport_Mechanical_Contractor_Bond.csv",
                    AS_OF,
                    "Public spreadsheet linked from https://dli.mn.gov/license-and-registration-lookup. Filtered to Status Issued, business state MN, and a phone number. Email addresses in the file are not republished. This is a mechanical contracting bond, not a heat-pump program roster. The listing does not claim the business installs heat pumps.",
                )],
            ))
    return listings, skipped


LABELS = {
    "unverified": "Ownership: unverified",
    "independent": "Independent",
    "pe_owned": "PE or platform-owned",
    "platform_owned": "PE or platform-owned",
    "franchise": "Franchise",
    "utility": "Utility-owned",
    "other_corporate": "Other corporate owner",
}


def ownership_label(status: str) -> str:
    return LABELS.get(status, status)


def apply_evidence(listings):
    path = DATA / "ownership" / "evidence.json"
    if not path.exists():
        return 0
    payload = load_json(path)
    by_id = {row["listing_id"]: row for row in payload.get("records", [])}
    applied = 0
    for listing in listings:
        evidence = by_id.get(listing["id"])
        if not evidence:
            continue
        status = evidence["ownership_status"]
        listing["ownership_status"] = status
        listing["ownership_label"] = ownership_label(status)
        listing["ownership_parent"] = evidence.get("parent")
        listing["ownership_source_url"] = evidence["source_url"]
        listing["ownership_source_note"] = evidence["evidence_quote"]
        listing["ownership_evidence_quote"] = evidence["evidence_quote"]
        listing["ownership_checked"] = evidence.get("checked")
        listing["ownership_matched_term"] = None
        applied += 1
    return applied


def apply_ownership(listings):
    catalog = load_json(DATA / "ownership" / "platforms.json")
    prepared = []
    for record in catalog["records"]:
        terms = [normalize_name(term) for term in record["match_terms"]]
        prepared.append((record, [term for term in terms if term]))
    matched = Counter()
    for listing in listings:
        name = normalize_name(listing.get("legal_name") or listing["name"])
        # Also try the name before a parenthetical DBA wrapper.
        candidates = [name]
        if "(" in listing["name"]:
            candidates.append(normalize_name(listing["name"].split("(", 1)[0]))
            inside = listing["name"].split("(", 1)[1].rstrip(")")
            candidates.append(normalize_name(inside))
        hit = None
        hit_term = None
        for record, terms in prepared:
            for candidate in candidates:
                for term in terms:
                    mode = record["match_mode"]
                    if mode == "exact" and candidate == term:
                        hit, hit_term = record, term
                        break
                    if mode == "prefix" and (candidate == term or candidate.startswith(term + " ")):
                        hit, hit_term = record, term
                        break
                    if mode == "phrase" and phrase_in_name(candidate, term):
                        hit, hit_term = record, term
                        break
                if hit:
                    break
            if hit:
                break
        if not hit:
            continue
        status = "pe_owned" if hit["status"] in {"platform_owned", "pe_owned"} else hit["status"]
        listing["ownership_status"] = status
        listing["ownership_label"] = ownership_label(status)
        listing["ownership_parent"] = hit["parent"]
        listing["ownership_source_url"] = hit["source_url"]
        listing["ownership_source_note"] = hit["source_note"]
        listing["ownership_matched_term"] = hit_term
        listing["ownership_backer"] = hit.get("backer")
        matched[hit["id"]] += 1
    return matched


def prettify_name(name: str) -> str:
    letters = [char for char in name if char.isalpha()]
    if not letters or not all(char.isupper() for char in letters):
        return name
    keep = {"LLC", "INC", "CO", "PC", "LLP", "PLLC", "DBA", "HVAC", "USA"}
    parts = []
    for word in name.split():
        bare = word.strip(".,()").upper()
        if bare in keep:
            parts.append(word.upper())
        else:
            parts.append(word[:1].upper() + word[1:].lower() if word else word)
    return " ".join(parts)


def assign_paths(listings):
    used = defaultdict(set)
    for listing in listings:
        state = listing["admin1"].lower()
        outside = listing.get("outside_program_state")
        if outside:
            region = (listing.get("address_region") or "xx").lower()
            city_slug = f"outside-{region}"
            city_label = f"Based outside the state ({listing['city']}, {listing.get('address_region')})"
        else:
            city_slug = slugify(listing["city"])
            city_label = listing["city"]
        base = slugify(listing["name"])
        slug = base
        n = 2
        while slug in used[(state, city_slug)]:
            slug = f"{base}-{n}"
            n += 1
        used[(state, city_slug)].add(slug)
        listing["admin1_slug"] = state
        listing["state_name"] = STATES[state]["name"]
        listing["city_slug"] = city_slug
        listing["city_label"] = city_label
        listing["slug"] = slug
        listing["id"] = f"us-{state}-{city_slug}-{slug}"
        listing["path"] = f"/us/{state}/{city_slug}/{slug}/"


def main():
    missing = [name for name in [
        "hpin-contractors.xlsx",
        "eme-heat-pumps.html",
        "nys-contractors.json",
        "ContractorProjectData_2026-10-20.xlsx",
        "cslb-c20.xlsx",
        "cslb-c36.xlsx",
        "mn-mechanical-contractor-bond.csv",
    ] if not (RAW / name).exists()]
    if missing:
        raise SystemExit(
            "Missing data/raw files: " + ", ".join(missing) + ". Run scripts/fetch_sources.py first."
        )
    c20 = load_cslb(RAW / "cslb-c20.xlsx")
    c36 = load_cslb(RAW / "cslb-c36.xlsx")
    buckets = {}
    skip_report = {}
    for key, fn in (
        ("ma", mass_save),
        ("me", maine),
        ("ny", nys),
        ("mn", minnesota),
    ):
        rows, skipped = fn()
        buckets[key] = rows
        skip_report[key] = dict(skipped)
    ca_rows, ca_skipped = tech(c20, c36)
    buckets["ca"] = ca_rows
    skip_report["ca"] = {k: int(v) for k, v in ca_skipped.items()}
    listings = []
    for key in ("ma", "me", "ny", "ca", "mn"):
        listings.extend(buckets[key])
    for listing in listings:
        if not listing.get("legal_name"):
            listing["legal_name"] = listing["name"]
        listing["name"] = prettify_name(listing["name"])
    ownership_hits = apply_ownership(listings)
    assign_paths(listings)
    evidence_applied = apply_evidence(listings)
    listings.sort(key=lambda row: (row["admin1"], row["city_label"], row["name"]))
    out = {
        "generated_from": "scripts/build_listings.py",
        "as_of": AS_OF,
        "category": "heat_pump",
        "country_code": "US",
        "count": len(listings),
        "listings": listings,
    }
    dest = DATA / "listings.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=None), encoding="utf-8")
    by_state = Counter(row["admin1"] for row in listings)
    by_own = Counter(row["ownership_status"] for row in listings)
    by_signal = Counter((row["admin1"], row["heat_pump_signal"]) for row in listings)
    stats = {
        "as_of": AS_OF,
        "count": len(listings),
        "by_state": dict(by_state),
        "by_ownership": dict(by_own),
        "ownership_hits": dict(ownership_hits),
        "evidence_applied": evidence_applied,
        "by_signal": {f"{a}:{b}": n for (a, b), n in by_signal.items()},
        "skipped": skip_report,
        "cslb_c20_rows": len(c20),
        "cslb_c36_rows": len(c36),
    }
    (DATA / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
