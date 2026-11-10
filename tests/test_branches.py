"""Branch groups stay cited, small, and independent of ownership labels."""

from __future__ import annotations

import copy
import json
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from branches import FAST_MODE_ERROR, BranchGroupError, attach_branch_groups  # noqa: E402

DIST = ROOT / "dist"
DAVES_WORLD = [
    "us-me-augusta-dave-s-world-augusta",
    "us-me-dover-foxcroft-dave-s-world-dover-foxcroft",
    "us-me-edgecomb-dave-s-world-edgecomb",
    "us-me-ellsworth-dave-s-world-ellsworth",
    "us-me-presque-isle-dave-s-world-presque-isle",
    "us-me-scarborough-dave-s-world-scarborough",
    "us-me-windham-dave-s-world-windham",
]
SIMILAR_NOT_GROUPED = [
    "us-me-milford-dave-s-mechanical-maintenance-inc",
    "us-me-winthrop-dave-s-heat-pumps-dave-s-appliance-inc",
    "us-me-westbrook-dave-perry-electric",
    "us-ct-new-milford-daves-heating-and-air",
    "us-ct-southington-dave-s-hvac-llc",
    "us-ma-outside-nh-dave-s-ductless-hvac-dave-the-plumber-llc",
]
AIRE_SERV = [
    "us-ca-arcadia-aire-serv-of-pasadena-dba-cool-and-clean-refrigeration-resolv",
    "us-ct-east-windsor-aire-serv-of-north-central-ct",
    "us-me-hollis-center-aire-serv-of-southern-maine",
    "us-mn-cloquet-b-d-total-temp-llc-aire-serv-of-northeastern-minnesota",
    "us-mn-eden-prairie-fas-heating-and-cooling-llc-aire-serv-of-the-south-metro",
    "us-mn-lake-elmo-bosch-works-llc-aire-serv-of-east-metro",
    "us-mn-north-branch-hpmd-enterprises-inc-aire-serv-of-east-central-minnesota",
]


def load_rows():
    return json.loads((ROOT / "data" / "listings.json").read_text(encoding="utf-8"))["listings"]


def site_config():
    return json.loads((ROOT / "config" / "site.json").read_text(encoding="utf-8"))


def groups_payload():
    return json.loads((ROOT / "data" / "branches" / "groups.json").read_text(encoding="utf-8"))


def fake_row(listing_id, status, city, street, postal, name):
    slug = city.lower().replace(" ", "-")
    return {
        "id": listing_id,
        "name": name,
        "city": city,
        "admin1": "ME",
        "street": street,
        "postal_code": postal,
        "path": f"/us/me/{slug}/{listing_id}/",
        "ownership_status": status,
        "ownership_label": status,
        "ownership_parent": "Example Franchise" if status == "franchise" else None,
    }


