"""Answer-first copy for the eight November 2026 questions.

Counts come from listing rows. Rebate dollar amounts are the figures already
quoted in this repo from official program pages checked on the data date.
This module does not invent a rebate, a roster size, or an ownership label.
"""

from __future__ import annotations

from collections import Counter

from common import ROOT, STATES, load_json

CONTENT_UPDATED = "2026-11-10"
MASS_SAVE_ASHP = (
    "https://www.masssave.com/residential/rebates-offers-services/heating-and-cooling/heat-pumps/air-source-heat-pumps"
)
MASS_SAVE_FINDER = "https://www.masssave.com/residential/find-a-contractor/find-a-heat-pump-installer"
EFFICIENCY_MAINE_REBATES = "https://www.efficiencymaine.com/at-home/residential-heat-pump-rebates/"
EFFICIENCY_MAINE_LOCATOR = "https://www.efficiencymaine.com/at-home/vendor-locator/"
MN_COMMERCE = "https://mn.gov/commerce/energy/consumer/energy-programs/heat-pump.jsp"
DEALSEAM = "https://dealseam.com/hvac-pe-rollup-tracker-2026"

_MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


def data_as_of() -> str:
    return load_json(ROOT / "config" / "site.json")["data_as_of"]


def checked_phrase(as_of: str | None = None) -> str:
    as_of = as_of or data_as_of()
    year, month, _day = as_of.split("-")
    return f"As of the {_MONTHS[int(month) - 1]} {year} ElectrifyRadar data (checked {as_of})"


def verb(count: int) -> str:
    return "is" if count == 1 else "are"


def join_clauses(items) -> str:
    items = [item for item in items if item]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]


def count_ownership(rows) -> Counter:
    return Counter(row["ownership_status"] for row in rows)


def pe_total(counts) -> int:
    return counts.get("pe_owned", 0) + counts.get("platform_owned", 0)


def platform_records():
    payload = load_json(ROOT / "data" / "ownership" / "platforms.json")
    return payload.get("records") or []


def backer_for(row, records) -> str:
    parent = row.get("ownership_parent")
    if parent:
        for record in records:
            if record.get("parent") == parent:
                return record.get("backer") or ""
    term = (row.get("ownership_matched_term") or "").strip().lower()
    if term:
        for record in records:
            terms = [(item or "").lower() for item in record.get("match_terms") or []]
            if term in terms:
                return record.get("backer") or ""
    return ""


def state_name(row) -> str:
    if row.get("state_name"):
        return row["state_name"]
    slug = row.get("admin1_slug")
    if slug in STATES:
        return STATES[slug]["name"]
    return row.get("admin1") or ""


def pe_phrase(row, records, with_state: bool = False) -> str:
    parent = row.get("ownership_parent") or "documented owner"
    backer = backer_for(row, records)
    who = f"{parent}, {backer}" if backer else parent
    place = f"{row['city']}, {state_name(row)}" if with_state else row["city"]
    return f"{row['name']} in {place} ({who})"


def ownership_sentence(counts) -> str:
    pe = pe_total(counts)
    parts = [
        f"{counts.get('unverified', 0)} labeled Ownership: unverified",
        f"{counts.get('independent', 0)} independent",
        f"{pe} PE or platform-owned",
        f"{counts.get('franchise', 0)} franchise",
    ]
    if counts.get("utility"):
        parts.append(f"{counts['utility']} utility-owned")
    if counts.get("other_corporate"):
        parts.append(f"{counts['other_corporate']} other corporate owner")
    return (
        ", ".join(parts)
        + ". These are label counts. Unverified means no documented parent was matched and no positive independent evidence was recorded."
    )


def _pe_rows(rows):
    return sorted(
        (row for row in rows if row["ownership_status"] in {"pe_owned", "platform_owned"}),
        key=lambda row: row["name"].lower(),
    )


