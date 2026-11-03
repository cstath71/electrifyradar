#!/usr/bin/env python3
"""Build the static ElectrifyRadar site into dist/ from data/listings.json."""

from __future__ import annotations

import html
import json
import shutil
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

from common import ROOT, STATES, load_json

DIST = ROOT / "dist"
SITE = load_json(ROOT / "config" / "site.json")
ORIGIN = SITE["canonical_origin"].rstrip("/")
AS_OF = SITE["data_as_of"]
EMAIL = SITE["contact_email"]
NAME = SITE["name"]
FORM_KEY = SITE.get("form_access_key", "")
FORM_ENDPOINT = SITE.get("form_endpoint", "") if FORM_KEY else ""


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def rel_url(from_dir: str, target: str) -> str:
    is_dir = target.endswith("/")
    from_parts = [part for part in from_dir.strip("/").split("/") if part]
    to_parts = [part for part in target.strip("/").split("/") if part]
    index = 0
    while index < len(from_parts) and index < len(to_parts) and from_parts[index] == to_parts[index]:
        index += 1
    parts = [".."] * (len(from_parts) - index) + to_parts[index:]
    if not parts:
        return "./"
    url = "/".join(parts)
    if is_dir:
        url += "/"
    return url


def absolute(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return ORIGIN + path


def logo_svg() -> str:
    return (ROOT / "assets" / "logo.svg").read_text(encoding="utf-8").replace(
        'role="img" aria-label="ElectrifyRadar"',
        'class="logo" aria-hidden="true"',
    )


def shell(from_dir: str, title: str, description: str, body: str, path: str, extra_head: str = "", extra_script: str = "") -> str:
    root = rel_url(from_dir, "/")
    css = rel_url(from_dir, "/assets/site.css")
    icon = rel_url(from_dir, "/favicon.svg")
    nav = [
        ("Directory", "/"),
        ("States", "/us/"),
        ("Rebates", "/us/rebates/"),
        ("Guides", "/us/guides/"),
        ("Ownership", "/us/guides/how-we-label-ownership/"),
        ("About", "/about/"),
    ]
    nav_html = "".join(
        f'<a href="{esc(rel_url(from_dir, href))}">{esc(label)}</a>' for label, href in nav
    )
    footer_links = [
        ("About", "/about/"),
        ("Privacy", "/privacy/"),
        ("Terms", "/terms/"),
        ("Claim a listing", "/claim/"),
        ("Report a correction", "/report-correction/"),
    ]
    footer = "".join(
        f'<a href="{esc(rel_url(from_dir, href))}">{esc(label)}</a>' for label, href in footer_links
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(absolute(path))}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(absolute(path))}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(NAME)}">
<meta name="theme-color" content="#1f4d3a">
<link rel="icon" href="{esc(icon)}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@500;600;700&family=Fraunces:opsz,wght@9..144,560;9..144,640&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{esc(css)}">
{extra_head}
</head>
<body>
<a class="skip" href="#content">Skip to content</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{esc(root)}">{logo_svg()}<span>ElectrifyRadar</span></a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
  </div>
  <div class="wrap"><nav id="site-nav" class="nav">{nav_html}</nav></div>
</header>
<main id="content">
{body}
</main>
<footer class="site-footer">
  <div class="wrap footer-grid">
    <div>
      <strong>ElectrifyRadar</strong>
      <p class="fine">A public directory of heat pump and ductless mini-split installers in five launch states. Ownership is labeled only when a name matches a documented platform or franchise list. Last data check {esc(AS_OF)}.</p>
    </div>
    <div>
      <p>{footer}</p>
      <p><a href="mailto:{esc(EMAIL)}">{esc(EMAIL)}</a></p>
    </div>
    <form class="newsletter" action="mailto:{esc(EMAIL)}" data-subject="Newsletter signup">
      <label for="newsletter-email">Newsletter</label>
      <input id="newsletter-email" name="email" type="email" autocomplete="email" placeholder="you@example.com" required>
      <button type="submit">Sign me up</button>
      <p class="fine">Occasional updates on installers and rebates. Unsubscribe any time by writing to {esc(EMAIL)}.</p>
    </form>
  </div>
</footer>
<script>
document.querySelector(".menu-btn").addEventListener("click", function () {{
  var nav = document.getElementById("site-nav");
  nav.classList.toggle("open");
  this.setAttribute("aria-expanded", nav.classList.contains("open") ? "true" : "false");
}});
var FORM_ENDPOINT = {json.dumps(FORM_ENDPOINT)};
var FORM_KEY = {json.dumps(FORM_KEY)};
document.querySelectorAll("form[action^='mailto:']").forEach(function (form) {{
  form.addEventListener("submit", function (event) {{
    event.preventDefault();
    var data = new FormData(form);
    if (FORM_ENDPOINT && FORM_KEY) {{
      if ((data.get("company_website") || "").trim()) return;
      data.delete("company_website");
      data.append("access_key", FORM_KEY);
      data.append("subject", "ElectrifyRadar: " + (form.getAttribute("data-subject") || "Form"));
      data.append("from_name", "ElectrifyRadar website");
      data.append("page", window.location.href);
      var btn = form.querySelector("button[type=submit]");
      if (btn) btn.disabled = true;
      fetch(FORM_ENDPOINT, {{method: "POST", body: data, headers: {{"Accept": "application/json"}}}})
        .then(function (r) {{ return r.json(); }})
        .then(function (res) {{
          var msg = document.createElement("p");
          msg.className = "fine form-status";
          msg.textContent = res.success ? "Thanks, we got it." : "Sorry, that didn't send. Please email {EMAIL}.";
          form.appendChild(msg);
          if (res.success) form.reset();
        }})
        .catch(function () {{
          var msg = document.createElement("p");
          msg.className = "fine form-status";
          msg.textContent = "Sorry, that didn't send. Please email {EMAIL}.";
          form.appendChild(msg);
        }})
        .finally(function () {{ if (btn) btn.disabled = false; }});
      return;
    }}
    var lines = [];
    data.forEach(function (value, key) {{
      if (key !== "company_website") lines.push(key + ": " + value);
    }});
    if ((data.get("company_website") || "").trim()) return;
    var subject = encodeURIComponent(form.getAttribute("data-subject") || "ElectrifyRadar");
    var body = encodeURIComponent(lines.join("\\n"));
    window.location.href = form.getAttribute("action") + "?subject=" + subject + "&body=" + body;
  }});
}});
</script>
{extra_script}
</body>
</html>
"""


def write_page(path: str, html_doc: str):
    folder = DIST / path.strip("/")
    if path == "/":
        folder = DIST
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "index.html").write_text(html_doc, encoding="utf-8")


def crumbs(from_dir: str, items: list[tuple[str, str]]) -> str:
    parts = []
    for label, href in items[:-1]:
        parts.append(f'<a href="{esc(rel_url(from_dir, href))}">{esc(label)}</a>')
    parts.append(esc(items[-1][0]))
    return '<p class="crumbs">' + " / ".join(parts) + "</p>"


def search_block(from_dir: str, preset_state: str = "") -> str:
    index = rel_url(from_dir, "/search-index.json")
    state_options = '<option value="">All launch states</option>' + "".join(
        f'<option value="{code}">{esc(meta["name"])}</option>'
        for code, meta in STATES.items()
    )
    hidden_state = ""
    if preset_state:
        state_options = f'<option value="{esc(preset_state.lower())}">{esc(STATES[preset_state.lower()]["name"])}</option>'
    root = rel_url(from_dir, "/")
    return f"""
