"""Attach cited branch groups to listings already in memory.

A group is a set of directory records whose city, ZIP, and street number
match addresses on one public page. The page URL, a quote, and the day the
page was read are required. Same name, a shared website host, and a franchise
or platform label are not join keys.

fast_mode would cluster listings by similar names. It is not implemented.
The launch configuration and the groups file must both set it to false, or
the build stops.
"""

from __future__ import annotations

import re

from common import DATA, load_json

GROUPS_PATH = DATA / "branches" / "groups.json"
FAST_MODE_ERROR = (
    "branch grouping fast_mode must be false. "
    "Fast name clustering is not implemented and is disabled at launch."
)


class BranchGroupError(ValueError):
    pass


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def street_number(value: str, label: str) -> str:
    match = re.search(r"\d+", value or "")
    if not match:
        raise BranchGroupError(f"{label} has no street number")
    return match.group(0)


def postal_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _require_fast_mode_off(site: dict, payload: dict) -> None:
    config = site.get("branch_groups") if isinstance(site, dict) else None
    if not isinstance(config, dict) or config.get("fast_mode") is not False:
        raise BranchGroupError(FAST_MODE_ERROR)
    if not isinstance(payload, dict) or payload.get("fast_mode") is not False:
        raise BranchGroupError(FAST_MODE_ERROR)


def _validate_group(group: dict, by_id: dict, seen_ids: set[str]) -> list[dict]:
    if not isinstance(group, dict):
        raise BranchGroupError("a branch group must be an object")
    group_id = group.get("id") or ""
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", group_id):
        raise BranchGroupError(f"invalid branch group id: {group_id!r}")
    for field in ("name", "scope", "source_url", "evidence_quote", "checked"):
        if not str(group.get(field) or "").strip():
            raise BranchGroupError(f"branch group {group_id} is missing {field}")
    source = group["source_url"].strip()
    if not source.startswith("https://"):
        raise BranchGroupError(f"branch group {group_id} source_url must be https")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", group["checked"].strip()):
        raise BranchGroupError(f"branch group {group_id} checked date must be YYYY-MM-DD")
    members = group.get("members")
    if not isinstance(members, list) or len(members) < 2:
        raise BranchGroupError(f"branch group {group_id} needs at least two listing ids")
    locations = []
    for member in members:
        if not isinstance(member, dict):
            raise BranchGroupError(f"branch group {group_id} has a member that is not an object")
        listing_id = member.get("listing_id") or ""
        if listing_id in seen_ids:
            raise BranchGroupError(f"listing {listing_id} is in more than one branch group")
        listing = by_id.get(listing_id)
        if listing is None:
            raise BranchGroupError(f"branch group {group_id} names unknown listing {listing_id}")
        page_city = member.get("page_city") or ""
        page_street = member.get("page_street") or ""
        page_postal = member.get("page_postal") or ""
        if compact(page_city) != compact(listing.get("city") or ""):
            raise BranchGroupError(
                f"{listing_id} city {listing.get('city')!r} does not match cited city {page_city!r}"
            )
        if postal_digits(page_postal) != postal_digits(listing.get("postal_code") or ""):
            raise BranchGroupError(
                f"{listing_id} ZIP {listing.get('postal_code')!r} does not match cited ZIP {page_postal!r}"
            )
        listed_number = street_number(listing.get("street") or "", listing_id)
        cited_number = street_number(page_street, f"{listing_id} cited street")
        if listed_number != cited_number:
            raise BranchGroupError(
                f"{listing_id} street number {listed_number} does not match cited street {page_street!r}"
            )
        seen_ids.add(listing_id)
        locations.append({
            "listing_id": listing["id"],
            "name": listing["name"],
            "city": listing["city"],
            "admin1": listing["admin1"],
            "path": listing["path"],
        })
    return locations


def attach_branch_groups(listings: list[dict], site: dict, payload: dict | None = None) -> list[dict]:
    """Mark cited branches on listing dicts. Does not change ownership fields.

    Name equality is not a join key. Listings omitted from the groups file stay
    ungrouped, including names that look alike.
    """
    if payload is None:
        payload = load_json(GROUPS_PATH)
    _require_fast_mode_off(site, payload)
    before = [
        (row.get("id"), row.get("ownership_status"), row.get("ownership_label"), row.get("ownership_parent"))
        for row in listings
    ]
    by_id = {}
    for row in listings:
        listing_id = row.get("id")
        if listing_id in by_id:
            raise BranchGroupError(f"duplicate listing id {listing_id}")
        by_id[listing_id] = row
    groups = payload.get("groups") or []
    if not isinstance(groups, list):
        raise BranchGroupError("branch groups must be a list")
    seen_ids: set[str] = set()
    prepared = []
    seen_group_ids = set()
    for group in groups:
        group_id = group.get("id") if isinstance(group, dict) else None
        if group_id in seen_group_ids:
            raise BranchGroupError(f"duplicate branch group id {group_id}")
        locations = _validate_group(group, by_id, seen_ids)
        seen_group_ids.add(group_id)
        prepared.append((group, locations))
    for row in listings:
        row.pop("_branch", None)
    for group, locations in prepared:
        info = {
            "group_id": group["id"],
            "name": group["name"].strip(),
            "listed_location_count": len(locations),
            "scope": group["scope"].strip(),
            "source_url": group["source_url"].strip(),
            "evidence_quote": group["evidence_quote"].strip(),
            "checked": group["checked"].strip(),
            "locations": locations,
        }
        for location in locations:
            by_id[location["listing_id"]]["_branch"] = info
    after = [
        (row.get("id"), row.get("ownership_status"), row.get("ownership_label"), row.get("ownership_parent"))
        for row in listings
    ]
    if before != after:
        raise BranchGroupError("branch grouping changed an ownership field")
    return listings