def state_pe_lead(name: str, rows, records, program: str, file_note: str, as_of: str | None = None) -> str:
    as_of = as_of or data_as_of()
    counts = count_ownership(rows)
    pe_n = pe_total(counts)
    matched = _pe_rows(rows)
    if matched:
        named = join_clauses(pe_phrase(row, records, with_state=True) for row in matched)
        named_sentence = f"The PE or platform-owned names are {named}."
    else:
        named_sentence = "No listing in this state matched a documented private equity or platform owner."
    kind_labels = {
        "franchise": "a franchise label, not private equity",
        "utility": "a utility owner, not private equity",
        "other_corporate": "another corporate owner, not private equity",
    }
    others = sorted(
        (row for row in rows if row["ownership_status"] in kind_labels),
        key=lambda row: row["name"].lower(),
    )
    if others:
        bits = [
            f"{pe_phrase(row, records, with_state=True)}, {kind_labels[row['ownership_status']]}"
            for row in others
        ]
        other_sentence = "Other sourced owners in this state: " + join_clauses(bits) + "."
    else:
        other_sentence = "No franchise, utility, or other corporate owner was matched in this state."
    return (
        f"{checked_phrase(as_of)}, ElectrifyRadar lists {len(rows)} heat pump installer records in {name}, "
        f"of which {pe_n} {verb(pe_n)} PE or platform-owned, "
        f"from the {program} ({file_note}). "
        f"{ownership_sentence(counts)} "
        f"{named_sentence} {other_sentence} "
        "Only matched names are labeled."
    )


def how_to_tell_lead(listings, records, as_of: str | None = None) -> str:
    as_of = as_of or data_as_of()
    counts = count_ownership(listings)
    pe_n = pe_total(counts)
    matched = sorted(
        (row for row in listings if row["ownership_status"] in {"pe_owned", "platform_owned"}),
        key=lambda row: (row.get("admin1") or "", row["name"].lower()),
    )
    named = join_clauses(pe_phrase(row, records, with_state=True) for row in matched)
    return (
        f"{checked_phrase(as_of)}, {pe_n} of {len(listings)} heat pump installer records are labeled PE or platform-owned. "
        f"The matched names are {named}. "
        f"{counts.get('unverified', 0)} records are Ownership: unverified, which is not a confirmation that the company is independent. "
        "An independent label is used only when a quoted page states family ownership with a year or generation, or names the owner. "
        "To tell for one installer, open the ElectrifyRadar profile and read the ownership line and the source link."
    )


def how_to_tell_faqs(lead: str):
    return [
        (
            "Is my HVAC heat pump installer owned by private equity, and how can I tell?",
            lead,
        ),
        (
            "Does Ownership: unverified mean the company is independent?",
            "No. Ownership: unverified means no documented private equity, franchise, or other parent was matched, "
            "and no positive independent evidence was recorded. It is not a confirmation that the company is independent. "
            "Only matched names are labeled.",
        ),
        (
            "When does ElectrifyRadar use an independent label?",
            "Only when a quoted page states family ownership with a year or generation, or names the owner. "
            "Missing a private equity list is not enough. A claim form answer is not that source.",
        ),
        (
            "Where are the Massachusetts, Maine, and Minnesota lists?",
            "Massachusetts Mass Save contractors: https://electrifyradar.com/us/ma/. "
            "Maine Efficiency Maine registered vendors: https://electrifyradar.com/us/me/. "
            "Minnesota mechanical-bond directory: https://electrifyradar.com/us/mn/. "
            "Private equity matches by state start at https://electrifyradar.com/us/ma/private-equity/.",
        ),
    ]


def mass_save_network_lead(rows, records, as_of: str | None = None) -> str:
    as_of = as_of or data_as_of()
    counts = count_ownership(rows)
    pe_n = pe_total(counts)
    matched = _pe_rows(rows)
    named = join_clauses(pe_phrase(row, records, with_state=False) for row in matched)
    other = [
        row for row in rows if row["ownership_status"] == "other_corporate"
    ]
    other.sort(key=lambda row: row["name"].lower())
    if other:
        other_bits = join_clauses(
            f"{row['name']} in {row['city']} ({row.get('ownership_parent') or 'documented owner'})"
            for row in other
        )
        other_sentence = (
            f"{len(other)} {verb(len(other))} another corporate owner, not a private equity label: {other_bits}."
        )
    else:
        other_sentence = "0 are another corporate owner."
    ind = counts.get("independent", 0)
    return (
        f"{checked_phrase(as_of)}, {len(rows)} contractors are on this Mass Save Heat Pump Installer Network list, "
        f"from the public spreadsheet whose header says Revised: 10-29-2026, "
        f"of which {pe_n} {verb(pe_n)} PE or platform-owned: {named}. "
        f"{ind} {verb(ind)} independent, and that label is used only when a quoted page supports it. "
        f"{other_sentence} "
        f"{counts.get('unverified', 0)} are Ownership: unverified. "
        f"Confirm a company on {MASS_SAVE_FINDER} before you rely on a listing."
    )