<section id="directory-search" class="panel" data-index="{esc(index)}" data-root="{esc(root)}" data-state="{esc(preset_state.lower())}">
  <form>
    <div class="filters">
      <div>
        <label for="q">Search by name or city</label>
        <input id="q" name="q" type="search" placeholder="Boston, mini-split, a company name">
      </div>
      <div>
        <label for="state">State</label>
        <select id="state" name="state">{state_options}</select>
      </div>
      <div>
        <label for="ownership">Ownership</label>
        <select id="ownership" name="ownership">
          <option value="">Any label</option>
          <option value="unverified">Ownership unverified</option>
          <option value="platform_owned">PE or platform-owned</option>
          <option value="franchise">Franchise</option>
        </select>
      </div>
      <div>
        <label for="signal">What the source shows</label>
        <select id="signal" name="signal">
          <option value="">Either</option>
          <option value="program_roster">Heat pump program roster</option>
          <option value="mechanical_license_only">Mechanical license only</option>
        </select>
      </div>
    </div>
    <div class="actions"><button type="submit">Filter</button></div>
  </form>
  <p id="search-count" aria-live="polite"></p>
  <div id="search-results" class="grid cards"></div>
  <p class="pager"><button type="button" id="search-more" class="secondary" hidden>Show more</button></p>
  {hidden_state}
</section>
"""


def json_ld(obj) -> str:
    payload = json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c")
    return f'<script type="application/ld+json">{payload}</script>'


def group_listings(listings):
    by_state = defaultdict(list)
    by_city = defaultdict(list)
    for row in listings:
        by_state[row["admin1_slug"]].append(row)
        by_city[(row["admin1_slug"], row["city_slug"])].append(row)
    return by_state, by_city


def city_title(state_slug: str, city_slug: str, sample: dict) -> str:
    if city_slug.startswith("outside-"):
        region = city_slug.split("-", 1)[1].upper()
        return f"Mailing address in {region}"
    return sample["city"]


def ownership_phrase(row) -> str:
    if row["ownership_status"] == "unverified":
        return (
            f"Ownership: unverified. No known PE or franchise parent in our dataset as of {AS_OF}. "
            "That is not the same as confirmed independent."
        )
    kind = "Franchise" if row["ownership_status"] == "franchise" else "PE or platform-owned"
    return (
        f"{kind}: {row['ownership_parent']}. Matched on “{row['ownership_matched_term']}”. "
        f"{row.get('ownership_source_note') or ''}"
    )


def badge_html(row) -> str:
    if row["ownership_status"] == "platform_owned":
        own = '<span class="badge platform">PE or platform-owned</span>'
    elif row["ownership_status"] == "franchise":
        own = '<span class="badge franchise">Franchise</span>'
    else:
        own = '<span class="badge quiet">Ownership: unverified</span>'
    if row["heat_pump_signal"] == "mechanical_license_only":
        signal = '<span class="badge license">Mechanical license only</span>'
    else:
        signal = '<span class="badge">Heat pump program roster</span>'
    manuals = '<span class="badge quiet">Manual J: not in source</span>'
    rebates = "".join(f'<span class="badge">{esc(item["name"])}</span>' for item in row["rebate_programs"])
    return f'<p class="badges">{own}{signal}{manuals}{rebates}</p>'


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / "assets").mkdir()
    shutil.copy(ROOT / "assets" / "site.css", DIST / "assets" / "site.css")
    shutil.copy(ROOT / "assets" / "search.js", DIST / "assets" / "search.js")
    shutil.copy(ROOT / "assets" / "logo.svg", DIST / "favicon.svg")
    if SITE.get("publish_cname"):
        shutil.copy(ROOT / "CNAME", DIST / "CNAME")

    payload = load_json(ROOT / "data" / "listings.json")
    listings = payload["listings"]
    by_state, by_city = group_listings(listings)
    counts = {code: len(rows) for code, rows in by_state.items()}

    index = []
    for row in listings:
        index.append({
            "n": row["name"],
            "c": row["city"] if not row.get("outside_program_state") else f"{row['city']}, {row.get('address_region')}",
            "st": row["admin1_slug"],
            "sn": row["state_name"],
            "p": row["path"].lstrip("/"),
            "o": row["ownership_status"],
            "g": row["heat_pump_signal"],
            "sv": ", ".join(row["services"][:6]),
            "rb": " ".join(item["name"] for item in row["rebate_programs"]),
        })
    (DIST / "search-index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")

    write_home(counts)
    write_country(counts)
    write_states(by_state, by_city)
    write_cities(by_city)
    write_profiles(listings)
    write_static_pages(counts)
    write_sitemap(listings, by_city)
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {absolute('/sitemap.xml')}\n",
        encoding="utf-8",
    )
    (DIST / "404.html").write_text(
        shell("", f"Page not found | {NAME}", "That page is not on ElectrifyRadar.",
              f'''<div class="wrap prose"><h1>Page not found</h1>
              <p>That address is not in this directory. Try a <a href="us/">state page</a> or the <a href="./">home search</a>.</p></div>''',
              "/404.html"),
        encoding="utf-8",
    )
    print(f"Wrote {len(listings)} profiles and {len(by_city)} city pages to {DIST}")


def write_home(counts):
    cards = "".join(
        f'<a class="state-card" href="us/{code}/"><strong>{esc(STATES[code]["name"])}</strong><span>{counts.get(code, 0)} listings</span></a>'
        for code in STATES
    )
    body = f"""
<div class="wrap hero">
  <p class="eyebrow">United States · heat pumps and ductless mini-splits</p>
  <h1>Find the installer. See who owns them.</h1>
  <p class="lede">ElectrifyRadar lists heat pump contractors from public program rosters and one state license file. Each listing says Independent only when we have evidence. Right now the honest default is <strong>Ownership: unverified</strong>, unless the name matches a documented private-equity platform or franchise.</p>
</div>
<div class="wrap">
  <h2>Launch states</h2>
  <div class="state-grid">{cards}</div>
</div>
<div class="wrap">{search_block("")}</div>
<div class="wrap">
  <div class="split">
    <div class="prose">
      <h2>What this directory is for</h2>
      <p>Homeowners shopping for a heat pump or ductless mini-split usually get a lead form, a brand locator, or a star rating. None of those say whether the local truck is still a local company. Private-equity platforms and franchise brands buy and rebadge shops. The name on the door does not always say so.</p>
      <p>We publish the label we can support. A match against our sourced platform and franchise list becomes “PE or platform-owned” or “Franchise,” with the source linked on the profile. No match stays unverified. Nexstar membership is not treated as ownership.</p>
      <p><a href="us/guides/independent-vs-pe-hvac/">Why the ownership label matters</a> · <a href="us/guides/how-we-label-ownership/">How the label is decided</a></p>
    </div>
    <aside class="note">
      <p><strong>Manual J</strong> is the load calculation that sizes a heat pump to the house. None of the public files behind this launch state that an installer performed Manual J, so every listing says “Manual J: not in source.” <a href="us/guides/manual-j-load-calculation/">Read the Manual J guide</a>.</p>
    </aside>
  </div>
