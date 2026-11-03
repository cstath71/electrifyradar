# ElectrifyRadar

A static directory of heat pump and ductless mini-split installers in Massachusetts, Maine, New York, California, and Minnesota. The public label on each listing is ownership: unverified, PE or platform-owned, or franchise. “Independent” is not applied without a source.

The site is plain HTML. GitHub Actions builds `dist/` and publishes it to GitHub Pages on every push to `main`.

Live URL while the custom domain is not attached: `https://cstath71.github.io/electrifyradar/`

**One-time Pages switch.** The GitHub App that pushes this repo cannot create the Pages site (`POST /pages` returns 403 “Resource not accessible by integration”). The workflow build and tests pass; the deploy step fails until Pages exists. In the repo, open Settings → Pages → Build and deployment → Source → **GitHub Actions**, save, then re-run “Deploy to GitHub Pages” (or push any commit). After that, the same workflow publishes on every push to `main`.

Planned domain: `electrifyradar.com`. The repository root `CNAME` file contains that hostname. It is **not** copied into the Pages artifact until `publish_cname` is true in `config/site.json`. Publishing it earlier would make GitHub redirect the github.io URL to a domain that does not resolve yet. Internal links are relative, so the same HTML works at either host.

Contact: hello@electrifyradar.com

## What an operator runs

From the repository root, with Python 3.12:

```bash
pip install -r requirements.txt
python3 scripts/pipeline.py --fetch    # download sources, then rebuild
python3 scripts/pipeline.py            # rebuild from data/raw only
python3 -m unittest discover -s tests -v
python3 -m http.server -d dist 8080
```

`scripts/build_site.py` alone is what GitHub Actions runs. It reads the committed `data/listings.json` and does not call the source sites.

## Pipeline

| Step | Script | Output |
| --- | --- | --- |
| Download | `scripts/fetch_sources.py` | `data/raw/` (gitignored) |
| Normalize | `scripts/build_listings.py` | `data/listings.json`, `data/stats.json` |
| HTML | `scripts/build_site.py` | `dist/` |

`data/raw/` is not committed. After a fetch that changes the public set, commit the new `data/listings.json` and `data/stats.json`.

### Sources

Checked 2026-11-03.

| State | What is published | How it was obtained |
| --- | --- | --- |
| Massachusetts | Mass Save Heat Pump Installer Network. File header “Revised: 10-29-2026”. | The finder page links “Download the spreadsheet”: `https://www.masssave.com/-/media/Files/PDFs/Contractor-Lists/hpin-contractors.xlsx`. `robots.txt` disallows `/-/media/` for crawlers. The pipeline requests that one published export, not the media library. |
| Maine | Efficiency Maine Residential Registered Vendors with the Heat Pumps service. | The locator is a form. `fetch_sources.py` submits Heat Pumps, distance “any”, ZIP 04101 (the form requires a ZIP) and saves the HTML. Installer email addresses in the locator are not republished. |
| New York | NYS Clean Heat residential contractors offering ASHP, air-to-water, ground-source, or heat pump water heater installation. | The finder’s own `/api/contractor/search`. Email addresses are dropped before the file is written. |
| California | TECH Clean California contractors in `ContractorProjectData_2026-10-20`, one row per contractor name + CSLB number + city. | Public xlsx linked from the TECH contractor data page. Phone and license status are joined from CSLB classification downloads C-20 and C-36 on license number. Contractors with no phone after that join are omitted. The full license lists are not published. A C-20 license alone is not treated as heat pump work. |
| Minnesota | Issued Mechanical Contractor Bond, Minnesota address, phone present. | DLI CSV linked from the license lookup page. This is **not** a heat-pump program roster. Profiles say so. Email addresses are not republished. |

OEM dealer locators were not copied. Their terms generally prohibit scraping, and a brand badge is not an ownership label.

### Ownership

`data/ownership/platforms.json` is the only match list. A listing stays **Ownership: unverified** unless the business name matches a term in that file. Platform and franchise rows store the source URL. Nexstar is not a match term. The word “Independent” is not written onto a listing in this release.

Featured placement is a boolean on every row and is false. The quote form emails the publisher. It does not send the message to the installer and it is not a sold lead.

## Forms

Every form opens the visitor’s email program to hello@electrifyradar.com (a `mailto:` link). Nothing is stored on the site.

A hosted form endpoint is **not** connected. To replace mailto later, set `form_endpoint` in `config/site.json` and teach `scripts/build_site.py` to post there. Services that need an account before they work: Formspree, Getform, Web3Forms, Basin, or a Google Form. None of those accounts exist for this project yet.

## Custom domain

1. Buy `electrifyradar.com`.
2. At the DNS host, add the GitHub Pages records GitHub shows for a project site (usually a `CNAME` for `www` and `A`/`AAAA` records for the apex — use the values GitHub displays in the Pages settings, not a guess).
3. Set `publish_cname` to `true` and `canonical_origin` to `https://electrifyradar.com` in `config/site.json`.
4. Push to `main`. The next build copies `CNAME` into `dist/`, and GitHub will redirect the github.io URL to the custom domain.

## Adding a country or EV chargers

Listings already have `country_code` and `category` (`heat_pump` today). URLs are `/{country}/{admin1}/{city}/{slug}/`. `config/site.json` lists `future_countries` (`CA`, `GB`) and `future_categories` (`ev_charger`). A new roster is another builder function in `scripts/build_listings.py` plus a section in the templates. No EV data is included.

## Search and answer engines

`dist/llms.txt` and `dist/llms-full.txt` describe the method, sources, counts, and key URLs. `robots.txt` allows GPTBot, OAI-SearchBot, ChatGPT-User, PerplexityBot, ClaudeBot, Google-Extended, Applebot-Extended, and Bingbot. City pages with fewer than three listings are `noindex` and left out of the sitemap. Installer profiles stay in the sitemap.

`config/site.json` has empty `google_site_verification` and `msvalidate` hooks. DNS verification is already done, so leave them empty unless you also add an HTML-tag check.

After a deploy is live, ping IndexNow yourself (this is not part of CI):

```bash
python3 scripts/build_site.py
python3 scripts/indexnow.py --dry-run
python3 scripts/indexnow.py
```

## Tests

```bash
python3 scripts/build_site.py
python3 -m unittest discover -s tests -v
```
