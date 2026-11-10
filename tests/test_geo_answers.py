"""The eight November 2026 answer pages stay tied to the data files.

Headline installer counts are recomputed from data/listings.json and checked
against data/stats.json. Dollar amounts in the new quick answers must already
appear in the official-page quotes kept in scripts/guide_content.py or
scripts/build_site.py. FAQ JSON-LD must equal the visible FAQ text.
"""

from __future__ import annotations

import json
import re
import sys
import unittest
from collections import Counter
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from geo_answers import answer_catalog, answer_link_pairs  # noqa: E402

DIST = ROOT / "dist"
ORIGIN = "https://electrifyradar.com"
DASHES = ("\u2014", "\u2013")
FORBIDDEN = ("PrimeLogic", "Stathopoulos", "Constantin", "Switzerland")
CONTENT_UPDATED = "2026-11-10"
PE_STATUSES = {"pe_owned", "platform_owned"}


def _blocks(html: str):
    return [
        json.loads(block)
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    ]


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


def _visible_faq(html: str):
    section = re.search(r'<section class="faq">(.*?)</section>', html, re.S)
    if not section:
        return []
    pairs = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", section.group(1), re.S)
    return [(_norm(re.sub(r"<[^>]+>", "", q)), _norm(re.sub(r"<[^>]+>", "", a))) for q, a in pairs]


def _faq_ld(html: str):
    for block in _blocks(html):
        if block.get("@type") == "FAQPage":
            return [
                (_norm(item["name"]), _norm(item["acceptedAnswer"]["text"]))
                for item in block["mainEntity"]
            ]
    return []


def _quick(html: str) -> str:
    match = re.search(r'<p class="quick-answer">(.*?)</p>', html, re.S)
    text = re.sub(r"<[^>]+>", "", match.group(1))
    text = _norm(text)
    prefix = "Quick answer."
    if text.startswith(prefix):
        text = text[len(prefix):].strip()
    return text


def _page(path: str) -> str:
    relative = path.strip("/")
    file = DIST / "index.html" if not relative else DIST / relative / "index.html"
    return file.read_text(encoding="utf-8")


class GeoAnswerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        payload = json.loads((ROOT / "data" / "listings.json").read_text(encoding="utf-8"))
        cls.listings = payload["listings"]
        cls.stats = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
        cls.site = json.loads((ROOT / "config" / "site.json").read_text(encoding="utf-8"))
        cls.by_slug = {}
        for row in cls.listings:
            cls.by_slug.setdefault(row["admin1_slug"], []).append(row)
        cls.catalog = answer_catalog(cls.listings)
        cls.sourced = (
            (ROOT / "scripts" / "guide_content.py").read_text(encoding="utf-8")
            + (ROOT / "scripts" / "build_site.py").read_text(encoding="utf-8")
        )

    def test_stats_match_listings(self):
        rows = self.listings
        self.assertEqual(self.stats["count"], len(rows))
        self.assertEqual(self.stats["as_of"], self.site["data_as_of"])
        self.assertEqual(self.stats["as_of"], "2026-11-03")
        by_state = Counter(row["admin1"] for row in rows)
        by_status = Counter(row["ownership_status"] for row in rows)
        for code, count in self.stats["by_state"].items():
            self.assertEqual(by_state[code], count, code)
        for status, count in self.stats["by_ownership"].items():
            self.assertEqual(by_status[status], count, status)
        self.assertEqual(sum(by_state.values()), len(rows))

    def test_each_answer_page_leads_with_recomputed_figures(self):
        rows = self.listings
        as_of = self.stats["as_of"]
        ma = self.by_slug["ma"]
        me = self.by_slug["me"]
        mn = self.by_slug["mn"]
        pe = lambda group: sum(1 for row in group if row["ownership_status"] in PE_STATUSES)
        ind = lambda group: sum(1 for row in group if row["ownership_status"] == "independent")
        unverified = lambda group: sum(1 for row in group if row["ownership_status"] == "unverified")
        franchise = lambda group: sum(1 for row in group if row["ownership_status"] == "franchise")
        phrases = {
            "ER-1": [
                f"{pe(rows)} of {len(rows)} heat pump installer records are labeled PE or platform-owned",
                f"{unverified(rows)} records are Ownership: unverified",
            ],
            "ER-2": [
                f"{len(ma)} contractors are on this Mass Save Heat Pump Installer Network list",
                f"of which {pe(ma)} are PE or platform-owned",
                f"{ind(ma)} are independent",
                f"{unverified(ma)} are Ownership: unverified",
            ],
            "ER-3": [
                "$3,000 for low income (lifetime cap $9,000 per housing unit)",
                "$2,000 for moderate income (cap $6,000)",
                "$1,000 for any income (cap $3,000)",
            ],
            "ER-4": [f"ElectrifyRadar lists {len(rows)} installer records across {len(self.by_slug)} states"],
            "ER-5": [
                "$2,650 per ton up to $8,500",
                "$1,125 per ton up to $8,500",
                "$250 per ton up to $2,500",
                "$16,000",
            ],
            "ER-6": [
                f"{len(me)} installers in Maine are Efficiency Maine Residential Registered Vendors",
                f"of which {pe(me)} are PE or platform-owned",
                f"{franchise(me)} is a franchise" if franchise(me) == 1 else f"{franchise(me)} are franchises",
                f"{ind(me)} are independent",
                "$3,000 (low income, lifetime cap $9,000)",
                "$2,000 (moderate income, cap $6,000)",
                "$1,000 (any income, cap $3,000)",
            ],
            "ER-7": [
                f"lists {len(ma)} heat pump installer records in Massachusetts, of which {pe(ma)} are PE or platform-owned",
                f"{unverified(ma)} labeled Ownership: unverified",
                f"{ind(ma)} independent",
            ],
            "ER-8": [
                f"{len(mn)} businesses are listed in this Minnesota directory",
                f"of which {pe(mn)} is PE or platform-owned" if pe(mn) == 1 else f"of which {pe(mn)} are PE or platform-owned",
                f"{franchise(mn)} are franchises",
                f"{ind(mn)} are independent",
                "lesser of $4,000",
                "not a cold-climate heat pump program roster",
            ],
        }
        self.assertEqual([item["id"] for item in self.catalog], list(phrases))
        pairs = answer_link_pairs()
        self.assertEqual([item["title"] for item in self.catalog], [title for title, _path in pairs])
        self.assertEqual([item["path"] for item in self.catalog], [path for _title, path in pairs])
        for item in self.catalog:
            html = _page(item["path"])
            quick = _quick(html)
            self.assertEqual(quick, item["lead"], item["id"])
            self.assertTrue(quick.startswith(f"As of the November 2026 ElectrifyRadar data (checked {as_of})"), item["id"])
            for phrase in phrases[item["id"]]:
                self.assertIn(phrase, quick, item["id"])
                self.assertIn(phrase, item["lead"], item["id"])
            dollars = set(re.findall(r"\$[\d,]+", quick))
            for amount in dollars:
                self.assertIn(amount, self.sourced, amount)
            self.assertIn(f"<h1>{item['title']}</h1>", html)
            self.assertIn(f"<title>{item['title']} | ElectrifyRadar</title>", html)
            self.assertEqual(_visible_faq(html), _faq_ld(html), item["id"])
            self.assertTrue(_faq_ld(html), item["id"])
            self.assertEqual(_faq_ld(html)[0][1], item["lead"], item["id"])
            datasets = [block for block in _blocks(html) if block.get("@type") == "Dataset"]
            self.assertEqual(len(datasets), 1, item["id"])
            self.assertEqual(datasets[0]["dateModified"], as_of, item["id"])
            fresh = _quick(html) + "\n" + "\n".join(part for pair in _visible_faq(html) for part in pair)
            for dash in DASHES:
                self.assertNotIn(dash, fresh, item["id"])
            for word in FORBIDDEN:
                self.assertNotIn(word, html, item["id"])

    def test_directory_itemlists_match_listing_counts(self):
        expected = {
            "/us/ma/": len(self.by_slug["ma"]),
            "/us/me/": len(self.by_slug["me"]),
            "/us/mn/": len(self.by_slug["mn"]),
            "/us/ma/private-equity/": sum(
                1 for row in self.by_slug["ma"] if row["ownership_status"] in PE_STATUSES
            ),
        }
        for path, count in expected.items():
            html = _page(path)
            lists = [block for block in _blocks(html) if block.get("@type") == "ItemList"]
            sizes = {block.get("numberOfItems") for block in lists}
            self.assertIn(count, sizes, path)
            if path != "/us/ma/private-equity/":
                section = re.search(r'<ul class="directory-names">(.*?)</ul>', html, re.S)
                self.assertIsNotNone(section, path)
                self.assertEqual(section.group(1).count("<li>"), count, path)

    def test_homepage_and_state_pages_link_the_answers(self):
        pages = [DIST / "index.html"]
        for code in self.by_slug:
            pages.append(DIST / "us" / code / "index.html")
        for page in pages:
            html = page.read_text(encoding="utf-8")
            for title, _path in answer_link_pairs():
                self.assertIn(f">{title}</a>", html, page.relative_to(DIST))

    def test_llms_and_sitemap_carry_the_answers(self):
        llms = (DIST / "llms.txt").read_text(encoding="utf-8")
        full = (DIST / "llms-full.txt").read_text(encoding="utf-8")
        sitemap = (DIST / "sitemap-pages.xml").read_text(encoding="utf-8")
        for item in self.catalog:
            self.assertIn(item["lead"], llms, item["id"])
            self.assertIn(item["lead"], full, item["id"])
            self.assertIn(item["title"], llms, item["id"])
            loc = f"<loc>{ORIGIN}{item['path']}</loc><lastmod>{CONTENT_UPDATED}</lastmod>"
            self.assertIn(loc, sitemap, item["id"])
        for dash in DASHES:
            self.assertNotIn(dash, llms)
            self.assertNotIn(dash, full)
        for word in FORBIDDEN:
            self.assertNotIn(word, llms)
            self.assertNotIn(word, full)


if __name__ == "__main__":
    unittest.main()