</div>
"""
    extra = f'<script src="{esc(rel_url("", "/assets/search.js"))}"></script>'
    write_page("/", shell("", f"{NAME} | Heat pump installers, with ownership in view",
                          "US directory of heat pump and ductless mini-split installers in Massachusetts, Maine, New York, California, and Minnesota. Ownership is labeled only from documented platform and franchise lists.",
                          body, "/", extra_script=extra))


def write_country(counts):
    total = sum(counts.values())
    items = "".join(
        f'<li><a href="{code}/">{esc(STATES[code]["name"])}</a> — {counts.get(code, 0)} listings</li>'
        for code in STATES
    )
    body = f"""
<div class="wrap prose">
  {crumbs("/us", [("Home", "/"), ("United States", "/us/")])}
  <h1>Heat pump installers in the United States</h1>
  <p class="lede">{total} listings across five launch states, built so another country or another trade can be added without renaming the URL pattern. Paths look like /us/ma/boston/name/.</p>
  <p>Canada and the UK are not in this release. Electric-vehicle charger installers are not either. The data model already has a country code and a category field so those can be added as their own rosters.</p>
  <ul>{items}</ul>
  <p><a href="guides/independent-vs-pe-hvac/">Independent, platform-owned, and franchise</a> · <a href="rebates/">Rebate guides</a></p>
</div>
"""
    write_page("/us/", shell("/us", f"US heat pump installer directory | {NAME}",
                             "State-by-state directory of heat pump installers with ownership labels for Massachusetts, Maine, New York, California, and Minnesota.",
                             body, "/us/"))


STATE_INTRO = {
    "ma": "Massachusetts listings come from the Mass Save Heat Pump Installer Network spreadsheet (file header: Revised 10-29-2026), the public download linked from the program’s finder. The file says participants provided EPA certification, Massachusetts insurance, and heat pump installation training. Mass Save says participation is not an endorsement and not a warranty of the work. Companies whose ZIP code is outside Massachusetts stay in this state section because they are on the Massachusetts roster, on a page titled with the mailing-address state.",
    "me": "Maine listings come from the Efficiency Maine Residential Registered Vendor locator, filtered to the Heat Pumps service, distance “any,” ZIP 04101, on 3 November 2026. The locator requires a ZIP. That search returned vendors as far as a few hundred miles from Portland, including some with mailing addresses in neighboring states. Efficiency Maine says registered vendors are independent of the program and that it does not endorse a provider. Installer emails shown in the locator are not republished.",
    "ny": "New York listings come from the NYS Clean Heat contractor finder. We used the same public search the site uses, limited to residential contractors offering ASHP installer, air-to-water heat pump installer, ground-source heat pump installer, or heat pump water heater installer services. Email addresses returned by that API are not republished. A jobs-completed field that is zero is not shown.",
    "ca": "California listings are contractors in the TECH Clean California file ContractorProjectData_2026-10-20 who have a city and a phone number. Phones come from a join to the California Contractors State License Board public classification downloads for C-20 (warm-air HVAC) and C-36 (plumbing), matched on license number. The full license lists are not published here. A C-20 license by itself is not treated as heat pump work. Contractors in the TECH file with no phone after that join are left out.",
    "mn": "Minnesota listings are businesses with an issued Mechanical Contractor Bond in the Minnesota Department of Labor and Industry public export, a Minnesota address, and a phone number. This is a mechanical contracting credential, not a heat-pump program roster. The page does not claim that each business installs heat pumps. Email addresses in the state file are not republished.",
}


def write_states(by_state, by_city):
    for code, meta in STATES.items():
        rows = by_state.get(code, [])
        cities = []
        for (state_slug, city_slug), group in sorted(by_city.items()):
            if state_slug != code:
                continue
            title = city_title(code, city_slug, group[0])
            cities.append((title, city_slug, len(group)))
        cities.sort(key=lambda item: (-item[2], item[0]))
        city_links = "".join(
            f'<li><a href="{esc(slug)}/">{esc(title)}</a> — {count}</li>'
            for title, slug, count in cities
        )
        own = defaultdict(int)
        for row in rows:
            own[row["ownership_status"]] += 1
        from_dir = f"/us/{code}"
        body = f"""
<div class="wrap">
  {crumbs(from_dir, [("Home", "/"), ("United States", "/us/"), (meta["name"], f"/us/{code}/")])}
  <p class="eyebrow">{esc(meta["code"])}</p>
  <h1>Heat pump installers in {esc(meta["name"])}</h1>
  <p class="lede">{len(rows)} listings. Ownership in this state: {own["unverified"]} unverified, {own["platform_owned"]} PE or platform-owned, {own["franchise"]} franchise.</p>
  <div class="prose"><p>{esc(STATE_INTRO[code])}</p>
  <p><a href="../rebates/{code}/">Rebate guide for {esc(meta["name"])}</a></p></div>
  {search_block(from_dir, code.upper())}
  <h2>Cities and mailing-address groups</h2>
  <ul>{city_links}</ul>
</div>
"""
        script = f'<script src="{esc(rel_url(from_dir, "/assets/search.js"))}"></script>'
        desc = f"{len(rows)} heat pump installer listings in {meta['name']}, with ownership labels and the public source behind each row."
        write_page(f"/us/{code}/", shell(from_dir, f"Heat pump installers in {meta['name']} | {NAME}", desc, body, f"/us/{code}/", extra_script=script))


def write_cities(by_city):
    for (state_slug, city_slug), rows in by_city.items():
        meta = STATES[state_slug]
        title = city_title(state_slug, city_slug, rows[0])
        from_dir = f"/us/{state_slug}/{city_slug}"
        path = f"/us/{state_slug}/{city_slug}/"
        cards = []
        item_list = []
        for position, row in enumerate(sorted(rows, key=lambda item: item["name"].lower()), start=1):
            profile = rel_url(from_dir, row["path"])
            place = row["city"] if not row.get("outside_program_state") else f"{row['city']}, {row.get('address_region')}"
            cards.append(
                f'<article class="card"><h3><a href="{esc(profile)}">{esc(row["name"])}</a></h3>'
                f'<p class="meta">{esc(place)}</p>{badge_html(row)}</article>'
            )
            item_list.append({
                "@type": "ListItem",
                "position": position,
                "url": absolute(row["path"]),
                "name": row["name"],
            })
        ld = json_ld({
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"Heat pump installers — {title}, {meta['name']}",
            "numberOfItems": len(rows),
            "itemListElement": item_list,
        })
        if city_slug.startswith("outside-"):
            heading = f"{title}, listed on the {meta['name']} roster"
            lede = f"These {len(rows)} businesses are on the {meta['name']} source used for this directory, and the address in that source is outside {meta['name']}."
        else:
            heading = f"Heat pump installers in {title}, {meta['name']}"
            lede = f"{len(rows)} listings with a {title} address in the public source for {meta['name']}."
        body = f"""
