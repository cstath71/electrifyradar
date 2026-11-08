"""The published installer-comparison guide matches the approved copy."""

from __future__ import annotations

import json
import re
import unittest
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
GUIDE = DIST / "us" / "guides" / "questions-to-ask-heat-pump-installer" / "index.html"
INDEX = DIST / "us" / "guides" / "index.html"
TITLE = "How to compare heat pump installers before requesting quotes"
DESCRIPTION = (
    "Build a useful heat pump installer shortlist, ask about sizing and service, "
    "and compare written quotes without assuming credentials or rebates guarantee results."
)
CANONICAL = "https://electrifyradar.com/us/guides/questions-to-ask-heat-pump-installer/"
FORBIDDEN = ("PrimeLogic", "Stathopoulos", "Constantin", "Switzerland")
STALE = (
    "What is Manual J and why does it matter?",
    "How many quotes should I get?",
    "Should I care if the company is PE- or platform-owned?",
    "Does a program badge (HPIN / Efficiency Maine / Clean Heat) guarantee quality?",
    "What paperwork should I keep after install?",
    "Square-footage-only sizing is a red flag",
    "Shortlist three program-roster installers",
    "FAQPage",
)

# Approved public body, without the title line the page template renders as h1.
APPROVED_BODY = """
Start with businesses that serve your home and have experience with the kind of system you need. Then ask each bidder to explain its sizing approach and put the same scope of work in writing. A directory listing, familiar brand or low headline price cannot answer those questions for you.

The aim is a shortlist you understand and proposals you can compare, not a ranking based on badges or company size.

Prepare a short description of your home

Before contacting installers, note your existing heating system, uncomfortable rooms, recent energy use and any planned insulation or window work. Explain whether you want whole-home heating, help for particular rooms or a replacement cooling system with heating capability.

ENERGY STAR's contractor-hiring guidance recommends knowing your existing system and its maintenance history, noting comfort problems and expecting a home evaluation. Give bidders the same starting information. Ask what they need to inspect before providing a firm proposal.

Shortlist businesses, not just directory entries

Confirm service coverage for your address and ask which office would handle installation and later service. Check whether multiple listings are branches of a business you have already contacted. A second branch is not automatically a separate competitor.

Ask about recent work on similar homes and the proposed system type, such as ducted or ductless equipment. Request references and ask about installation and follow-up service. Experience with one type of project does not establish suitability for every home.

Verify applicable licensing and insurance requirements through the relevant state or local authority. If you plan to use an incentive, separately check the program administrator's current contractor requirements. Not every jurisdiction or program uses the same credentials.

Read the source behind a directory entry. ElectrifyRadar's Minnesota mechanical-bond listings are not a heat-pump-qualified installer roster. A mechanical contracting credential alone does not establish heat-pump experience or rebate eligibility. Our methodology explains these source differences.

Ask how the proposed system will be sized

Ask the installer to explain the home's heating and cooling loads and how those loads inform equipment selection. ENERGY STAR's heat pump buying guidance recommends verifying system size with a Manual J calculation and discusses component matching, duct assessment and onsite inspection.

Ask how the proposal accounts for your local winter conditions, room distribution and any retained backup heat. A statement based only on floor area or the old equipment size needs more explanation. You do not need to perform the design yourself, but you should understand the basis of the recommendation and what documentation you will receive.

Request a comparable written scope

Ask each bidder to identify what is included, excluded and still subject to inspection. Use the same questions for each proposal:

Ask about | What to request in writing
Equipment and sizing | Indoor and outdoor model numbers, sizing basis and intended heating coverage
Distribution | Proposed duct work or indoor-unit placement, refrigerant routing and relevant airflow checks
Electrical and ancillary work | Circuits, any proposed panel work, mounting, drainage, removal and making good disturbed areas
Existing heat | What stays, what changes and how backup heat or controls would operate
Installation responsibilities | Who performs the work, handles applicable permits and documents commissioning checks
Warranty and service | Equipment and labor coverage, exclusions, registration responsibilities and service contact
Timing and price | Schedule, itemized costs, exclusions and how changes will be agreed

Some items will not apply to your project. Ask bidders to mark those explicitly rather than leaving gaps. ENERGY STAR recommends written, itemized estimates and a written proposal covering costs, model numbers, schedule and warranty information.

Keep rebates separate from the installation promise

Ask which program a quoted incentive refers to, what equipment and contractor conditions apply, whether approval is needed before work and who submits the documents. Verify the answer with the current program administrator before relying on it.

Keep the full project price visible beside any assumed incentive. A contractor's estimate is not a guarantee of a rebate or tax benefit. Eligibility can depend on the household, equipment, work scope, application timing and program rules. This guide does not establish your eligibility.

Compare the proposals before choosing

Check that the bidders are offering the same intended heating coverage.
Resolve missing equipment details, electrical work and exclusions before comparing totals.
Ask why sizing or backup-heat recommendations differ.
Compare warranty and service responsibilities as well as purchase cost.
Keep written answers and request a revised proposal when the scope changes.

Ownership information is separate context, not a workmanship score. Our ownership-label guide explains what sourced labels mean. Whether the business has one location or several, compare its written proposal and answers for your home. None of these checks guarantees performance, but they make unresolved questions visible before you commit.
""".strip()