def mass_save_network_faqs(lead: str, rows):
    counts = count_ownership(rows)
    pe_n = pe_total(counts)
    return [
        ("Where is the Mass Save heat pump installer network list of contractors?", lead),
        (
            "How many of those Massachusetts contractors are PE or platform-owned?",
            f"{pe_n} of {len(rows)} records are labeled PE or platform-owned. "
            f"{counts.get('unverified', 0)} are Ownership: unverified. Only matched names are labeled. "
            "The named list is https://electrifyradar.com/us/ma/private-equity/.",
        ),
        (
            "Does Ownership: unverified mean the company is independent?",
            "No. Ownership: unverified means no documented parent was matched and no positive independent evidence was recorded. "
            "An independent label is used only when a quoted page supports it.",
        ),
        (
            "Where do I confirm a contractor is still on the official Mass Save network?",
            "Search the company on the Mass Save heat pump installer finder at "
            f"{MASS_SAVE_FINDER}. ElectrifyRadar copies the public spreadsheet whose header says Revised: 10-29-2026. "
            "The program page is the record that decides approval.",
        ),
    ]


def mass_save_rebate_lead(as_of: str | None = None) -> str:
    as_of = as_of or data_as_of()
    return (
        f"{checked_phrase(as_of)}, the Mass Save air-source heat pump page lists a 2026 whole-home rebate of "
        "$2,650 per ton up to $8,500 and a partial-home rebate of $1,125 per ton up to $8,500. "
        "A basic rebate is $250 per ton up to $2,500. Income-based enhanced incentives go up to $16,000. "
        "Equipment must be ENERGY STAR Cold Climate and on the Mass Save qualified products list, "
        "and it must be installed by a Heat Pump Installer Network contractor. "
        f"Re-check {MASS_SAVE_ASHP} before you sign."
    )


def mass_save_rebate_faqs(lead: str, as_of: str | None = None):
    as_of = as_of or data_as_of()
    return [
        (
            "What is the Mass Save heat pump rebate in 2026 for whole-home versus partial-home?",
            lead,
        ),
        (
            "Do I need insulation done first?",
            "For the whole-home rebate, Mass Save requires the home to be sufficiently weatherized and a "
            "Whole-Home Heat Pump Verification Form to be completed and signed. Sufficient weatherization can be shown by "
            "at least one of: the home was built during or after 2000; a Home Energy Assessment report recommends less than "
            "$1,000 of weatherization; or weatherization recommendations made during or after 2013 have been completed. "
            "Heat pumps that do not meet that weatherization rule may still be eligible for partial-home amounts. "
            "Partial-home projects can earn a $500 weatherization bonus when assessment and recommended weatherization fall "
            f"in the window Mass Save publishes. Details are on {MASS_SAVE_ASHP}. Page checked {as_of}.",
        ),
        (
            "Does my installer have to be on the Heat Pump Installer Network?",
            "Yes for these Mass Save air-source heat pump rebates. The program page states that equipment must be installed "
            "by a contractor participating in the Mass Save Heat Pump Installer Network. The ElectrifyRadar Massachusetts list "
            f"is built from that public network file (header Revised: 10-29-2026, checked {as_of}): "
            "https://electrifyradar.com/us/ma/. Confirm the company on "
            f"{MASS_SAVE_FINDER} before you rely on a listing.",
        ),
        (
            "Where do I check if my model is on the qualified products list?",
            "Mass Save requires ENERGY STAR Cold Climate equipment and points to the Mass Save Heat Pump Qualified Products List from "
            f"{MASS_SAVE_ASHP}. Ask every bidder to write the exact outdoor and indoor model numbers and the AHRI reference number "
            "on the quote, then match those to the list yourself.",
        ),
        (
            "How does the Mass Save HEAT loan relate to the rebate?",
            "The rebate and the HEAT loan are separate paths. Mass Save program materials point homeowners to the HEAT loan portal at "
            "https://www.myheatloan.com/ for financing questions. Loan eligibility, rates, and whether a project can combine both change. "
            "Treat the portal and your HPIN contractor as the source of truth. This page is not lending advice.",
        ),
    ]