<div class="wrap">
  {crumbs(from_dir, [("Home", "/"), (meta["name"], f"/us/{state_slug}/"), (title, path)])}
  <h1>{esc(heading)}</h1>
  <p class="lede">{esc(lede)}</p>
  <div class="grid cards">{''.join(cards)}</div>
</div>
"""
        desc = f"{len(rows)} heat pump installer listings in {title}, {meta['name']}."
        write_page(path, shell(from_dir, f"{heading} | {NAME}", desc, body, path, extra_head=ld))


def write_profiles(listings):
    for row in listings:
        from_dir = row["path"].rstrip("/")
        path = row["path"]
        state_slug = row["admin1_slug"]
        meta = STATES[state_slug]
        city_path = f"/us/{state_slug}/{row['city_slug']}/"
        city_name = city_title(state_slug, row["city_slug"], row)
        phone = f'<a href="tel:{esc(row["phone"])}">{esc(row["phone"])}</a>' if row["phone"] else "Not in source"
        website = f'<a href="{esc(row["website"])}">{esc(row["website"])}</a>' if row["website"] else "Not in source"
        services = "".join(f"<li>{esc(item)}</li>" for item in row["services"]) or "<li>Not broken out in the source.</li>"
        programs = "".join(
            f'<li><a href="{esc(item["url"])}">{esc(item["name"])}</a></li>' for item in row["rebate_programs"]
        ) or "<li>None recorded. A missing badge is not a statement that the business is ineligible.</li>"
        licenses = []
        for lic in row["license_ids"]:
            bits = [esc(lic.get("authority") or ""), esc(lic.get("id") or "")]
            if lic.get("classification"):
                bits.append(esc(lic["classification"]))
            if lic.get("status"):
                bits.append("status " + esc(lic["status"]))
            licenses.append("<li>" + " · ".join(bit for bit in bits if bit) + "</li>")
        license_html = "".join(licenses) or "<li>Not in the source used here.</li>"
        sources = "".join(
            f'<li><a href="{esc(item["url"])}">{esc(item["name"])}</a> — checked {esc(item["retrieved"])}. {esc(item["note"])}</li>'
            for item in row["sources"]
        )
        extra_bits = []
        extra = row.get("extra") or {}
        if row["heat_pump_signal"] == "mechanical_license_only":
            extra_bits.append("<p class=\"note\">Minnesota DLI lists an issued mechanical contractor bond for this business. That file does not say the business installs heat pumps.</p>")
        if extra.get("tech_project_rows"):
            extra_bits.append(
                f"<p>TECH Clean California project rows for this contractor in the 20 October 2026 file: {esc(extra['tech_project_rows'])}. "
                f"Latest installation end date in that file: {esc(extra.get('tech_latest_installation_end') or 'not shown')}. This is a row count, not a rating.</p>"
            )
        if extra.get("counties_served"):
            extra_bits.append("<p>Counties served, as listed by Mass Save: " + esc(", ".join(extra["counties_served"])) + ".</p>")
        if extra.get("languages"):
            extra_bits.append("<p>Languages spoken, as listed by Mass Save: " + esc(", ".join(extra["languages"])) + ".</p>")
        if extra.get("property_types"):
            extra_bits.append("<p>Property types served, as listed by Mass Save: " + esc(extra["property_types"]) + ".</p>")
        if extra.get("hpln"):
            extra_bits.append("<p>Heat Pump Leaders Network field in the Mass Save file: " + esc(extra["hpln"]) + ".</p>")
        if extra.get("instant_rebate"):
            extra_bits.append("<p>Instant rebate field in the Mass Save file: " + esc(extra["instant_rebate"]) + ".</p>")
        if extra.get("diverse_business_type"):
            extra_bits.append("<p>Diverse business type, as reported in the Mass Save file: " + esc(extra["diverse_business_type"]) + ".</p>")
        address_line = ", ".join(
            part for part in [row.get("street") or "", row["city"], row.get("address_region") or row["admin1"], row.get("postal_code") or ""] if part
        )
        map_q = esc("https://www.google.com/maps/search/?api=1&query=" + quote(address_line))
        own_link = ""
        if row.get("ownership_source_url"):
            own_link = f' <a href="{esc(row["ownership_source_url"])}">Source</a>'
        ld = json_ld({
            "@context": "https://schema.org",
            "@type": "HVACBusiness",
            "name": row["name"],
            "url": absolute(path),
            "telephone": row["phone"] or None,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": row.get("street") or None,
                "addressLocality": row["city"],
                "addressRegion": row.get("address_region") or row["admin1"],
                "postalCode": row.get("postal_code") or None,
                "addressCountry": "US",
            },
            "areaServed": meta["name"],
        })
        if row.get("lat") and row.get("lng"):
            # geo is only included when the source API provided coordinates
            pass
        geo = ""
        if isinstance(row.get("lat"), (int, float)) and isinstance(row.get("lng"), (int, float)):
            geo = json_ld({
                "@context": "https://schema.org",
                "@type": "Place",
                "geo": {"@type": "GeoCoordinates", "latitude": row["lat"], "longitude": row["lng"]},
            })
        claim = rel_url(from_dir, "/claim/")
        correct = rel_url(from_dir, "/report-correction/")
        body = f"""
<div class="wrap">
  {crumbs(from_dir, [("Home", "/"), (meta["name"], f"/us/{state_slug}/"), (city_name, city_path), (row["name"], path)])}
  <p class="eyebrow">{esc(meta["name"])} · heat pump directory</p>
  <h1>{esc(row["name"])}</h1>
  <p class="meta">{esc(address_line)}</p>
  {badge_html(row)}
  <div class="note"><p>{esc(ownership_phrase(row))}{own_link}</p></div>
  <dl class="facts">
    <div><dt>Phone</dt><dd>{phone}</dd></div>
    <div><dt>Website</dt><dd>{website}</dd></div>
    <div><dt>Manual J</dt><dd>{esc(row["manual_j_note"])}</dd></div>
    <div><dt>Featured</dt><dd>No. Paid placement is not turned on.</dd></div>
  </dl>
  <h2>Services in the source</h2>
  <ul>{services}</ul>
  <h2>Rebate programs</h2>
  <ul>{programs}</ul>
  <h2>License or program id</h2>
  <ul>{license_html}</ul>
  {''.join(extra_bits)}
  <p><a href="{map_q}">Open this address in Google Maps</a></p>
  <h2>Where this row came from</h2>
  <ul>{sources}</ul>
  <h2>Ask for a quote</h2>
  <p>Quote requests are not sold, and this form does not send your details to the installer. It goes to {esc(EMAIL)} so we can see demand. Nothing is forwarded unless we later say so on this page.</p>
  <form action="mailto:{esc(EMAIL)}" data-subject="Quote request — {esc(row['name'])}">
    <input type="text" name="company_website" autocomplete="off" tabindex="-1" style="position:absolute;left:-9999px" aria-hidden="true">
    <label for="lead-name">Your name</label>
    <input id="lead-name" name="name" type="text" required>
    <label for="lead-contact">Email or phone</label>
    <input id="lead-contact" name="contact" type="text" required>
    <label for="lead-city">City</label>
    <input id="lead-city" name="city" type="text" value="{esc(row['city'])}">
    <label for="lead-note">What you need</label>
    <textarea id="lead-note" name="note"></textarea>
    <div class="actions"><button type="submit">Send request</button></div>
  </form>
  <p class="actions"><a class="button secondary" href="{esc(claim)}">Claim this listing</a> <a class="button secondary" href="{esc(correct)}">Report an ownership correction</a></p>