def _plain_lines(fragment: str) -> list[str]:
    text = re.sub(r"<a\b[^>]*>(.*?)</a>", r"\1", fragment, flags=re.S)
    text = re.sub(r"</(p|h1|h2|li|tr|div|table|thead|tbody)>", "\n", text)
    text = re.sub(r"<t[hd][^>]*>", " | ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    lines = []
    for line in text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip(" |")
        if cleaned:
            lines.append(cleaned)
    return lines


class InstallerGuideTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = GUIDE.read_text(encoding="utf-8")
        cls.blocks = [
            json.loads(block)
            for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', cls.html)
        ]

    def test_title_description_canonical_and_h1(self):
        html = self.html
        self.assertIn(f"<title>{TITLE} | ElectrifyRadar</title>", html)
        self.assertIn(f'<meta name="description" content="{DESCRIPTION}">', html)
        self.assertIn(f'<meta property="og:title" content="{TITLE} | ElectrifyRadar">', html)
        self.assertIn(f'<meta property="og:description" content="{DESCRIPTION}">', html)
        self.assertIn(f'<meta name="twitter:title" content="{TITLE} | ElectrifyRadar">', html)
        self.assertIn(f'<meta name="twitter:description" content="{DESCRIPTION}">', html)
        self.assertIn(f'<link rel="canonical" href="{CANONICAL}">', html)
        self.assertIn(f"<h1>{TITLE}</h1>", html)
        self.assertEqual(html.count("<h1>"), 1)

    def test_body_matches_approved_copy(self):
        start = self.html.index("<h1>")
        end = self.html.index('<p class="fine">Last reviewed')
        rendered = _plain_lines(self.html[start:end])
        # The template h1 repeats the title; the approved body starts at the first paragraph.
        self.assertEqual(rendered[0], TITLE)
        self.assertEqual(rendered[1:], _plain_lines(APPROVED_BODY))
        self.assertIn(
            "ElectrifyRadar's Minnesota mechanical-bond listings are not a heat-pump-qualified installer roster.",
            self.html,
        )
        self.assertIn(
            "A mechanical contracting credential alone does not establish heat-pump experience or rebate eligibility.",
            self.html,
        )

    def test_article_schema_dates_and_no_stale_faq(self):
        types = [block["@type"] for block in self.blocks]
        self.assertIn("Article", types)
        self.assertIn("BreadcrumbList", types)
        self.assertNotIn("FAQPage", types)
        article = next(block for block in self.blocks if block["@type"] == "Article")
        self.assertEqual(article["headline"], TITLE)
        self.assertEqual(article["description"], DESCRIPTION)
        self.assertEqual(article["datePublished"], "2026-11-03")
        self.assertEqual(article["dateModified"], "2026-11-08")
        self.assertEqual(article["author"], {
            "@type": "Organization",
            "name": "ElectrifyRadar",
            "url": "https://electrifyradar.com/",
        })
        self.assertNotEqual(article["author"]["@type"], "Person")
        self.assertEqual(article["mainEntityOfPage"]["@id"], CANONICAL)
        crumbs = next(block for block in self.blocks if block["@type"] == "BreadcrumbList")
        self.assertEqual(crumbs["itemListElement"][-1]["name"], TITLE)
        self.assertEqual(crumbs["itemListElement"][-1]["item"], CANONICAL)
        for phrase in STALE:
            self.assertNotIn(phrase, self.html)
        self.assertIn("Last reviewed 2026-11-08. Publisher: ElectrifyRadar.", self.html)
        self.assertIn('<meta name="author" content="ElectrifyRadar">', self.html)

    def test_links_resolve_and_index_metadata_matches(self):
        content = self.html.split("<h1>", 1)[1].split('<p class="fine">', 1)[0]
        links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', content)
        self.assertEqual(
            links,
            [
                (
                    "https://www.energystar.gov/saveathome/heating-cooling/10-tips-hiring",
                    "ENERGY STAR's contractor-hiring guidance",
                ),
                (
                    "https://electrifyradar.com/methodology/",
                    "methodology",
                ),
                (
                    "https://www.energystar.gov/products/energy_star_home_upgrade/clean_heating_cooling",
                    "heat pump buying guidance",
                ),
                (
                    "https://electrifyradar.com/us/guides/independent-vs-pe-hvac/",
                    "ownership-label guide",
                ),
            ],
        )
        local = {
            "https://electrifyradar.com/methodology/": DIST / "methodology" / "index.html",
            "https://electrifyradar.com/us/guides/independent-vs-pe-hvac/": DIST / "us" / "guides" / "independent-vs-pe-hvac" / "index.html",
        }
        for href, path in local.items():
            self.assertTrue(path.exists(), href)
        index = INDEX.read_text(encoding="utf-8")
        self.assertIn(f">{TITLE}</a>", index)
        self.assertIn(DESCRIPTION, index)
        self.assertNotIn("Questions to ask a heat pump installer before you sign", index)
        sitemap = (DIST / "sitemap-pages.xml").read_text(encoding="utf-8")
        self.assertIn(f"<loc>{CANONICAL}</loc><lastmod>2026-11-08</lastmod>", sitemap)
        self.assertIn(
            "<loc>https://electrifyradar.com/us/guides/mass-save-heat-pump-rebate/</loc><lastmod>2026-11-03</lastmod>",
            sitemap,
        )
        llms = (DIST / "llms.txt").read_text(encoding="utf-8")
        self.assertIn(TITLE, llms)
        self.assertNotIn("Vetting checklist", llms)
        for word in FORBIDDEN:
            self.assertNotIn(word, self.html)
            self.assertNotIn(word, index)

    def test_other_guides_keep_original_dates_and_faq_when_present(self):
        other = (DIST / "us" / "guides" / "mass-save-heat-pump-rebate" / "index.html").read_text(encoding="utf-8")
        blocks = [json.loads(block) for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', other)]
        article = next(block for block in blocks if block["@type"] == "Article")
        self.assertEqual(article["datePublished"], "2026-11-03")
        self.assertEqual(article["dateModified"], "2026-11-03")
        self.assertIn("FAQPage", other)
        self.assertIn("Last reviewed 2026-11-03.", other)

    def test_mobile_table_layout_rules(self):
        self.assertIn('<div class="table-scroll">', self.html)
        rows = re.findall(r"<tr>(.*?)</tr>", self.html, flags=re.S)
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0].count("<th>"), 2)
        for row in rows[1:]:
            self.assertEqual(row.count("<td>"), 2)
        css = (ROOT / "assets" / "site.css").read_text(encoding="utf-8")
        self.assertIn(".table-scroll {\n  overflow-x: auto;", css)
        self.assertIn("max-width: 100%;", css)
        self.assertIn("table-layout: fixed;", css)
        self.assertIn("overflow-wrap: anywhere;", css)
        self.assertIn("@media (max-width: 719px)", css)
        self.assertIn(".prose .table-scroll th,", css)
        self.assertIn(".footer-grid > * { min-width: 0; max-width: 100%; }", css)
        self.assertIn('.site-footer p a + a::before { content: "\\200b"; }', css)


if __name__ == "__main__":
    unittest.main()
