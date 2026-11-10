"""Answer-first ownership pages stay tied to the published listings."""

from __future__ import annotations

import json
import re
import unittest
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ORIGIN = "https://electrifyradar.com"
STATES = ("ma", "me", "ny", "ct", "ri", "vt", "ca", "mn")
DASHES = ("\u2014", "\u2013")
FORBIDDEN = ("PrimeLogic", "Stathopoulos", "Constantin", "Switzerland")


def _blocks(html: str):
    return [
        json.loads(block)
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html)
    ]


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


def _visible_faq(html: str):
    section = re.search(r'<section class="faq">(.*?)</section>', html, re.S)
    if not section:
        return []
    pairs = re.findall(r"<h3>(.*?)</h3>\s*<p>(.*?)</p>", section.group(1), re.S)
    return [(_norm(re.sub(r"<[^>]+>", "", question)), _norm(re.sub(r"<[^>]+>", "", answer))) for question, answer in pairs]


def _faq_ld(html: str):
    for block in _blocks(html):
        if block.get("@type") == "FAQPage":
            return [
                (_norm(item["name"]), _norm(item["acceptedAnswer"]["text"]))
                for item in block["mainEntity"]
            ]
    return []


class OwnershipAnswerTest(unittest.TestCase):
    def test_faq_visible_text_matches_jsonld(self):
        pages = [DIST / "index.html", DIST / "us" / "me" / "index.html"]
        pages.append(DIST / "us" / "guides" / "efficiency-maine-heat-pump-rebate" / "index.html")
        for code in STATES:
            pages.append(DIST / "us" / code / "private-equity" / "index.html")
        for page in pages:
            html = page.read_text(encoding="utf-8")
            self.assertEqual(_visible_faq(html), _faq_ld(html), page.relative_to(DIST))
            self.assertTrue(_faq_ld(html), page.relative_to(DIST))

    def test_ownership_pages_name_matches_and_are_in_the_sitemap(self):
        sitemap = (DIST / "sitemap-pages.xml").read_text(encoding="utf-8")
        platforms = (DIST / "platforms" / "index.html").read_text(encoding="utf-8")
        expected = {
            "ma": ["Sila Services", "American Residential Services, LLC", "Goldman Sachs Alternatives", "GI Partners and Charlesbank Capital Partners"],
            "ca": ["Divine Electric", "Any Hour Group", "Knox Lane"],
            "mn": ["Mcquillan Home Services LLC", "Any Hour Group"],
            "me": ["No listing in this state matched a documented private equity or platform owner.", "Aire Serv of Southern Maine"],
            "ct": ["Aire Serv of North Central CT"],
            "ny": ["No listing in this state matched a documented private equity or platform owner."],
            "ri": ["No listing in this state matched a documented private equity or platform owner."],
            "vt": ["No listing in this state matched a documented private equity or platform owner."],
        }
        counts = {"ma": 2, "ca": 1, "mn": 1, "me": 0, "ct": 0, "ny": 0, "ri": 0, "vt": 0}
        for code, phrases in expected.items():
            html = (DIST / "us" / code / "private-equity" / "index.html").read_text(encoding="utf-8")
            url = f"{ORIGIN}/us/{code}/private-equity/"
            self.assertIn(url, sitemap)
            self.assertIn(f"/us/{code}/private-equity/", platforms)
            self.assertIn("Last updated 3 November 2026.", html)
            self.assertIn("Source note:", html)
            self.assertIn("Only matched names are labeled.", html)
            for phrase in phrases:
                self.assertIn(phrase, html)
            item_lists = [block for block in _blocks(html) if block.get("@type") == "ItemList"]
            self.assertEqual(item_lists[0]["numberOfItems"], counts[code])
            webpage = next(block for block in _blocks(html) if block.get("@type") == "WebPage")
            self.assertEqual(webpage["dateModified"], "2026-11-03")
            for dash in DASHES:
                self.assertNotIn(dash, html)
            for word in FORBIDDEN:
                self.assertNotIn(word, html)

    def test_homepage_and_maine_open_with_dated_answers(self):
        home = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn("Last updated 3 November 2026.", home)
        self.assertIn("7243", home)
        self.assertIn("Sila Services", home)
        self.assertIn("Mcquillan Home Services LLC", home)
        self.assertLess(home.index("Quick answer."), home.index("Launch states"))
        self.assertIn('"dateModified": "2026-11-03"', home)
        maine = (DIST / "us" / "me" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Last updated 3 November 2026.", maine)
        self.assertIn("$3,000 (low income, lifetime cap $9,000)", maine)
        self.assertIn("$2,000 (moderate income, cap $6,000)", maine)
        self.assertIn("$1,000 (any income, cap $3,000)", maine)
        self.assertIn("private-equity/", maine)
        self.assertIn('"dateModified": "2026-11-03"', maine)
        guide = (DIST / "us" / "guides" / "efficiency-maine-heat-pump-rebate" / "index.html").read_text(encoding="utf-8")
        self.assertLess(guide.index("Last updated 3 November 2026."), guide.index("<h2>Rebate amounts"))
        self.assertLess(guide.index("<section class=\"faq\">"), guide.index("<h2>Rebate amounts"))
        self.assertIn("$3,000 for low income (lifetime cap $9,000 per housing unit)", guide)
        self.assertIn("dateModified", guide)
        self.assertIn("../../me/private-equity/", guide)
        for word in FORBIDDEN:
            self.assertNotIn(word, home)
            self.assertNotIn(word, maine)
            self.assertNotIn(word, guide)

    def test_llms_describes_dataset_and_ownership_lists(self):
        llms = (DIST / "llms.txt").read_text(encoding="utf-8")
        full = (DIST / "llms-full.txt").read_text(encoding="utf-8")
        self.assertIn("data_as_of: 2026-11-03", llms)
        self.assertIn("data/listings.json", llms)
        self.assertIn("data/ownership/platforms.json", llms)
        self.assertIn("How to compare heat pump installers before requesting quotes", llms)
        self.assertNotIn("Vetting checklist", llms)
        for code in STATES:
            url = f"{ORIGIN}/us/{code}/private-equity/"
            self.assertIn(url, llms)
            self.assertIn(url, full)
        self.assertIn("Sila Services", llms)
        self.assertIn("Divine Electric", full)
        self.assertIn("## Franchise records", full)
        for dash in DASHES:
            self.assertNotIn(dash, llms)
            self.assertNotIn(dash, full)
        for word in FORBIDDEN:
            self.assertNotIn(word, llms)
            self.assertNotIn(word, full)


if __name__ == "__main__":
    unittest.main()
