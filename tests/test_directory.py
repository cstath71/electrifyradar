"""Checks that listings stay sourced and the built site links to itself."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
FORBIDDEN = ("PrimeLogic", "Stathopoulos", "Constantin", "Switzerland")


class ListingsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads((ROOT / "data" / "listings.json").read_text(encoding="utf-8"))
        cls.rows = cls.payload["listings"]

    def test_launch_states_are_populated(self):
        counts = {}
        for row in self.rows:
            counts[row["admin1"]] = counts.get(row["admin1"], 0) + 1
        for code in ("MA", "ME", "NY", "CA", "MN"):
            self.assertGreater(counts.get(code, 0), 50, code)

    def test_required_fields_and_no_invented_labels(self):
        for row in self.rows:
            self.assertEqual(row["country_code"], "US")
            self.assertEqual(row["category"], "heat_pump")
            self.assertTrue(row["name"] and row["city"] and row["admin1"])
            self.assertTrue(row["phone"] or row["website"])
            self.assertTrue(row["sources"])
            self.assertIn(row["ownership_status"], {"unverified", "platform_owned", "franchise"})
            self.assertFalse(row["featured"])
            self.assertIsInstance(row["manual_j_claimed"], bool)
            self.assertNotIn("email", row)
            self.assertNotIn("rating", row)
            for source in row["sources"]:
                self.assertTrue(source["url"].startswith("http"))
                self.assertTrue(source["retrieved"])
            if row["ownership_status"] != "unverified":
                self.assertTrue(row["ownership_source_url"])
                self.assertTrue(row["ownership_parent"])
            else:
                self.assertEqual(row["ownership_label"], "Ownership: unverified")
            if row["admin1"] == "MN":
                self.assertEqual(row["heat_pump_signal"], "mechanical_license_only")
                self.assertEqual(row["rebate_programs"], [])
            else:
                self.assertEqual(row["heat_pump_signal"], "program_roster")
                self.assertTrue(row["rebate_programs"])

    def test_manual_j_is_not_asserted_without_a_source_flag(self):
        # None of the ingested files state Manual J. A true value would be a bug
        # until a source column is wired through.
        self.assertTrue(all(row["manual_j_claimed"] is False for row in self.rows))


class SiteTest(unittest.TestCase):
    def test_dist_exists(self):
        self.assertTrue((DIST / "index.html").exists(), "run python3 scripts/build_site.py")
        self.assertTrue((DIST / "sitemap.xml").exists())
        self.assertTrue((DIST / "robots.txt").exists())
        self.assertTrue((DIST / "404.html").exists())
        cfg = json.loads((ROOT / "config" / "site.json").read_text(encoding="utf-8"))
        self.assertEqual((DIST / "CNAME").exists(), bool(cfg.get("publish_cname")), "CNAME presence must follow config publish_cname")

    def test_every_listing_page_exists(self):
        rows = json.loads((ROOT / "data" / "listings.json").read_text(encoding="utf-8"))["listings"]
        missing = [row["path"] for row in rows if not (DIST / row["path"].strip("/") / "index.html").exists()]
        self.assertEqual(missing[:5], [])
        self.assertEqual(len(missing), 0)

    def test_internal_links_on_key_pages(self):
        pages = [
            DIST / "index.html",
            DIST / "us" / "index.html",
            DIST / "us" / "ma" / "index.html",
            DIST / "us" / "rebates" / "mn" / "index.html",
            DIST / "us" / "guides" / "how-we-label-ownership" / "index.html",
            DIST / "about" / "index.html",
            DIST / "claim" / "index.html",
        ]
        rows = json.loads((ROOT / "data" / "listings.json").read_text(encoding="utf-8"))["listings"]
        for state in ("ma", "me", "ny", "ca", "mn"):
            sample = next(row for row in rows if row["admin1_slug"] == state and not row.get("outside_program_state"))
            pages.append(DIST / sample["path"].strip("/") / "index.html")
            pages.append(DIST / "us" / state / sample["city_slug"] / "index.html")
        hrefs = re.compile(r'href="([^"]+)"')
        for page in pages:
            text = page.read_text(encoding="utf-8")
            self.assertIn('rel="canonical"', text)
            for href in hrefs.findall(text):
                if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                    continue
                target = (page.parent / href).resolve()
                if target.is_dir():
                    target = target / "index.html"
                self.assertTrue(target.exists(), f"{href} from {page.relative_to(DIST)}")

    def test_public_copy_has_no_private_names(self):
        blobs = []
        for path in [ROOT / "README.md", DIST / "index.html", DIST / "about" / "index.html"]:
            blobs.append(path.read_text(encoding="utf-8"))
        # Sample profiles rather than reading every page into one string.
        for path in list((DIST / "us").rglob("index.html"))[:40]:
            blobs.append(path.read_text(encoding="utf-8"))
        text = "\n".join(blobs)
        for word in FORBIDDEN:
            self.assertNotIn(word, text)
        self.assertNotIn(" Gus ", " " + text + " ")


if __name__ == "__main__":
    unittest.main()