</div>
"""
        # own_link was escaped inside a paragraph that also escaped the sentence via esc(ownership_phrase) which would escape the link if concatenated wrong.
        # I inserted own_link AFTER esc(ownership_phrase) inside the same <p>, and own_link is raw HTML. But the paragraph uses esc() only on the phrase. Good.
        # Wait, look: {esc(ownership_phrase(row))}{own_link} — good.
        title = f"{row['name']} in {row['city']}, {row.get('address_region') or row['admin1']} | {NAME}"
        desc = f"{row['name']} in {row['city']}. {row['ownership_label']}. Source checked {AS_OF}."
        write_page(path, shell(from_dir, title, desc, body, path, extra_head=ld + geo))


def guide(slug, title, description, inner):
    return {
        "path": f"/us/guides/{slug}/",
        "from": f"/us/guides/{slug}",
        "title": title,
        "description": description,
        "inner": inner,
    }


def write_static_pages(counts):
    guides = guide_pages()
    index_items = "".join(
        f'<li><a href="{esc(page["path"].split("/us/guides/")[1])}">{esc(page["title"])}</a></li>'
        for page in guides
    )
    guide_index = f"""
<div class="wrap prose">
  {crumbs("/us/guides", [("Home", "/"), ("Guides", "/us/guides/")])}
  <h1>Guides</h1>
  <p>Practical pages for homeowners comparing heat pumps. Dollar figures appear only when an official page we checked on {esc(AS_OF)} stated them.</p>
  <ul>{index_items}</ul>
</div>
"""
    write_page("/us/guides/", shell("/us/guides", f"Heat pump guides | {NAME}",
                                    "Guides on heat pump cost, cold-climate performance, Manual J, rebates, and ownership.",
                                    guide_index, "/us/guides/"))
    for page in guides:
        body = f'''<div class="wrap prose">{crumbs(page["from"], [("Home", "/"), ("Guides", "/us/guides/"), (page["title"], page["path"])])}
        <h1>{esc(page["title"])}</h1>{page["inner"]}<p class="fine">Last checked {esc(AS_OF)}.</p></div>'''
        write_page(page["path"], shell(page["from"], f'{page["title"]} | {NAME}', page["description"], body, page["path"]))

    rebate_states = "".join(
        f'<li><a href="{code}/">{esc(STATES[code]["name"])}</a></li>' for code in STATES
    )
    rebates_index = f"""
<div class="wrap prose">
  {crumbs("/us/rebates", [("Home", "/"), ("Rebates", "/us/rebates/")])}
  <h1>Heat pump rebates</h1>
  <p>Rebate rules change. These pages quote official program sites checked on {esc(AS_OF)} and link back so you can confirm the current offer. This is not tax advice.</p>
  <ul>{rebate_states}</ul>
  <p>National overview: <a href="../guides/heat-pump-rebates/">how heat pump rebates are structured</a>.</p>
</div>
"""
    write_page("/us/rebates/", shell("/us/rebates", f"Heat pump rebates | {NAME}",
                                     "Heat pump rebate guides for Massachusetts, Maine, New York, California, and Minnesota, with official links and a last-checked date.",
                                     rebates_index, "/us/rebates/"))
    for code, meta in STATES.items():
        inner = REBATE_COPY[code]
        path = f"/us/rebates/{code}/"
        from_dir = f"/us/rebates/{code}"
        body = f'''<div class="wrap prose">{crumbs(from_dir, [("Home", "/"), ("Rebates", "/us/rebates/"), (meta["name"], path)])}
        <h1>Heat pump rebates in {esc(meta["name"])}</h1>{inner}
        <p><a href="../../{code}/">Installer listings in {esc(meta["name"])}</a></p>
        <p class="fine">Last checked {esc(AS_OF)}.</p></div>'''
        doc = shell(from_dir, f"Heat pump rebates in {meta['name']} | {NAME}",
                    f"Official heat pump rebate facts for {meta['name']}, checked {AS_OF}, with links to the program pages.",
                    body, path)
        write_page(path, doc)
        # Keyword alias /us/{state}/rebates/ points at the canonical rebate URL.
        alias_from = f"/us/{code}/rebates"
        alias_body = f'''<div class="wrap prose"><h1>Heat pump rebates in {esc(meta["name"])}</h1>
        <p>The rebate guide lives at <a href="{esc(rel_url(alias_from, path))}">{esc(absolute(path))}</a>.</p></div>'''
        alias = shell(alias_from, f"Heat pump rebates in {meta['name']} | {NAME}",
                      f"Rebate guide for {meta['name']}.",
                      alias_body, path)
        # canonical in shell uses `path` argument which we set to the canonical rebate path. Good.
        write_page(f"/us/{code}/rebates/", alias)

    about = f"""
<div class="wrap prose">
  <h1>About ElectrifyRadar</h1>
  <p>ElectrifyRadar is a directory of residential heat pump and ductless mini-split installers. The first release covers Massachusetts, Maine, New York, California, and Minnesota.</p>
  <p>The point of the site is ownership transparency. Other finders emphasize licenses, insurance, and quote requests. This one also says whether a published brand list identifies the business as platform-owned or a franchise. If we cannot support that, the label is “Ownership: unverified.” We do not mark a business independent without evidence.</p>
  <p>Listings are rebuilt from public program files and, for Minnesota, a public license export. Each profile names the source and the date it was checked. We do not invent installers, phone numbers, ratings, or counts.</p>
  <p>Paid featured listings are a field in the data and are turned off. The quote form emails the publisher. It is not a lead sold to a contractor.</p>
  <p>Contact <a href="mailto:{esc(EMAIL)}">{esc(EMAIL)}</a>.</p>
</div>
"""
    write_page("/about/", shell("/about", f"About | {NAME}", "What ElectrifyRadar publishes, and what it refuses to guess.", about, "/about/"))
    privacy = f"""
<div class="wrap prose">
  <h1>Privacy</h1>
  <p>ElectrifyRadar is a static site. Pages do not set analytics cookies and do not run a signed-in account.</p>
  <p>Forms on this site are delivered to {esc(EMAIL)} through Web3Forms, a form-to-email service, which processes what you type under its own privacy terms. The site itself does not store form entries, and we do not sell or share them with installers.</p>
  <p>Installer phone numbers and addresses are copied from public program rosters and public license files. Email addresses that appeared in those files are not republished.</p>
  <p>If you want a listing changed or removed, use <a href="../report-correction/">report a correction</a> or email {esc(EMAIL)}.</p>
</div>
"""
    write_page("/privacy/", shell("/privacy", f"Privacy | {NAME}", "How ElectrifyRadar handles forms and public installer records.", privacy, "/privacy/"))
    terms = f"""