class BranchGroupDataTest(unittest.TestCase):
    def test_fast_mode_is_explicitly_false(self):
        site = site_config()
        payload = groups_payload()
        self.assertIn("branch_groups", site)
        self.assertIs(site["branch_groups"]["fast_mode"], False)
        self.assertIs(payload["fast_mode"], False)
        self.assertEqual(payload["groups"][0]["id"], "daves-world")
        self.assertEqual(
            payload["groups"][0]["evidence_quote"],
            "Proudly Serving All of Maine Out of Our 7 Locations",
        )
        self.assertEqual(payload["groups"][0]["source_url"], "https://www.davesworld.com/locations")
        self.assertEqual(payload["groups"][0]["checked"], "2026-11-07")

    def test_launch_groups_only_the_cited_daves_world_records(self):
        rows = copy.deepcopy(load_rows())
        before = Counter(row["ownership_status"] for row in rows)
        attach_branch_groups(rows, site_config())
        after = Counter(row["ownership_status"] for row in rows)
        self.assertEqual(before, after)
        grouped = [row for row in rows if row.get("_branch")]
        self.assertEqual({row["id"] for row in grouped}, set(DAVES_WORLD))
        for row in grouped:
            self.assertEqual(row["ownership_status"], "unverified")
            self.assertEqual(row["ownership_label"], "Ownership: unverified")
            self.assertIsNone(row["ownership_parent"])
            info = row["_branch"]
            self.assertEqual(info["listed_location_count"], 7)
            self.assertEqual(info["group_id"], "daves-world")
            self.assertIn("not a separate census", info["scope"].lower())
            self.assertEqual(len(info["locations"]), 7)
        by_id = {row["id"]: row for row in rows}
        for listing_id in SIMILAR_NOT_GROUPED:
            self.assertNotIn("_branch", by_id[listing_id])
            self.assertEqual(by_id[listing_id]["ownership_status"], "unverified")
        for listing_id in AIRE_SERV:
            self.assertNotIn("_branch", by_id[listing_id])
            self.assertEqual(by_id[listing_id]["ownership_status"], "franchise")
        comfort = [row for row in rows if row["name"].lower().startswith("comfort zone")]
        self.assertGreaterEqual(len(comfort), 3)
        self.assertTrue(all("_branch" not in row for row in comfort))

    def test_published_ownership_counts_are_unchanged_on_disk(self):
        payload = json.loads((ROOT / "data" / "listings.json").read_text(encoding="utf-8"))
        rows = payload["listings"]
        self.assertEqual(payload["count"], 7243)
        self.assertEqual(Counter(row["admin1"] for row in rows)["ME"], 590)
        self.assertEqual(
            Counter(row["ownership_status"] for row in rows),
            {
                "unverified": 7155,
                "independent": 76,
                "franchise": 7,
                "pe_owned": 4,
                "other_corporate": 1,
            },
        )
        maine = [row for row in rows if row["admin1"] == "ME"]
        self.assertEqual(
            Counter(row["ownership_status"] for row in maine),
            {"unverified": 584, "independent": 5, "franchise": 1},
        )
        stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
        self.assertEqual(stats["count"], 7243)
        self.assertEqual(stats["by_state"]["ME"], 590)
        self.assertEqual(stats["by_ownership"]["unverified"], 7155)
        self.assertEqual(stats["by_ownership"]["independent"], 76)
        self.assertEqual(stats["by_ownership"]["franchise"], 7)

    def test_fast_mode_raises_and_does_not_cluster_similar_names(self):
        rows = [
            fake_row("a", "unverified", "Augusta", "1 Main St", "04330", "Northwind Comfort"),
            fake_row("b", "unverified", "Bangor", "2 Main St", "04401", "Northwind Comfort"),
            fake_row("c", "independent", "Bath", "3 Main St", "04530", "Northwind Comfort LLC"),
        ]
        payload = {
            "fast_mode": True,
            "groups": [],
        }
        site = {"branch_groups": {"fast_mode": True}}
        with self.assertRaises(BranchGroupError) as caught:
            attach_branch_groups(rows, site, payload)
        self.assertIn(FAST_MODE_ERROR, str(caught.exception))
        self.assertTrue(all("_branch" not in row for row in rows))
        self.assertEqual([row["ownership_status"] for row in rows], ["unverified", "unverified", "independent"])

    def test_missing_fast_mode_flag_is_rejected(self):
        rows = [fake_row("a", "unverified", "Augusta", "1 Main St", "04330", "Northwind Comfort")]
        with self.assertRaises(BranchGroupError):
            attach_branch_groups(rows, {}, {"fast_mode": False, "groups": []})
        with self.assertRaises(BranchGroupError):
            attach_branch_groups(rows, {"branch_groups": {"fast_mode": False}}, {"groups": []})

    def test_label_independence_and_similar_name_left_out(self):
        rows = [
            fake_row("north-a", "independent", "Augusta", "10 Water St", "04330", "Northwind Comfort"),
            fake_row("north-b", "franchise", "Bangor", "20 Water St", "04401", "Northwind Comfort"),
            fake_row("north-c", "unverified", "Bath", "30 Water St", "04530", "Northwind Comfort Services"),
        ]
        payload = {
            "fast_mode": False,
            "groups": [{
                "id": "northwind",
                "name": "Northwind Comfort",
                "source_url": "https://example.com/locations",
                "evidence_quote": "Our two shops are listed here.",
                "checked": "2026-11-07",
                "scope": "Two cited addresses only.",
                "members": [
                    {"listing_id": "north-a", "page_city": "Augusta", "page_street": "10 Water Street", "page_postal": "04330"},
                    {"listing_id": "north-b", "page_city": "Bangor", "page_street": "20 Water Street", "page_postal": "04401"},
                ],
            }],
        }
        attach_branch_groups(rows, {"branch_groups": {"fast_mode": False}}, payload)
        self.assertEqual(rows[0]["ownership_status"], "independent")
        self.assertIsNone(rows[0]["ownership_parent"])
        self.assertEqual(rows[1]["ownership_status"], "franchise")
        self.assertEqual(rows[1]["ownership_parent"], "Example Franchise")
        self.assertEqual(rows[0]["_branch"]["listed_location_count"], 2)
        self.assertEqual(rows[1]["_branch"]["listed_location_count"], 2)
        self.assertNotIn("_branch", rows[2])
        self.assertEqual(rows[2]["ownership_status"], "unverified")

    def test_address_mismatch_and_unknown_id_are_rejected(self):
        rows = [
            fake_row("north-a", "unverified", "Augusta", "10 Water St", "04330", "Northwind Comfort"),
            fake_row("north-b", "unverified", "Bangor", "20 Water St", "04401", "Northwind Comfort"),
        ]
        payload = {
            "fast_mode": False,
            "groups": [{
                "id": "northwind",
                "name": "Northwind Comfort",
                "source_url": "https://example.com/locations",
                "evidence_quote": "Our two shops are listed here.",
                "checked": "2026-11-07",
                "scope": "Two cited addresses only.",
                "members": [
                    {"listing_id": "north-a", "page_city": "Augusta", "page_street": "10 Water Street", "page_postal": "99999"},
                    {"listing_id": "north-b", "page_city": "Bangor", "page_street": "20 Water Street", "page_postal": "04401"},
                ],
            }],
        }
        site = {"branch_groups": {"fast_mode": False}}
        with self.assertRaises(BranchGroupError):
            attach_branch_groups(copy.deepcopy(rows), site, payload)
        payload["groups"][0]["members"][0]["page_postal"] = "04330"
        payload["groups"][0]["members"].append({
            "listing_id": "missing-shop",
            "page_city": "Bath",
            "page_street": "1 Main St",
            "page_postal": "04530",
        })
        with self.assertRaises(BranchGroupError):
            attach_branch_groups(copy.deepcopy(rows), site, payload)
        self.assertTrue(all("_branch" not in row for row in rows))