def efficiency_maine_lead(as_of: str | None = None) -> str:
    as_of = as_of or data_as_of()
    return (
        f"{checked_phrase(as_of)}, the Efficiency Maine residential heat pump rebates page lists per outdoor unit amounts of "
        "$3,000 for low income (lifetime cap $9,000 per housing unit), $2,000 for moderate income (cap $6,000), "
        "and $1,000 for any income (cap $3,000). Multi-zone outdoor units are not rebate-eligible on that table. "
        "Single-zone units on the Efficiency Maine list are rebate-eligible. "
        f"Read the official table at {EFFICIENCY_MAINE_REBATES} before you apply."
    )


def efficiency_maine_faqs(lead: str, as_of: str | None = None):
    as_of = as_of or data_as_of()
    return [
        ("What is the Efficiency Maine heat pump rebate amount in 2026?", lead),
        (
            "Who must install the system for the rebate?",
            "The Efficiency Maine residential heat pump rebate page states the system must be installed by an Efficiency Maine "
            f"Residential Registered Vendor for heat pumps. The ElectrifyRadar Maine directory (https://electrifyradar.com/us/me/) "
            f"is built from that locator, checked {as_of}. Confirm the vendor on {EFFICIENCY_MAINE_LOCATOR}.",
        ),
        (
            "Do multi-zone systems qualify?",
            f"On the eligibility table Efficiency Maine published (checked {as_of}), multi-zone heat pumps are not rebate-eligible, "
            "though their design-temperature heating capacity can still count toward total heating capacity of all heat pumps. "
            "Single-zone units on the Efficiency Maine list are rebate-eligible. Dual-fuel heat pump / furnace packages are not "
            "rebate-eligible and their capacity does not count. "
            f"Re-read {EFFICIENCY_MAINE_REBATES} before you buy.",
        ),
        (
            "What does primary heating system mean if I keep oil or propane?",
            "The rebate page requires heat pumps to be used as the primary heating system throughout the heating season. "
            "For existing construction, any furnace or boiler must be reserved for emergency backup only, for example by turning "
            "thermostats all the way down, covering the power switch, or connecting the fossil system only to a generator. "
            "Primary systems can back you up in an emergency, but their heating capacity cannot be counted toward the 100% sizing requirement. "
            f"New construction rules tighten further on 1 January 2027 (no furnace or boiler). Page checked {as_of}.",
        ),
        (
            "How long do I have to submit the claim?",
            f"Efficiency Maine says the rebate claim form must be emailed or postmarked within six months of project completion (page checked {as_of}). "
            "Incomplete information can delay or disqualify the rebate.",
        ),
        (
            "Where is the list of Efficiency Maine registered heat pump vendors?",
            "The ElectrifyRadar Maine list is https://electrifyradar.com/us/me/. City pages include Portland "
            "(https://electrifyradar.com/us/me/portland/), Bangor (https://electrifyradar.com/us/me/bangor/), "
            "Augusta (https://electrifyradar.com/us/me/augusta/), and Brunswick (https://electrifyradar.com/us/me/brunswick/). "
            f"Confirm each company on {EFFICIENCY_MAINE_LOCATOR}. "
            "Names matched to a private equity platform are listed at https://electrifyradar.com/us/me/private-equity/.",
        ),
    ]