<div class="wrap prose">
  <h1>Terms</h1>
  <p>Listings are summaries of public records as of {esc(AS_OF)}. Programs and licenses change. Confirm the contractor, the license, and any rebate with the program and the contractor before you sign a contract.</p>
  <p>An ownership label is a name match against a published list, not a finding from a company’s private books. “Unverified” means we did not find a documented platform or franchise parent. It is not a promise that the business is independent.</p>
  <p>Nothing on this site is an endorsement, a warranty of workmanship, or tax, legal, or energy-savings advice. Rebate amounts are quoted from the linked official pages and can change after the last-checked date.</p>
  <p>You may link to these pages. You may not scrape the site in order to resell the directory as a lead list.</p>
</div>
"""
    write_page("/terms/", shell("/terms", f"Terms | {NAME}", "Terms for using the ElectrifyRadar directory.", terms, "/terms/"))
    write_form_page(
        "/claim/",
        "Claim a listing",
        "Tell us you operate this business.",
        "Claim a listing",
        """<p>Claiming a listing is free. It does not buy placement. Email {email} with the business name, the listing URL, and a phone number or website we can match to the public record. We will not mark the business independent from a claim alone.</p>""",
    )
    write_form_page(
        "/report-correction/",
        "Report an ownership correction",
        "Tell us a platform, franchise, or independence label is wrong.",
        "Ownership correction",
        """<p>If a listing should be marked platform-owned or franchise, send the business name and a public source (a press release, the platform’s brand list, or the company’s own site). If you believe a platform label is wrong, send the same kind of source. We do not flip a label to “independent” on an email alone.</p>""",
    )


def write_form_page(path, heading, description, subject, intro):
    from_dir = path.rstrip("/")
    body = f"""
<div class="wrap prose">
  <h1>{esc(heading)}</h1>
  {intro.format(email=esc(EMAIL))}
  <form action="mailto:{esc(EMAIL)}" data-subject="{esc(subject)}">
    <input type="text" name="company_website" autocomplete="off" tabindex="-1" style="position:absolute;left:-9999px" aria-hidden="true">
    <label for="f-name">Your name</label>
    <input id="f-name" name="name" type="text" required>
    <label for="f-biz">Business name</label>
    <input id="f-biz" name="business" type="text" required>
    <label for="f-url">Listing URL, if you have it</label>
    <input id="f-url" name="listing_url" type="url">
    <label for="f-contact">Email or phone</label>
    <input id="f-contact" name="contact" type="text" required>
    <label for="f-detail">Details and source links</label>
    <textarea id="f-detail" name="details" required></textarea>
    <div class="actions"><button type="submit">Send</button></div>
  </form>
  <p>Or write directly to <a href="mailto:{esc(EMAIL)}">{esc(EMAIL)}</a>.</p>