class BranchGroupSiteTest(unittest.TestCase):
    def test_profiles_keep_urls_and_separate_location_copy_from_ownership(self):
        self.assertTrue((DIST / "index.html").exists(), "run python3 scripts/build_site.py")
        augusta = (DIST / "us/me/augusta/dave-s-world-augusta/index.html").read_text(encoding="utf-8")
        self.assertIn(
            'rel="canonical" href="https://electrifyradar.com/us/me/augusta/dave-s-world-augusta/"',
            augusta,
        )
        self.assertIn('class="badge quiet">Ownership: unverified</span>', augusta)
        self.assertIn('class="badge locations">7 listed locations</span>', augusta)
        self.assertIn('id="listed-locations"', augusta)
        self.assertIn("https://www.davesworld.com/locations", augusta)
        self.assertIn("Proudly Serving All of Maine Out of Our 7 Locations", augusta)
        self.assertIn("not an exhaustive national total", augusta)
        self.assertIn("not an ownership label", augusta)
        note = re.search(r'<div class="note"><p>(.*?)</p></div>', augusta, re.S).group(1)
        self.assertIn("Ownership: unverified", note)
        self.assertNotIn("listed locations", note.lower())
        section = re.search(r'<section id="listed-locations".*?</section>', augusta, re.S).group(0)
        hrefs = re.findall(r'href="([^"]+)"', section)
        self.assertEqual(hrefs[0], "https://www.davesworld.com/locations")
        page = DIST / "us/me/augusta/dave-s-world-augusta/index.html"
        sibling_slugs = [
            "dave-s-world-dover-foxcroft/",
            "dave-s-world-edgecomb/",
            "dave-s-world-ellsworth/",
            "dave-s-world-presque-isle/",
            "dave-s-world-scarborough/",
            "dave-s-world-windham/",
        ]
        self.assertEqual(len(hrefs), 1 + len(sibling_slugs))
        for href, slug in zip(hrefs[1:], sibling_slugs):
            self.assertIn(slug, href)
            target = (page.parent / href).resolve()
            if target.is_dir():
                target = target / "index.html"
            self.assertTrue(target.exists(), href)
        self.assertNotIn("parentOrganization", augusta)
        self.assertNotIn("branchOf", augusta)
        mechanical = (DIST / "us/me/milford/dave-s-mechanical-maintenance-inc/index.html").read_text(encoding="utf-8")
        self.assertIn("Ownership: unverified", mechanical)
        self.assertNotIn("listed-locations", mechanical)
        self.assertNotIn("listed locations", mechanical.lower())
        aire = (DIST / "us/me/hollis-center/aire-serv-of-southern-maine/index.html").read_text(encoding="utf-8")
        self.assertIn('class="badge franchise">Franchise</span>', aire)
        self.assertNotIn("listed-locations", aire)
        self.assertNotIn("7 listed locations", aire)

    def test_directories_link_branches_without_changing_ownership_counts(self):
        maine = (DIST / "us/me/index.html").read_text(encoding="utf-8")
        quick = re.search(r'<p class="quick-answer">(.*?)</p>', maine, re.S).group(1)
        self.assertIn("590", quick)
        self.assertIn("584 are Ownership: unverified", quick)
        self.assertIn("5 are independent", quick)
        self.assertIn("0 are PE or platform-owned", quick)
        self.assertIn("1 is a franchise", quick)
        self.assertNotIn("listed location", quick.lower())
        self.assertIn("not an exhaustive national total", maine)
        city = (DIST / "us/me/augusta/index.html").read_text(encoding="utf-8")
        self.assertIn('data-ownership="unverified"', city)
        self.assertIn("dave-s-world-dover-foxcroft/", city)
        self.assertIn("7 listed locations", city)
        self.assertIn("Not an ownership label", city)
        self.assertNotIn("dave-s-mechanical-maintenance-inc", city)
        milford = (DIST / "us/me/milford/index.html").read_text(encoding="utf-8")
        self.assertNotIn("listed locations", milford.lower())
        index = json.loads((DIST / "search-index.json").read_text(encoding="utf-8"))
        dave_rows = [row for row in index if row["p"].endswith("dave-s-world-augusta/")]
        self.assertEqual(len(dave_rows), 1)
        self.assertEqual(dave_rows[0]["o"], "unverified")
        self.assertEqual(dave_rows[0]["lc"], 7)
        self.assertEqual(len(dave_rows[0]["br"]), 6)
        mechanical_rows = [row for row in index if "dave-s-mechanical-maintenance-inc" in row["p"]]
        self.assertEqual(mechanical_rows[0]["lc"], 0)
        self.assertNotIn("br", mechanical_rows[0])
        aire_rows = [row for row in index if "aire-serv-of-southern-maine" in row["p"]]
        self.assertEqual(aire_rows[0]["o"], "franchise")
        self.assertEqual(aire_rows[0]["lc"], 0)

    def test_sitemap_keeps_profiles_and_thin_city_rules(self):
        installers = (DIST / "sitemap-installers.xml").read_text(encoding="utf-8")
        cities = (DIST / "sitemap-cities.xml").read_text(encoding="utf-8")
        for slug in (
            "augusta/dave-s-world-augusta",
            "dover-foxcroft/dave-s-world-dover-foxcroft",
            "edgecomb/dave-s-world-edgecomb",
            "ellsworth/dave-s-world-ellsworth",
            "presque-isle/dave-s-world-presque-isle",
            "scarborough/dave-s-world-scarborough",
            "windham/dave-s-world-windham",
        ):
            self.assertIn(f"https://electrifyradar.com/us/me/{slug}/", installers)
        self.assertNotIn("https://electrifyradar.com/us/me/edgecomb/", cities)
        edgecomb_city = (DIST / "us/me/edgecomb/index.html").read_text(encoding="utf-8")
        self.assertIn('content="noindex, follow"', edgecomb_city)
        edgecomb_profile = (DIST / "us/me/edgecomb/dave-s-world-edgecomb/index.html").read_text(encoding="utf-8")
        self.assertNotIn('content="noindex', edgecomb_profile)
        self.assertIn('id="listed-locations"', edgecomb_profile)
        method = (DIST / "methodology/index.html").read_text(encoding="utf-8")
        self.assertIn("branch_groups.fast_mode", method)
        self.assertIn("Proudly Serving All of Maine Out of Our 7 Locations", method)
        self.assertIn("Ownership: unverified", method)
        guide = (DIST / "us/guides/how-we-label-ownership/index.html").read_text(encoding="utf-8")
        self.assertIn("listed-location count is separate", guide)
        compare = (DIST / "us/guides/independent-vs-pe-hvac/index.html").read_text(encoding="utf-8")
        self.assertIn("Listed locations", compare)
        self.assertIn("Not an ownership label", compare)


if __name__ == "__main__":
    unittest.main()