def questions_lead(total: int, states: int, as_of: str | None = None) -> str:
    as_of = as_of or data_as_of()
    return (
        f"{checked_phrase(as_of)}, ask every heat pump installer the same questions before getting quotes. "
        f"ElectrifyRadar lists {total} installer records across {states} states. "
        "A directory listing, a familiar brand, or a low headline price does not answer how the system will be sized, "
        "what the written scope includes, which rebate program applies, or who owns the company. "
        "Ask each bidder to explain the sizing method and to put the same scope in writing, "
        "then confirm any rebate on the official program page."
    )


def questions_faqs(lead: str):
    return [
        ("What questions should I ask a heat pump installer before getting quotes?", lead),
        (
            "What should the written scope include?",
            "Ask each bidder for indoor and outdoor model numbers, the sizing basis, intended heating coverage, "
            "duct work or indoor-unit placement, electrical work, what happens to the existing heat, who pulls permits, "
            "warranty and service terms, and the schedule and price. Ask them to mark items that do not apply. "
            "ENERGY STAR recommends written, itemized estimates and a written proposal covering costs, model numbers, schedule, and warranty information.",
        ),
        (
            "How should I treat a rebate amount written into a quote?",
            "Ask which program the incentive refers to, which equipment and contractor rules apply, whether approval is needed before the work, "
            "and who submits the documents. Verify the answer on the current program page. A contractor estimate is not a guarantee of a rebate. "
            "This guide does not establish eligibility.",
        ),
        (
            "Where do I read who owns the installer before I compare quotes?",
            "Open the ElectrifyRadar profile and read the ownership line and its source link. "
            "An independent label is used only when a quoted page supports it. Ownership: unverified is not a confirmation of independent ownership. "
            "Ownership is context, not a workmanship score. Compare the written proposals either way. "
            "The ownership guide is https://electrifyradar.com/us/guides/independent-vs-pe-hvac/.",
        ),
    ]


def maine_vendor_lead(rows, records, as_of: str | None = None) -> str:
    as_of = as_of or data_as_of()
    counts = count_ownership(rows)
    pe_n = pe_total(counts)
    franchises = sorted(
        (row for row in rows if row["ownership_status"] == "franchise"),
        key=lambda row: row["name"].lower(),
    )
    if len(franchises) == 1:
        franchise_sentence = (
            f"1 is a franchise ({franchises[0]['name']}), which is not a private equity label."
        )
    elif franchises:
        names = join_clauses(row["name"] for row in franchises)
        franchise_sentence = (
            f"{len(franchises)} are franchises: {names}. Franchise is not a private equity label."
        )
    else:
        franchise_sentence = "0 are franchises."
    ind = counts.get("independent", 0)
    return (
        f"{checked_phrase(as_of)}, {len(rows)} installers in Maine are Efficiency Maine Residential Registered Vendors "
        f"with the Heat Pumps service, of which {pe_n} {verb(pe_n)} PE or platform-owned. "
        f"{franchise_sentence} "
        f"{ind} {verb(ind)} independent, and that label is used only when a quoted page supports it. "
        f"{counts.get('unverified', 0)} are Ownership: unverified. "
        "The Efficiency Maine residential heat pump rebates page, checked "
        f"{as_of}, lists per outdoor-unit amounts of $3,000 (low income, lifetime cap $9,000), "
        "$2,000 (moderate income, cap $6,000), and $1,000 (any income, cap $3,000). "
        "Multi-zone units are not rebate-eligible on that table. Only matched names are labeled."
    )