</div>
"""
    write_page(path, shell(from_dir, f"{heading} | {NAME}", description, body, path))


def guide_pages():
    return [
        guide(
            "independent-vs-pe-hvac",
            "Why independent installers",
            "Why a homeowner comparing heat pump installers should be able to see platform and franchise ownership.",
            """
            <p>A heat pump quote is a long relationship with a company: the equipment, the refrigerant circuit, and whoever answers the phone in year six. Roll-ups buy local heating and cooling companies and often keep the local name. Franchise brands put a national trademark on a local owner. Neither fact is automatically bad work. Both are facts a homeowner cannot see on a star rating.</p>
            <p>ElectrifyRadar exists to show the fact when a public list supports it. The label is “PE or platform-owned” or “Franchise” only after a name match against a list we cite. Otherwise the label is “Ownership: unverified.” We do not print “Independent” just because a name missed the list.</p>
            <p>DealSeam’s July 2026 HVAC roll-up tracker, which we read on 3 November 2026, describes private equity as a large buyer of HVAC, plumbing, and electrical companies and points to outside sources (WSJ/PitchBook, IBISWorld, Forbes, Capstone Partners) for market counts. Those are DealSeam’s citations, not a census we performed. The tracker’s named platforms are the list we match. <a href="how-we-label-ownership/">How a name gets a label</a>.</p>
            <p>Coaching networks are not on that list. Nexstar, for example, describes itself as a network for contractors. We do not treat membership as private-equity ownership, and we do not publish a membership badge because we did not ingest a membership roster. See <a href="https://www.nexstarnetwork.com/about/">Nexstar’s about page</a>.</p>
            """,
        ),
        guide(
            "how-we-label-ownership",
            "How we label ownership",
            "The rules ElectrifyRadar uses before it calls an installer platform-owned, a franchise, or unverified.",
            """
            <p>Every listing starts as <strong>Ownership: unverified</strong>. That sentence means: no documented private-equity platform or franchise parent was matched in our dataset as of the date on the page. It does not mean we investigated the company’s owners, and it does not mean the company is independent.</p>
            <p>A listing becomes <strong>PE or platform-owned</strong> or <strong>Franchise</strong> only when the business name matches a term in our platform file. The file records the parent, the match term, the source URL, and the day we read the source. The profile links that source. The current source for platforms is <a href="https://dealseam.com/hvac-pe-rollup-tracker-2026">DealSeam’s 2026 PE roll-up tracker</a> (page last updated 28 July 2026; we read it 3 November 2026). Aire Serv is labeled a franchise because <a href="https://www.aireserv.com/">aireserv.com</a> describes Aire Serv as a Neighborly company whose work is done by franchise companies.</p>
            <p>Matches are conservative. “Comfort Systems” is a common local name and is not treated as Comfort Systems USA. “Champion” is not treated as Champions Group. “ARS” alone is not treated as Rescue Rooter. “Service Experts” counts only when the name starts with those words, so a sentence like “heating service experts” does not match. Nexstar is not a match term.</p>
            <p>We will set an independent label only after a public filing or the owner’s own statement shows no platform or franchise parent, and we record that source. No listing in this release has that label.</p>
            <p>Featured placement exists as a data flag and is false on every row. Paying for a label is not offered.</p>
            """,
        ),
        guide(
            "manual-j-load-calculation",
            "Manual J load calculation",
            "What a Manual J load calculation is, and why this directory does not award the badge unless a source says so.",
            """
            <p>Manual J is the Air Conditioning Contractors of America procedure for estimating a home’s heating and cooling load. The result is what a heat pump should be sized to. A unit that is too large short-cycles. A unit that is too small runs continuously and still misses the design temperature. Ductless heads in the wrong rooms have the same problem at the scale of one room.</p>
            <p>A serious installer can show the load calculation, the outdoor design temperature they used, and how the capacity at that temperature compares with the load. “We put in what the last house got” is not a load calculation.</p>
            <p>This directory has a Manual J field. It is true only when the public source says the installer performed or claimed Manual J. The Mass Save network file, the Efficiency Maine locator, the NYS Clean Heat finder, the TECH Clean California contractor file, and the Minnesota mechanical-bond export do not say that. Every launch listing therefore reads “Manual J: not in source.” An empty badge is not an accusation. It is the absence of a record.</p>
            """,
        ),
        guide(
            "heat-pump-installation-cost",
            "Heat pump installation cost",
            "Why ElectrifyRadar does not publish an unsourced heat pump installation price.",
            """
            <p>People search for a single heat pump installation cost. The public files behind this directory do not support one. A ductless single zone, a cold-climate ducted system with new ductwork, and a heat pump water heater are different projects. Electrical panel work may or may not be in the price.</p>
            <p>The TECH Clean California contractor file we publish from (ContractorProjectData_2026-10-20) does not include project cost. TECH’s separate anonymized installation datasets do, and those downloads are behind a request form on <a href="https://techcleanca.com/heat-pump-data/download-data/">TECH’s download page</a>. We did not ingest that file, so we do not reprint a cost range from it.</p>
            <p>What we can cite is an operating-cost comparison, not an install price. Efficiency Maine’s heat pump page, checked 3 November 2026, says its home heating cost comparison was current as of 11 September 2026 and lists these assumptions: propane at $3.20 a gallon, 93% combustion efficiency, 90% distribution efficiency, electricity at $0.26 per kWh, and a heat pump COP of 3.15 with 100% distribution efficiency. The page says your results may differ. See <a href="https://www.efficiencymaine.com/heat-pumps/">Efficiency Maine’s heat pump page</a>.</p>
            <p>Ask two or three installers for a price that names the equipment, the load calculation, electrical work, and what happens to the old furnace or boiler. Use the <a href="../rebates/">rebate guides</a> for the program that actually applies to the house.</p>
            """,
        ),
        guide(
            "cold-climate-heat-pumps",
            "Cold-climate heat pumps",
            "What cold-climate heat pump performance means in the northern launch states, using figures from program pages.",
            """
            <p>A cold-climate heat pump is sized and selected for capacity at a low outdoor temperature, not only for the mild-weather efficiency number on a yellow label. Capacity falls as the air outside gets colder. The useful question is whether the machine still covers the house at the design temperature, and what backs it up if it does not.</p>
            <p>Efficiency Maine’s heat pump page, checked 3 November 2026, says many heat pumps provide efficient heating down to −22°F or lower, regardless of windchill, and that Efficiency Maine rebates only the highest performing units. The same page says more than 200,000 heat pumps have been installed in Maine homes and businesses and that they are now more common than oil heat in new homes, citing the 2021 Maine New Construction Baseline Assessment. <a href="https://www.efficiencymaine.com/heat-pumps/">Read it on Efficiency Maine</a>.</p>
            <p>Minnesota’s residential heat pump rebate statute, as described by the Department of Commerce on the page checked 3 November 2026, defines an eligible heat pump for that state rebate as an ENERGY STAR certified, cold-climate rated air-source heat pump. Ground-source, air-to-water, and heat pump water heaters are called out as not eligible for that particular state rebate. <a href="https://mn.gov/commerce/energy/consumer/energy-programs/heat-pump.jsp">Minnesota program page</a>.</p>
            <p><a href="../../me/">Maine installers</a> · <a href="../../mn/">Minnesota listings</a> · <a href="../../ny/">New York installers</a></p>
            """,
        ),
        guide(
            "heat-pump-vs-furnace",
            "Heat pump vs furnace",
            "How a heat pump differs from a furnace, without an unsourced savings promise.",
            """
            <p>A furnace makes heat by burning fuel, or by electric resistance, and pushes it through ducts. A heat pump moves heat. In heating season it moves heat from outdoors in. In cooling season the same machine moves heat out. There is no flue on a heat-pump-only system.</p>
            <p>In a cold climate the comparison is not “heat pump versus a furnace that ran last year.” It is capacity at the design temperature, the backup you keep, the ductwork you already have, and the price of electricity versus the fuel you would have burned. Efficiency Maine publishes a comparison with stated fuel and electricity assumptions. Those assumptions are on our <a href="heat-pump-installation-cost/">cost page</a>, dated, and they are not a promise about your house.</p>
            <p>Some Mass Save Heat Pump Installer Network contractors also list conventional furnaces and boilers in the equipment field of the state file. That is a service the file records. It is not a recommendation to keep a furnace.</p>
            """,
        ),
        guide(
            "ductless-mini-split-installers",
            "Ductless mini-split installers",
            "What a ductless mini-split is, and where this directory shows installers who list that work.",
            """
            <p>A ductless mini-split is a heat pump with an outdoor unit and one or more indoor heads, connected by refrigerant lines, with no ducts. It is the usual retrofit where a house has radiators, baseboard, or no ductwork worth keeping. A ducted heat pump uses the same refrigeration cycle and sends air through ducts.</p>
            <p>The Mass Save network file has an equipment field. Contractors who checked “Ductless Air Source Heat Pumps” carry that phrase on their profile under services. The Efficiency Maine locator’s Heat Pumps category includes contractors who showed a heat pump service; the profile lists the services the locator printed for that vendor. NYS Clean Heat’s ASHP installer service covers air-source heat pumps, ducted and ductless, and the profile names the service the finder returned.</p>
            <p>We do not publish a ductless installation price. The files we used do not state one. Start with the city pages in <a href="../../ma/">Massachusetts</a>, <a href="../../me/">Maine</a>, and <a href="../../ny/">New York</a>, and ask for a load calculation. See <a href="manual-j-load-calculation/">Manual J</a>.</p>
            """,
        ),
        guide(
            "heat-pump-rebates",
            "Heat pump rebates",
            "How state heat pump rebates differ, and where to read the official page for each launch state.",
            """
            <p>There is no single national heat pump rebate with one dollar amount. A state program, a utility, a federal tax credit, and a local air-quality grant can stack, expire, or pause independently. This site keeps a page per launch state and a last-checked date.</p>
            <ul>
              <li><a href="../rebates/ma/">Massachusetts</a></li>
              <li><a href="../rebates/me/">Maine</a></li>
              <li><a href="../rebates/ny/">New York</a></li>
              <li><a href="../rebates/ca/">California</a></li>
              <li><a href="../rebates/mn/">Minnesota</a></li>
            </ul>
            <p>If a program page did not state a dollar amount on the day we checked it, the state page says so and links the official page instead of guessing.</p>
            """,
        ),
        guide(
            "best-heat-pump-brands",
            "Heat pump brands",
            "Why this site does not rank heat pump brands.",
            """
            <p>ElectrifyRadar does not publish a best-brands ranking. A ranking would need a method, a dataset, and a date. We do not have a test lab, and we do not take manufacturer placement.</p>
            <p>What a homeowner can verify: the equipment is on the rebate program’s qualified list, the capacity at the design temperature covers the Manual J load, and the installer is willing to name the model on the quote. Efficiency Maine points contractors and homeowners to its rebate-eligible equipment list from the <a href="https://www.efficiencymaine.com/at-home/residential-forms/">residential forms page</a>. Cold-climate criteria for the Minnesota state rebate are on the <a href="https://mn.gov/commerce/energy/consumer/energy-programs/heat-pump.jsp">Commerce program page</a>.</p>
            <p>An installer profile may later show an OEM affiliation when that affiliation comes from a public source. This release does not copy OEM locator results. Those sites generally prohibit scraping, and a brand badge is not an ownership label.</p>
            """,
        ),
    ]


REBATE_COPY = {
    "ma": """
    <p>Massachusetts heat pump incentives run through Mass Save. The installer network file we use (revised 29 October 2026, downloaded 3 November 2026) says contractors on the list provided EPA certification, insurance in Massachusetts, and heat pump installation training. The same disclaimer says the sponsors do not endorse the contractor or warrant the equipment.</p>
    <p>The heating-and-cooling incentives page we opened the same day is a program shell and did not state a single rebate dollar amount in the HTML we could read. We are not filling that gap with a number from somewhere else. Check the current offer on <a href="https://www.masssave.com/residential/rebates-and-incentives/heating-and-cooling">Mass Save’s heating and cooling incentives</a> and the <a href="https://www.masssave.com/residential/find-a-contractor/find-a-heat-pump-installer">heat pump installer finder</a>.</p>
    <p>The network file has its own “Instant rebate” and “HPLN” columns. Those values are copied onto installer profiles when the file contains them. They are the file’s fields, not a price quote.</p>
    """,
    "me": """
    <p>Efficiency Maine rebates heat pumps installed by a Residential Registered Vendor. The heat pump page checked 3 November 2026 says the program offers residential and commercial rebates, that many rebated units heat efficiently down to −22°F or lower, and that the program rebates only the highest performing units. It also says more than 200,000 heat pumps have been installed in Maine homes and businesses, citing the 2021 Maine New Construction Baseline Assessment.</p>
    <p>The residential rebate index checked the same day does not print one dollar figure. It links separate offers:</p>
    <ul>
      <li><a href="https://www.efficiencymaine.com/at-home/residential-rebates/">Residential heat pump rebates</a></li>
      <li><a href="https://www.efficiencymaine.com/heat-pumps/">Heat pumps overview</a></li>
      <li><a href="https://www.efficiencymaine.com/at-home/vendor-locator/">Find a registered vendor</a></li>
    </ul>
    <p>Use those pages for the current whole-home, mobile-home, low-income supplemental, and multifamily amounts. The operating-cost assumptions printed on the heat pump page (propane $3.20 per gallon, electricity $0.26 per kWh, heat pump COP 3.15, comparison dated 11 September 2026) are inputs to their calculator, not an installation price.</p>
    """,
    "ny": """
    <p>NYS Clean Heat is the statewide heat pump program behind the contractor finder this directory uses. The program site <a href="https://cleanheat.ny.gov/">cleanheat.ny.gov</a>, checked 3 November 2026, says rebates and financing are available and that NYS Clean Heat rebates can be combined with federal tax credits included in the Inflation Reduction Act. Federal credit rules change. Confirm the current credit before you rely on it. This page is not tax advice.</p>
    <p>The page we checked did not state a single rebate dollar amount. Utility-specific amounts live with the participating utilities (Central Hudson, Con Edison, National Grid, NYSEG, O&amp;R, and RG&amp;E are the program list returned by the finder). Start at <a href="https://www.nyserda.ny.gov/All-Programs/Heat-Pump-Program">NYSERDA’s heat pump pages</a> and <a href="https://nyscleanheat-findacontractor.icfsightline.com/">the contractor finder</a>.</p>
    """,
    "ca": """
    <p>TECH Clean California’s single-family incentives page, checked 3 November 2026, says these reservation statuses in its own words:</p>
    <ul>
      <li>As of 24 February 2026, HEEHRA single-family rebates are fully reserved statewide, and the program is no longer accepting new income-verification applications for single-family projects statewide. Unapproved requests, including those submitted after that date, are waitlisted.</li>
      <li>As of 7 January 2026, HEEHRA rebates for single-family homes in Central and Southern California are fully reserved, with the same waitlist rule.</li>
      <li>As of 14 November 2025, TECH Clean California single-family heat pump water heater and heat pump HVAC incentives are reserved statewide.</li>
      <li>As of 3 July 2025, 3CE incentives are fully reserved.</li>
    </ul>
    <p>A waitlisted project is eligible for a HEEHRA rebate only if the heat pump is installed after the reservation is approved, according to that page. TECH points Californians to <a href="https://www.switchison.org/">Switch Is On</a> for incentive lookup and says San Fernando Valley incentives tied to Aliso Canyon were expected in late summer 2026. Read the current page: <a href="https://techcleanca.com/incentives/single-family-incentives/">TECH single-family incentives</a>.</p>
    """,
    "mn": """
    <p>The Minnesota Department of Commerce residential heat pump rebate page, checked 3 November 2026, includes a status update dated 12 October 2026: Save Energy Minnesota has not launched. The state is waiting for formal US Department of Energy approval. There is no estimated launch date. The page says new federal rules change how the HEAR and HOMES rebates will work in Minnesota.</p>
    <p>The same page describes the state heat pump rebate this way:</p>
    <ul>
      <li>The applicant must receive a heat pump rebate through the federal Home Electrification and Appliance Rebate (HEAR) program. HEAR cannot approve a purchase made before approval. Commerce says it does not recommend delaying a necessary repair, and also says a pre-launch install is not eligible for the state rebate unless HEAR approves it first.</li>
      <li>The applicant owns and lives in the Minnesota residence. Owner-not-occupied multifamily units are not eligible.</li>
      <li>An auditor has to find the insulation and air sealing sufficient for a heat pump.</li>
      <li>For this program, “heat pump” means an ENERGY STAR certified, cold-climate rated air-source heat pump. Air-to-water heat pumps, ground-source heat pumps, heat pump dryers, and heat pump water heaters are listed as not eligible for the state rebate.</li>
      <li>The rebate amount will be the lesser of $4,000 or the total cost to purchase and install the heat pump minus the federal Home Energy Rebate and other rebates.</li>
      <li>The installer has to be on an approved contractor list that the page says will be released before launch. That list was not published on the day we checked. Our Minnesota names are mechanical-bond holders, not that future approved list.</li>
    </ul>
    <p>Source: <a href="https://mn.gov/commerce/energy/consumer/energy-programs/heat-pump.jsp">Minnesota Residential Heat Pump Rebate Program</a>. Questions on that page go to Residential.Rebates.COMM@state.mn.us.</p>
    """,
}


def write_sitemap(listings, by_city):
    paths = ["/", "/us/", "/us/guides/", "/us/rebates/", "/about/", "/privacy/", "/terms/", "/claim/", "/report-correction/", "/404.html"]
    for code in STATES:
        paths.append(f"/us/{code}/")
        paths.append(f"/us/rebates/{code}/")
        paths.append(f"/us/{code}/rebates/")
    for page in guide_pages():
        paths.append(page["path"])
    for state_slug, city_slug in by_city:
        paths.append(f"/us/{state_slug}/{city_slug}/")
    for row in listings:
        paths.append(row["path"])
    urls = []
    seen = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        loc = absolute(path if path.endswith(".html") else path)
        urls.append(f"  <url><loc>{esc(loc)}</loc><lastmod>{AS_OF}</lastmod></url>")
    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n" + "\n".join(urls) + "\n</urlset>\n"
    (DIST / "sitemap.xml").write_text(xml, encoding="utf-8")


if __name__ == "__main__":
    build()
