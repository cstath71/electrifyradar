"""IndexNow submission choice, the key file, Bingbot, and the homepage description."""

from __future__ import annotations

import json
import re
import sys
import unittest
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_site import homepage_description  # noqa: E402
from indexnow import select_urls  # noqa: E402

DIST = ROOT / "dist"
ORIGIN = "https://electrifyradar.com"


class IndexNowSelectionTest(unittest.TestCase):
    def test_first_run_is_hubs_and_largest_cities_without_profiles(self):
        groups = {
            "pages": [
                (f"{ORIGIN}/", "2026-11-10"),
                (f"{ORIGIN}/us/ma/", "2026-11-10"),
                (f"{ORIGIN}/us/guides/independent-vs-pe-hvac/", "2026-11-10"),
            ],
            "cities": [
                (f"{ORIGIN}/us/ma/small/", "2026-11-03"),
                (f"{ORIGIN}/us/ma/large/", "2026-11-03"),
            ],
            "installers": [
                (f"{ORIGIN}/us/ma/large/example-co/", "2026-11-03"),
            ],
        }
        counts = {f"{ORIGIN}/us/ma/large/": 50, f"{ORIGIN}/us/ma/small/": 3}
        chosen = select_urls(groups, counts, previous={}, first_run=True, limit=10)
        self.assertEqual(
            chosen,
            [
                f"{ORIGIN}/",
                f"{ORIGIN}/us/ma/",
                f"{ORIGIN}/us/guides/independent-vs-pe-hvac/",
                f"{ORIGIN}/us/ma/large/",
                f"{ORIGIN}/us/ma/small/",
            ],
        )
        self.assertNotIn(f"{ORIGIN}/us/ma/large/example-co/", chosen)

    def test_first_run_stops_at_the_limit(self):
        groups = {
            "pages": [(f"{ORIGIN}/", "2026-11-10"), (f"{ORIGIN}/us/ma/", "2026-11-10")],
            "cities": [(f"{ORIGIN}/us/ma/boston/", "2026-11-03")],
            "installers": [],
        }
        chosen = select_urls(groups, {}, previous=None, first_run=True, limit=1)
        self.assertEqual(chosen, [f"{ORIGIN}/"])

    def test_changed_run_keeps_pages_ahead_of_profiles_and_skips_unchanged(self):
        groups = {
            "pages": [
                (f"{ORIGIN}/", "2026-11-10"),
                (f"{ORIGIN}/us/me/", "2026-11-11"),
            ],
            "cities": [
                (f"{ORIGIN}/us/me/portland/", "2026-11-11"),
                (f"{ORIGIN}/us/me/bangor/", "2026-11-03"),
            ],
            "installers": [
                (f"{ORIGIN}/us/me/portland/one/", "2026-11-11"),
                (f"{ORIGIN}/us/me/bangor/two/", "2026-11-03"),
            ],
        }
        previous = {
            f"{ORIGIN}/": "2026-11-10",
            f"{ORIGIN}/us/me/": "2026-11-10",
            f"{ORIGIN}/us/me/portland/": "2026-11-03",
            f"{ORIGIN}/us/me/bangor/": "2026-11-03",
            f"{ORIGIN}/us/me/portland/one/": "2026-11-03",
            f"{ORIGIN}/us/me/bangor/two/": "2026-11-03",
        }
        chosen = select_urls(groups, {f"{ORIGIN}/us/me/portland/": 20}, previous, first_run=False, limit=10)
        self.assertEqual(
            chosen,
            [
                f"{ORIGIN}/us/me/",
                f"{ORIGIN}/us/me/portland/",
                f"{ORIGIN}/us/me/portland/one/",
            ],
        )

    def test_changed_run_caps_before_profiles_when_the_limit_is_reached(self):
        groups = {
            "pages": [(f"{ORIGIN}/", "2026-11-12")],
            "cities": [],
            "installers": [(f"{ORIGIN}/us/ma/boston/one/", "2026-11-12")],
        }
        chosen = select_urls(groups, {}, previous={}, first_run=False, limit=1)
        self.assertEqual(chosen, [f"{ORIGIN}/"])


class PublishedIndexNowTest(unittest.TestCase):
    def test_homepage_meta_description_is_120_to_155_characters(self):
        listings = json.loads((ROOT / "data" / "listings.json").read_text(encoding="utf-8"))["listings"]
        expected = homepage_description(len(listings), 8)
        self.assertGreaterEqual(len(expected), 120)
        self.assertLessEqual(len(expected), 155)
        for total in (1, 99, 7243, 999999):
            text = homepage_description(total, 8)
            self.assertGreaterEqual(len(text), 120, text)
            self.assertLessEqual(len(text), 155, text)
        html = (DIST / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<meta name="description" content="([^"]*)">', html)
        desc = unescape(match.group(1))
        self.assertEqual(desc, expected)
        self.assertEqual(len(desc), len(expected))
        self.assertIn(f'<meta property="og:description" content="{expected}">', html)
        self.assertIn(f'"description": "{expected}"', html)
        self.assertNotIn("\u2014", desc)
        self.assertNotIn("\u2013", desc)

    def test_key_file_sitemap_index_and_bingbot(self):
        site = json.loads((ROOT / "config" / "site.json").read_text(encoding="utf-8"))
        key = site["indexnow_key"]
        body = (DIST / f"{key}.txt").read_text(encoding="utf-8")
        self.assertEqual(body.strip(), key)
        self.assertNotIn("/", body)
        robots = (DIST / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("User-agent: Bingbot\nAllow: /", robots)
        self.assertNotIn("Disallow", robots)
        self.assertIn(f"Sitemap: {ORIGIN}/sitemap.xml", robots)
        sitemap = (DIST / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("<sitemapindex", sitemap)
        for name in ("sitemap-pages.xml", "sitemap-cities.xml", "sitemap-installers.xml"):
            self.assertIn(f"{ORIGIN}/{name}", sitemap)
            self.assertTrue((DIST / name).exists())
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        self.assertIn("indexnow:", workflow)
        self.assertIn("needs: deploy", workflow)
        self.assertIn("python3 scripts/indexnow.py --after-deploy", workflow)
        script = (ROOT / "scripts" / "indexnow.py").read_text(encoding="utf-8")
        self.assertIn("https://api.indexnow.org/indexnow", script)


if __name__ == "__main__":
    unittest.main()