def maine_vendor_faqs(lead: str, rows):
    counts = count_ownership(rows)
    pe_n = pe_total(counts)
    return [
        (
            "Where is the list of heat pump installers in Maine that are Efficiency Maine registered vendors?",
            lead,
        ),
        (
            "How many of those Maine listings are owned by private equity platforms?",
            f"{pe_n} of {len(rows)} Maine records are labeled PE or platform-owned. "
            f"{counts.get('unverified', 0)} are Ownership: unverified and {counts.get('independent', 0)} are independent. "
            "Only matched names are labeled. The named list is https://electrifyradar.com/us/me/private-equity/.",
        ),
        (
            "What are the Efficiency Maine residential heat pump rebate amounts?",
            "The Efficiency Maine residential heat pump rebates page, checked "
            f"{data_as_of()}, lists per outdoor-unit amounts of $3,000 (low income, lifetime cap $9,000), "
            "$2,000 (moderate income, cap $6,000), and $1,000 (any income, cap $3,000). "
            "Multi-zone units are not rebate-eligible on that table. "
            f"Confirm the current table at {EFFICIENCY_MAINE_REBATES} before you apply. "
            "The longer walkthrough is https://electrifyradar.com/us/guides/efficiency-maine-heat-pump-rebate/.",
        ),
        (
            "What does Ownership: unverified mean on the Maine page?",
            "Ownership: unverified means no documented parent was matched and no positive independent evidence was recorded. "
            "It is not a confirmation that the company is independent. Only matched names are labeled.",
        ),
    ]


def minnesota_lead(rows, records, as_of: str | None = None) -> str:
    as_of = as_of or data_as_of()
    counts = count_ownership(rows)
    pe_n = pe_total(counts)
    matched = _pe_rows(rows)
    if matched:
        named = join_clauses(pe_phrase(row, records, with_state=False) for row in matched)
        pe_sentence = f"of which {pe_n} {verb(pe_n)} PE or platform-owned: {named}."
    else:
        pe_sentence = f"of which {pe_n} {verb(pe_n)} PE or platform-owned."
    franchises = sorted(
        (row["name"] for row in rows if row["ownership_status"] == "franchise"),
        key=str.lower,
    )
    if franchises:
        franchise_sentence = (
            f"{len(franchises)} are franchises: {join_clauses(franchises)}. Franchise is not a private equity label."
        )
    else:
        franchise_sentence = "0 are franchises."
    ind = counts.get("independent", 0)
    return (
        f"{checked_phrase(as_of)}, {len(rows)} businesses are listed in this Minnesota directory, {pe_sentence} "
        f"{franchise_sentence} "
        f"{ind} {verb(ind)} independent, and that label is used only when a quoted page supports it. "
        f"{counts.get('unverified', 0)} are Ownership: unverified. "
        "These rows are issued Mechanical Contractor Bond holders from the Minnesota Department of Labor and Industry public export. "
        "This is not a cold-climate heat pump program roster, and the file does not say that each business installs heat pumps. "
        f"The Minnesota Commerce residential heat pump rebate page, checked {as_of}, includes a status update dated 12 October 2026: "
        "the state rebate had not launched, and the approved contractor list was not published. "
        "That page says an eligible heat pump for the future rebate means an ENERGY STAR certified, cold-climate rated air-source heat pump, "
        "and that the rebate amount will be the lesser of $4,000 or the total cost to purchase and install the heat pump minus other rebates. "
        f"Read {MN_COMMERCE} before you rely on a rebate."
    )


def minnesota_faqs(lead: str, rows):
    counts = count_ownership(rows)
    pe_n = pe_total(counts)
    return [
        ("Where is a directory of cold climate heat pump installers in Minnesota?", lead),
        (
            "Is this Minnesota list a cold-climate heat pump program roster?",
            f"No. The {len(rows)} names are businesses with an issued Mechanical Contractor Bond, a Minnesota address, and a phone number "
            f"in the Minnesota Department of Labor and Industry public export, checked {data_as_of()}. "
            "That file does not say each business installs heat pumps. "
            "The Minnesota Commerce page said the approved contractor list for the state heat pump rebate was not published yet.",
        ),
        (
            "How many of these Minnesota businesses are PE or platform-owned?",
            f"{pe_n} of {len(rows)} records are labeled PE or platform-owned. "
            f"{counts.get('franchise', 0)} are franchises, which is not a private equity label. "
            f"{counts.get('unverified', 0)} are Ownership: unverified. Only matched names are labeled. "
            "The named list is https://electrifyradar.com/us/mn/private-equity/.",
        ),
        (
            "What cold-climate rebate figure does the Minnesota Commerce page state?",
            "The Minnesota Commerce residential heat pump rebate page, checked "
            f"{data_as_of()}, includes a status update dated 12 October 2026: the state rebate had not launched. "
            "The same page says the rebate amount will be the lesser of $4,000 or the install cost minus other rebates, "
            "for an ENERGY STAR certified, cold-climate rated air-source heat pump, and that the approved contractor list was not published yet. "
            f"Read {MN_COMMERCE}.",
        ),
    ]


def answer_link_pairs():
    """Visible question titles and canonical paths, in question order."""
    return [
        ("Is my HVAC heat pump installer owned by private equity: how to tell", "/us/guides/independent-vs-pe-hvac/"),
        ("Mass Save heat pump installer network list of contractors", "/us/ma/"),
        ("Efficiency Maine heat pump rebate 2026 amount", "/us/guides/efficiency-maine-heat-pump-rebate/"),
        ("Questions to ask a heat pump installer before getting quotes", "/us/guides/questions-to-ask-heat-pump-installer/"),
        ("Mass Save heat pump rebate 2026 whole-home vs partial amount", "/us/guides/mass-save-heat-pump-rebate/"),
        ("List of heat pump installers in Maine Efficiency Maine registered vendors", "/us/me/"),
        ("Which HVAC companies in Massachusetts are owned by private equity platforms", "/us/ma/private-equity/"),
        ("Cold climate heat pump installers Minnesota directory", "/us/mn/"),
    ]


def answer_catalog(listings, records=None):
    """Titles, paths, leads, and official sources for the eight answer pages."""
    records = records if records is not None else platform_records()
    by_slug = {}
    for row in listings:
        by_slug.setdefault(row["admin1_slug"], []).append(row)
    ma = by_slug.get("ma", [])
    me = by_slug.get("me", [])
    mn = by_slug.get("mn", [])
    return [
        {
            "id": "ER-1",
            "title": "Is my HVAC heat pump installer owned by private equity: how to tell",
            "path": "/us/guides/independent-vs-pe-hvac/",
            "lead": how_to_tell_lead(listings, records),
            "source": DEALSEAM,
        },
        {
            "id": "ER-2",
            "title": "Mass Save heat pump installer network list of contractors",
            "path": "/us/ma/",
            "lead": mass_save_network_lead(ma, records),
            "source": MASS_SAVE_FINDER,
        },
        {
            "id": "ER-3",
            "title": "Efficiency Maine heat pump rebate 2026 amount",
            "path": "/us/guides/efficiency-maine-heat-pump-rebate/",
            "lead": efficiency_maine_lead(),
            "source": EFFICIENCY_MAINE_REBATES,
        },
        {
            "id": "ER-4",
            "title": "Questions to ask a heat pump installer before getting quotes",
            "path": "/us/guides/questions-to-ask-heat-pump-installer/",
            "lead": questions_lead(len(listings), len(STATES)),
            "source": "https://www.energystar.gov/saveathome/heating-cooling/10-tips-hiring",
        },
        {
            "id": "ER-5",
            "title": "Mass Save heat pump rebate 2026 whole-home vs partial amount",
            "path": "/us/guides/mass-save-heat-pump-rebate/",
            "lead": mass_save_rebate_lead(),
            "source": MASS_SAVE_ASHP,
        },
        {
            "id": "ER-6",
            "title": "List of heat pump installers in Maine Efficiency Maine registered vendors",
            "path": "/us/me/",
            "lead": maine_vendor_lead(me, records),
            "source": EFFICIENCY_MAINE_LOCATOR,
        },
        {
            "id": "ER-7",
            "title": "Which HVAC companies in Massachusetts are owned by private equity platforms",
            "path": "/us/ma/private-equity/",
            "lead": state_pe_lead(
                "Massachusetts",
                ma,
                records,
                "Mass Save Heat Pump Installer Network",
                "the public spreadsheet whose header says Revised: 10-29-2026",
            ),
            "source": DEALSEAM,
        },
        {
            "id": "ER-8",
            "title": "Cold climate heat pump installers Minnesota directory",
            "path": "/us/mn/",
            "lead": minnesota_lead(mn, records),
            "source": MN_COMMERCE,
        },
    ]
