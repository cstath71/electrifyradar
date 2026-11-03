"""Full and stub guide bodies for ElectrifyRadar.

Imported by build_site.guide_pages(). Dollar amounts appear only when an
official page checked on AS_OF stated them; the prose always links that page.
"""

from __future__ import annotations


def full_guides(as_of: str):
    """Return the five expanded guides first, then remaining stubs."""
    return [
        _mass_save(as_of),
        _vet_installer(as_of),
        _efficiency_maine(as_of),
        _independent_vs_pe(as_of),
        _cold_climate(as_of),
        *_stubs(as_of),
    ]


def _g(slug, title, description, inner, faqs):
    return {
        "slug": slug,
        "title": title,
        "description": description,
        "inner": inner,
        "faqs": faqs,
    }


def _mass_save(as_of: str):
    faqs = [
        (
            "Whole-home vs partial-home — what’s the difference?",
            "On the Mass Save air-source heat pump page checked "
            f"{as_of}, whole-home rebates are for customers who install heat pumps as the sole source for heating and cooling. "
            "Partial-home rebates are for customers who keep an existing boiler or furnace to supplement a new heat pump system, "
            "and those projects generally need an integrated control from Mass Save’s Integrated Control Qualified Product List "
            "where propane, oil, or natural gas will remain in use. Basic rebates cover installs that are not displacing fossil fuel "
            "or electric resistance heat. Re-check "
            '<a href="https://www.masssave.com/residential/rebates-offers-services/heating-and-cooling/heat-pumps/air-source-heat-pumps">the official ASHP page</a> '
            "before you sign.",
        ),
        (
            "Do I need insulation done first?",
            "For the whole-home rebate, Mass Save requires the home to be sufficiently weatherized and a Whole-Home Heat Pump Verification Form "
            "to be completed and signed. Sufficient weatherization can be shown by at least one of: the home was built during or after 2000; "
            "a Home Energy Assessment report recommends less than $1,000 of weatherization; or weatherization recommendations made during or after "
            "2013 have been completed. Heat pumps that do not meet that weatherization rule may still be eligible for partial-home amounts. "
            "Partial-home projects can earn a $500 weatherization bonus when assessment and recommended weatherization fall in the window Mass Save publishes. "
            "Details are on "
            '<a href="https://www.masssave.com/residential/rebates-offers-services/heating-and-cooling/heat-pumps/air-source-heat-pumps">Mass Save’s ASHP page</a>.',
        ),
        (
            "Does my installer have to be on HPIN?",
            "Yes for these Mass Save air-source heat pump rebates. The program page states that equipment must be installed by a contractor participating "
            "in the Mass Save Heat Pump Installer Network. ElectrifyRadar’s "
            '<a href="../../ma/">Massachusetts directory</a> '
            "is built from that public network file (header Revised: 10-29-2026, checked "
            f"{as_of}). Confirm the company on "
            '<a href="https://www.masssave.com/residential/find-a-contractor/find-a-heat-pump-installer">Mass Save’s installer finder</a> '
            "before you rely on a listing.",
        ),
        (
            "Where do I check if my model is on the QPL?",
            "Mass Save requires ENERGY STAR Cold Climate equipment and points to the Mass Save Heat Pump Qualified Products List from "
            '<a href="https://www.masssave.com/residential/rebates-offers-services/heating-and-cooling/heat-pumps/air-source-heat-pumps">the ASHP rebate page</a>. '
            "Ask every bidder to write the exact outdoor and indoor model numbers and the AHRI reference number on the quote, then match those to the QPL yourself.",
        ),
        (
            "How does the Mass Save HEAT loan relate to the rebate?",
            "The rebate and the HEAT loan are separate paths. Mass Save’s program materials point homeowners to the HEAT loan portal at "
            '<a href="https://www.myheatloan.com/">myheatloan.com</a> '
            "for financing questions. Loan eligibility, rates, and whether a project can combine both change. Treat the portal and your HPIN contractor as the source of truth; this page is not lending advice.",
        ),
    ]
    inner = f"""
<p class="quick-answer"><strong>Quick answer.</strong> Mass Save air-source heat pump rebates in 2026 are tonnage-based (whole-home, partial-home, and basic), require ENERGY STAR Cold Climate equipment on the Mass Save Qualified Products List, and must be installed by a Heat Pump Installer Network (HPIN) contractor. The 2026 amounts published on Mass Save’s ASHP page (checked {as_of}) are $2,650 per ton up to $8,500 for whole-home, $1,125 per ton up to $8,500 for partial-home, and $250 per ton up to $2,500 for basic, with income-based enhanced incentives up to $16,000. Those figures change — re-check the official page before you sign. ElectrifyRadar lists HPIN contractors from the public network file.</p>

<h2>What Mass Save published for 2026 (and the 2027 cut)</h2>
<p>Figures below are copied from
<a href="https://www.masssave.com/residential/rebates-offers-services/heating-and-cooling/heat-pumps/air-source-heat-pumps">Mass Save’s Air Source Heat Pumps page</a>,
checked {as_of}. Tons are calculated from AHRI cooling capacity divided by 12,000 BTUs.</p>
<table>
  <thead><tr><th>Rebate type (2026)</th><th>Amount (as of Nov 2026)</th><th>Typical trigger</th></tr></thead>
  <tbody>
    <tr><td>Whole-home</td><td>$2,650 per ton, up to $8,500</td><td>Heat pumps as the sole heating and cooling source; weatherization rules apply</td></tr>
    <tr><td>Partial-home</td><td>$1,125 per ton, up to $8,500</td><td>Existing boiler or furnace kept as supplement; integrated controls where fossil fuel remains</td></tr>
    <tr><td>Basic</td><td>$250 per ton, up to $2,500</td><td>Not displacing fossil fuel or electric resistance (for example replacing an existing heat pump or conditioning a new addition)</td></tr>
    <tr><td>Income-based enhanced</td><td>Up to $16,000, or up to no cost through Turnkey Services</td><td>See MassSave.com/Enhanced; pre-existing fuel must be oil, propane, or electric resistance</td></tr>
  </tbody>
</table>
<p>Mass Save also states that for whole-home projects installed on or after 1 January 2027 the rebate falls to $2,350 per ton capped at $7,500, and for partial-home projects on or after that date it falls to $1,000 per ton capped at $7,500. Instant incentives may also be available through the New England Heat Pump Accelerator at
<a href="https://nehpa.org/">nehpa.org</a>; Mass Save notes that NEHPA is not administered by the Mass Save Sponsors.</p>

<h2>Steps before you sign a contract</h2>
<ol>
  <li><strong>Confirm your utility is a Mass Save sponsor</strong> for the fuel you are displacing. The ASHP page lists Cape Light Compact, Eversource, National Grid, and Unitil on the electric side, and Berkshire Gas, Eversource, Liberty, National Grid, and Unitil on the gas side. Municipal-gas rules differ for basic rebates — read the eligibility section on the official page.</li>
  <li><strong>Schedule a Home Energy Assessment</strong> and note weatherization recommendations. Whole-home rebates require sufficient weatherization and a signed Whole-Home Heat Pump Verification Form.</li>
  <li><strong>Get two or three HPIN bids.</strong> Mass Save recommends at least 2–3 contractors and publishes “Questions to Ask your Installer.” Start with ElectrifyRadar’s
  <a href="../../ma/">Massachusetts HPIN directory</a>
  (for example <a href="../../ma/cambridge/">Cambridge</a>, <a href="../../ma/worcester/">Worcester</a>, <a href="../../ma/springfield/">Springfield</a>, <a href="../../ma/newton/">Newton</a>) and confirm each name on the
  <a href="https://www.masssave.com/residential/find-a-contractor/find-a-heat-pump-installer">official finder</a>.
  Use our <a href="../questions-to-ask-heat-pump-installer/">vetting checklist</a>.</li>
  <li><strong>Confirm models on the QPL and AHRI match.</strong> Equipment must meet ENERGY STAR Cold Climate and appear on Mass Save’s Heat Pump Qualified Products List.</li>
  <li><strong>Choose whole-home, partial-home, or basic</strong> based on whether fossil backup stays. Partial-home projects that keep propane, oil, or natural gas on a zone need an integrated control from Mass Save’s Integrated Control QPL, set at or below the published switchover temperatures.</li>
  <li><strong>Install, then keep invoices and serial photos.</strong> Beginning 1 October 2026, Mass Save requires serial numbers on rebate applications, with a clear photo of each outdoor unit nameplate.</li>
  <li><strong>Submit by the published deadline.</strong> For equipment installed between 1 January 2026 and 31 December 2026, Mass Save says the rebate form and supporting documents must be received by 28 February 2027. Optional financing runs through the HEAT loan portal.</li>
</ol>

<h2>Checklist: what your quote must name</h2>
<ul>
  <li>Whole-home, partial-home, or basic — and why</li>
  <li>Exact outdoor and indoor model numbers plus AHRI reference</li>
  <li>Heating capacity at your town’s outdoor design temperature (see <a href="../manual-j-load-calculation/">Manual J</a>)</li>
  <li>Whether integrated controls are included (partial-home with fossil backup)</li>
  <li>Who pulls permits and who handles the rebate application</li>
  <li>What happens to the old furnace or boiler (disconnected, removed, or left as emergency backup)</li>
  <li>Electrical panel work, line sets, and condensate drainage as line items</li>
</ul>

<h2>Partial-home bonuses Mass Save listed</h2>
<p>Checked {as_of} on the same ASHP page: a $500 weatherization bonus when a Home Energy Assessment and recommended weatherization fall within one year before or up to six months after a partial-home install; and a $500 sizing bonus when heat pumps are sized to meet 90–120% of total heating load at the outdoor design temperature per ACCA Manual J across 100% of conditioned space. The heat pump rebate and each bonus must be applied for together through the online portal, with the load calculation attached for the sizing bonus.</p>

<h2>Find HPIN installers on ElectrifyRadar</h2>
<p>Our <a href="../../ma/">Massachusetts pages</a> republish the Mass Save HPIN spreadsheet (Revised: 10-29-2026). Short rebate facts also live on
<a href="../rebates/ma/">/us/rebates/ma/</a>.
Ownership labels follow our <a href="../../../methodology/">methodology</a>. Cold-climate sizing context is in
<a href="../cold-climate-heat-pumps/">cold-climate heat pumps</a>.</p>

<h2>Sources (as of Nov 2026)</h2>
<ul>
  <li><a href="https://www.masssave.com/residential/rebates-offers-services/heating-and-cooling/heat-pumps/air-source-heat-pumps">Mass Save — Air Source Heat Pumps</a> (rebate table, eligibility, 2027 changes, serial-number rule)</li>
  <li><a href="https://www.masssave.com/residential/find-a-contractor/find-a-heat-pump-installer">Mass Save — Find a Heat Pump Installer (HPIN)</a></li>
  <li><a href="https://nehpa.org/">New England Heat Pump Accelerator</a> (instant incentives note on the Mass Save page)</li>
  <li><a href="https://www.myheatloan.com/">Mass Save HEAT loan portal</a></li>
</ul>
"""
    return _g(
        "mass-save-heat-pump-rebate",
        "Mass Save heat pump rebate (2026): whole-home vs partial, QPL, and HPIN installers",
        "2026 Mass Save air-source heat pump rebates, HPIN rules, QPL equipment, and how to find qualifying Massachusetts installers. Figures dated Nov 2026 from Mass Save.",
        inner,
        faqs,
    )


def _vet_installer(as_of: str):
    faqs = [
        (
            "What is Manual J and why does it matter?",
            "Manual J is the Air Conditioning Contractors of America procedure for estimating a home’s heating and cooling load. "
            "A heat pump that is too large short-cycles; one that is too small runs constantly and can still miss design temperature. "
            "ElectrifyRadar marks Manual J on a listing only when a public source says the installer performed or claimed it — and none of the launch-state files say that. "
            "See our <a href=\"../manual-j-load-calculation/\">Manual J guide</a>.",
        ),
        (
            "How many quotes should I get?",
            "Mass Save’s air-source heat pump page recommends proposals from at least two or three Heat Pump Installer Network contractors. "
            "Use the same written questions for each bid so you can compare equipment, capacity at design temperature, and rebate paperwork side by side.",
        ),
        (
            "Should I care if the company is PE- or platform-owned?",
            "Ownership is a fact about who answers the phone in year six, not a star rating. ElectrifyRadar labels PE or platform-owned and Franchise only from cited public lists; otherwise the label is Ownership: unverified. "
            "Read <a href=\"../independent-vs-pe-hvac/\">independent vs PE-owned HVAC</a> and still compare Manual J bids either way.",
        ),
        (
            "Does a program badge (HPIN / Efficiency Maine / Clean Heat) guarantee quality?",
            "No. Program networks document training, insurance, or registration rules the sponsor publishes — Mass Save, for example, says HPIN participation is not an endorsement. "
            "Treat the badge as a rebate-eligibility filter, then interview the contractor with the checklist on this page.",
        ),
        (
            "What paperwork should I keep after install?",
            "Keep the signed contract, equipment model and serial numbers (photos of nameplates help), Manual J or load sheet, permit finals, warranty registration, and the rebate application confirmation. "
            "Mass Save applications filed on or after 1 October 2026 require outdoor-unit serial photos. Efficiency Maine asks for claims within six months of project completion.",
        ),
    ]
    inner = f"""
<p class="quick-answer"><strong>Quick answer.</strong> A serious heat pump bid names the equipment models, shows a Manual J (or equivalent) load calculation with your town’s design outdoor temperature, explains capacity at that temperature, states permits and electrical work, and says who handles rebate paperwork. Square-footage-only sizing is a red flag. Pull program-qualified installers from ElectrifyRadar’s state directories, then interview them with the same list.</p>

<h2>Steps</h2>
<ol>
  <li><strong>Gather house facts:</strong> recent utility bills, existing heat type, duct condition, electrical panel amp rating, and comfort problems by room.</li>
  <li><strong>Shortlist three program-roster installers</strong> in your city from
  <a href="../../ma/">Massachusetts (HPIN)</a>,
  <a href="../../me/">Maine (Efficiency Maine registered vendors)</a>,
  <a href="../../ny/">New York (NYS Clean Heat)</a>,
  <a href="../../ca/">California (TECH Clean California)</a>, or
  <a href="../../mn/">Minnesota (mechanical-bond listings)</a>.
  Confirm rebate eligibility on the matching
  <a href="../rebates/">rebate guide</a>.</li>
  <li><strong>Ask every bidder the same questions</strong> from the table below. ENERGY STAR’s HVAC Quality Installation bid comparison sheet is a useful parallel checklist.</li>
  <li><strong>Compare on paper,</strong> not on a hallway handshake. Reject bids that only quote “X tons for Y square feet.”</li>
  <li><strong>Verify license, insurance, and program registration</strong> on the official finder, not only on our copy of the roster.</li>
  <li><strong>Sign only when</strong> Manual J (or equivalent), model numbers, warranty terms, and rebate responsibilities are written into the contract.</li>
</ol>

<h2>Questions checklist</h2>
<table>
  <thead><tr><th>Question</th><th>Good answer</th><th>Red flag</th></tr></thead>
  <tbody>
    <tr><td>Did you run Manual J (or equivalent) for this house?</td><td>Yes — and they can show the load, rooms, and design outdoor temperature</td><td>“We size by square footage” or “same as the last job”</td></tr>
    <tr><td>What heating capacity do you claim at design temperature?</td><td>A BTU number at a stated outdoor °F, compared with the load</td><td>Only mild-weather efficiency talk (SEER2/HSPF2) with no cold capacity</td></tr>
    <tr><td>Exact models and AHRI reference?</td><td>Written on the quote; match your state’s QPL / ENERGY STAR Cold Climate list</td><td>“We’ll pick something equivalent later”</td></tr>
    <tr><td>Ducts or refrigerant layout?</td><td>Static pressure / duct plan, or head placement and line-set path</td><td>No site visit before the final number</td></tr>
    <tr><td>Permits and electrical?</td><td>Who pulls the permit; panel or circuit work as line items</td><td>Cash price that “skips the permit”</td></tr>
    <tr><td>Backup heat plan?</td><td>Clear statement: remove, disconnect, or integrated control with switchover temp</td><td>Vague “leave the furnace, you’ll be fine”</td></tr>
    <tr><td>Who files the rebate?</td><td>Named party, required photos/serials, and the program deadline</td><td>“You figure out the rebate”</td></tr>
    <tr><td>Who services this in year five?</td><td>Local dispatch path; ownership label on ElectrifyRadar if sourced</td><td>Pressure to sign today with no service story</td></tr>
  </tbody>
</table>
<p>ENERGY STAR publishes a printable HVAC Quality Installation bid sheet at
<a href="https://www.energystar.gov/sites/default/files/asset/document/HVAC_QI_bidsheet.pdf">energystar.gov (PDF)</a>.
Mass Save’s ASHP page also points to “Questions to Ask your Installer.”</p>

<h2>Where to find roster installers</h2>
<ul>
  <li><a href="../../ma/">Massachusetts HPIN listings</a> · rebates: <a href="../rebates/ma/">/us/rebates/ma/</a> · deep dive: <a href="../mass-save-heat-pump-rebate/">Mass Save guide</a></li>
  <li><a href="../../me/">Maine registered vendors</a> · <a href="../rebates/me/">Maine rebates</a> · <a href="../efficiency-maine-heat-pump-rebate/">Efficiency Maine guide</a></li>
  <li><a href="../../ny/">NYS Clean Heat contractors</a> · <a href="../rebates/ny/">NY rebates</a> · official finder: <a href="https://cleanheat.ny.gov/">cleanheat.ny.gov</a></li>
  <li><a href="../../ca/">California TECH contractors</a> · <a href="../rebates/ca/">CA incentives status</a></li>
  <li><a href="../../ct/">Connecticut Energize CT heat pump installers</a> · <a href="../rebates/ct/">CT rebate notes</a></li>
  <li><a href="../../ri/">Rhode Island Clean Heat RI installers</a> · <a href="../rebates/ri/">RI rebate notes</a></li>
  <li><a href="../../vt/">Vermont ductless specialists</a> · <a href="../rebates/vt/">VT rebate notes</a></li>
  <li><a href="../../mn/">Minnesota mechanical-bond listings</a> · <a href="../rebates/mn/">MN rebate status</a> (state approved-contractor list not published as of {as_of})</li>
</ul>
<p>Ownership rules: <a href="../how-we-label-ownership/">how we label ownership</a> · <a href="../../../methodology/">methodology</a>.</p>

<h2>What a written bid should include</h2>
<p>Ask for the following in the email or PDF before you pay a deposit. If an item is missing, ask for a revision rather than filling gaps from memory after the crew leaves.</p>
<ul class="checklist">
  <li>Site address and date of the visit</li>
  <li>Heating and cooling loads from Manual J (or equivalent), with the outdoor design temperature named</li>
  <li>Indoor and outdoor model numbers, and the AHRI reference if your rebate program needs it</li>
  <li>Heating capacity (BTU/h) at the design outdoor temperature, not only at 47 °F</li>
  <li>Whether the system is full displacement, partial displacement, or cooling-led with optional heat</li>
  <li>Electrical scope: panel work, new circuits, disconnects, who pulls the permit</li>
  <li>Duct sealing or refrigerant line-set path, length, and insulation</li>
  <li>Plan for the existing furnace, boiler, or oil tank</li>
  <li>Who files rebate paperwork, which photos or serials are required, and the claim deadline</li>
  <li>Parts, labor, and compressor warranty lengths in writing</li>
  <li>Service phone number and typical response window after the first heating season</li>
</ul>

<h2>How to run the same script on every bid</h2>
<p>Print or paste the questions table into a notes app. For each company, fill Bid A / Bid B columns in the meeting. Do not rely on a hallway summary. Mass Save’s air-source heat pump page recommends proposals from at least two or three Heat Pump Installer Network contractors; the same habit helps in Maine, New York, California, and Minnesota even when the program name differs.</p>
<table>
  <thead><tr><th>Item</th><th>Bid A</th><th>Bid B</th><th>Bid C</th></tr></thead>
  <tbody>
    <tr><td>On official finder? (yes/no + date checked)</td><td></td><td></td><td></td></tr>
    <tr><td>Load calc shared?</td><td></td><td></td><td></td></tr>
    <tr><td>Design outdoor °F</td><td></td><td></td><td></td></tr>
    <tr><td>Heating capacity at that °F</td><td></td><td></td><td></td></tr>
    <tr><td>Backup heat plan</td><td></td><td></td><td></td></tr>
    <tr><td>Electrical included?</td><td></td><td></td><td></td></tr>
    <tr><td>Rebate filing included?</td><td></td><td></td><td></td></tr>
    <tr><td>Labor warranty (years)</td><td></td><td></td><td></td></tr>
  </tbody>
</table>
<p>The lower total is not automatically the better system if one bid omitted electrical work, used a warmer design day, or left rebate filing to you.</p>

<h2>Red flags that deserve a second look</h2>
<ul>
  <li>No load calculation, or “we always install 3-ton units on this street.”</li>
  <li>Capacity discussed only at 47 °F in a cold-climate town — see <a href="../cold-climate-heat-pumps/">cold-climate heat pumps</a>.</li>
  <li>Pressure to sign the same day to “lock a rebate” without written terms.</li>
  <li>Company name on the quote that does not match the official finder.</li>
  <li>Refusal to name subcontractors or the electrical permit holder.</li>
  <li>Cash price that “skips the permit.”</li>
</ul>
<p>None of those alone proves a bad actor. Together they mean you should get another bid before you pay a deposit. Ownership labels on ElectrifyRadar (<a href="../how-we-label-ownership/">how we label ownership</a>) are facts about who owns the company when we have a source — not star ratings and not a substitute for the questions above.</p>

<h2>Where ElectrifyRadar helps — and where it stops</h2>
<p>We publish free directory pages built from official lists, with methodology notes and ownership labels when sourced. We do not sell leads, invent star ratings, or take payment to reorder names. After you shortlist from <a href="../../">state and city pages</a>, the interview is yours. For rebate amounts and rules, use the dated program pages linked from <a href="../rebates/">rebate guides</a>, including <a href="../mass-save-heat-pump-rebate/">Mass Save</a> and <a href="../efficiency-maine-heat-pump-rebate/">Efficiency Maine</a>.</p>

<h2>Sources (as of Nov 2026)</h2>
<ul>
  <li><a href="https://www.energystar.gov/sites/default/files/asset/document/HVAC_QI_bidsheet.pdf">ENERGY STAR HVAC Quality Installation bid comparison sheet (PDF)</a></li>
  <li><a href="https://www.masssave.com/residential/rebates-offers-services/heating-and-cooling/heat-pumps/air-source-heat-pumps">Mass Save ASHP page</a> (2–3 HPIN proposals; Questions to Ask your Installer)</li>
  <li><a href="https://www.acca.org/standards/technical-manuals">ACCA technical manuals</a> (Manual J overview)</li>
  <li><a href="https://www.efficiencymaine.com/at-home/vendor-locator/">Efficiency Maine vendor locator</a></li>
  <li><a href="https://cleanheat.ny.gov/">NYS Clean Heat</a></li>
</ul>
"""
    return _g(
        "questions-to-ask-heat-pump-installer",
        "Questions to ask a heat pump installer before you sign (Manual J, quotes, rebates)",
        "A homeowner checklist for vetting heat pump installers: Manual J, design temperature capacity, QPL models, permits, rebates, and ownership. No fake ratings.",
        inner,
        faqs,
    )


def _efficiency_maine(as_of: str):
    faqs = [
        (
            "Who must install the system for the rebate?",
            "Efficiency Maine’s residential heat pump rebate page states the system must be installed by an Efficiency Maine Residential Registered Vendor for heat pumps. "
            f"ElectrifyRadar’s <a href=\"../../me/\">Maine directory</a> is built from that locator (checked {as_of}). Confirm the vendor on "
            '<a href="https://www.efficiencymaine.com/at-home/vendor-locator/">Efficiency Maine’s vendor locator</a>.',
        ),
        (
            "Do multi-zone systems qualify?",
            "On the eligibility table Efficiency Maine published (checked "
            f"{as_of}), multi-zone heat pumps are listed as <strong>not</strong> rebate-eligible, though their design-temperature heating capacity can still count toward total heating capacity of all heat pumps. "
            "Single-zone units on Efficiency Maine’s list are rebate-eligible. Dual-fuel heat pump / furnace packages are not rebate-eligible and their capacity does not count. Re-read "
            '<a href="https://www.efficiencymaine.com/at-home/residential-heat-pump-rebates/">the official table</a> before you buy.',
        ),
        (
            "What does “primary heating system” mean if I keep oil or propane?",
            "The rebate page requires heat pumps to be used as the primary heating system throughout the heating season. For existing construction, any furnace or boiler must be reserved for emergency backup only — for example by turning thermostats all the way down, covering the power switch, or connecting the fossil system only to a generator. "
            "Primary systems can back you up in an emergency, but their heating capacity cannot be counted toward the 100% sizing requirement. New-construction rules tighten further on 1 January 2027 (no furnace or boiler).",
        ),
        (
            "How long do I have to submit the claim?",
            f"Efficiency Maine says the rebate claim form must be emailed or postmarked within six months of project completion (page checked {as_of}). Incomplete information can delay or disqualify the rebate.",
        ),
        (
            "Where do I find registered vendors near Portland, Bangor, or Augusta?",
            'Start on ElectrifyRadar city pages such as <a href="../../me/portland/">Portland</a>, <a href="../../me/bangor/">Bangor</a>, <a href="../../me/augusta/">Augusta</a>, and <a href="../../me/brunswick/">Brunswick</a>, then confirm each company on '
            '<a href="https://www.efficiencymaine.com/at-home/vendor-locator/">the official locator</a>.',
        ),
    ]
    inner = f"""
<p class="quick-answer"><strong>Quick answer.</strong> Efficiency Maine pays residential heat pump rebates only when a Residential Registered Vendor installs eligible equipment under current rules (income tiers, primary-heat use, and sizing). As of {as_of}, the program page lists up to $3,000 per rebate-eligible outdoor unit for low income (lifetime cap $9,000 per housing unit), $2,000 for moderate income (cap $6,000), and $1,000 for any income (cap $3,000). Multi-zone outdoor units are treated differently from single-zone on the rebate-eligible column — read the official table. Use our Maine directory to shortlist, then confirm on Efficiency Maine.</p>

<h2>Rebate amounts Efficiency Maine published</h2>
<p>Copied from
<a href="https://www.efficiencymaine.com/at-home/residential-heat-pump-rebates/">Residential Heat Pump Rebates</a>,
checked {as_of}. A housing unit means a dedicated kitchen, sleeping area, and bathroom. Amounts are per rebate-eligible outdoor unit, with lifetime caps per housing unit.</p>
<table>
  <thead><tr><th>Income pathway</th><th>Per outdoor unit</th><th>Lifetime limit per housing unit</th><th>How income is framed on the page</th></tr></thead>
  <tbody>
    <tr><td>Low income</td><td>$3,000</td><td>$9,000</td><td>Homeowner or household member participates in MaineCare, HEAP, SNAP, or TANF (verify on Efficiency Maine)</td></tr>
    <tr><td>Moderate income</td><td>$2,000</td><td>$6,000</td><td>AGI up to $70,000 individual / $100,000 joint (verify on Efficiency Maine)</td></tr>
    <tr><td>Any income</td><td>$1,000</td><td>$3,000</td><td>Homeowner of any income</td></tr>
  </tbody>
</table>
<p>Efficiency Maine’s heat pump overview also shows an example with two indoor units and states that your results may differ. Operating-cost assumptions on that overview (propane $3.20/gallon, electricity $0.26/kWh, heat pump COP 3.15, comparison dated 11 September 2026) are calculator inputs, not an installation price quote.</p>

<h2>Eligibility table (equipment)</h2>
<table>
  <thead><tr><th>Equipment</th><th>Rebate eligible?</th><th>Counts toward design-temp capacity?</th></tr></thead>
  <tbody>
    <tr><td>Single-zone heat pumps on Efficiency Maine’s list</td><td>Yes</td><td>Yes</td></tr>
    <tr><td>Multi-zone heat pumps</td><td>No</td><td>Yes</td></tr>
    <tr><td>Dual-fuel heat pump / furnace</td><td>No</td><td>No</td></tr>
  </tbody>
</table>
<p>Other rules on the same page (checked {as_of}): new and previously installed heat pumps sized for at least 80% of peak heating load; heat pumps plus supplemental heat sized for at least 100% of peak load; install per the Heat Pump Installation Requirements Checklist; building is owner’s principal residence for low- and moderate-income pathways; housing unit did not have a natural gas utility account before the upgrade; claim within six months.</p>

<h2>Steps</h2>
<ol>
  <li><strong>Verify income pathway</strong> for enhanced low- or moderate-income rebates if that applies.</li>
  <li><strong>Read the current rebate page</strong> —
  <a href="https://www.efficiencymaine.com/at-home/residential-heat-pump-rebates/">Residential Heat Pump Rebates</a> —
  on the day you sign. Programs change.</li>
  <li><strong>Hire a Residential Registered Vendor.</strong> Shortlist on
  <a href="../../me/">ElectrifyRadar’s Maine directory</a>,
  then confirm on the
  <a href="https://www.efficiencymaine.com/at-home/vendor-locator/">vendor locator</a>.</li>
  <li><strong>Ask sizing and rebate-in-quote questions</strong> from our
  <a href="../questions-to-ask-heat-pump-installer/">vetting guide</a>.
  Confirm single-zone vs multi-zone treatment against the official table.</li>
  <li><strong>Complete the upgrade</strong> with heat pumps as primary heat under Efficiency Maine’s backup rules.</li>
  <li><strong>Submit the claim form</strong> within six months. Efficiency Maine says to allow about six weeks for processing.</li>
</ol>

<h2>Find Maine installers</h2>
<p><a href="../../me/portland/">Portland</a> ·
<a href="../../me/bangor/">Bangor</a> ·
<a href="../../me/augusta/">Augusta</a> ·
<a href="../../me/brunswick/">Brunswick</a> ·
<a href="../../me/">all Maine listings</a> ·
short rebate page <a href="../rebates/me/">/us/rebates/me/</a> ·
cold-climate context <a href="../cold-climate-heat-pumps/">cold-climate heat pumps</a> ·
<a href="../../../methodology/">methodology</a>.</p>

<h2>Primary heat and backup rules in plain language</h2>
<p>Efficiency Maine’s rebate page (checked {as_of}) requires heat pumps to be used as the primary heating system throughout the heating season. For existing construction, any furnace or boiler that remains must be reserved for emergency backup only — for example by turning thermostats all the way down, covering the power switch, or connecting the fossil system only to a generator. Primary systems can back you up in an emergency, but their heating capacity cannot be counted toward the 100% sizing requirement. New-construction rules tighten further on 1 January 2027 (no furnace or boiler). Get the backup plan in writing on the quote so it matches how you will actually run the house.</p>

<h2>Sizing checklist before you sign</h2>
<ul class="checklist">
  <li>Peak heating load from a Manual J (or equivalent) with your town’s design outdoor temperature</li>
  <li>New and previously installed heat pumps sized for at least 80% of peak heating load</li>
  <li>Heat pumps plus supplemental heat sized for at least 100% of peak load</li>
  <li>Single-zone vs multi-zone treatment checked against Efficiency Maine’s eligibility table</li>
  <li>Dual-fuel heat pump / furnace packages treated as not rebate-eligible (capacity does not count)</li>
  <li>Install planned against Efficiency Maine’s Heat Pump Installation Requirements Checklist</li>
  <li>Housing unit has no natural gas utility account before the upgrade (rule on the rebate page)</li>
  <li>Principal-residence rules satisfied for low- and moderate-income pathways</li>
  <li>Claim calendar: email or postmark within six months of project completion</li>
</ul>

<h2>How ElectrifyRadar’s Maine list relates to the locator</h2>
<p>Our <a href="../../me/">Maine directory</a> is built from Efficiency Maine’s public registered-vendor data and dated on each page. It is a mirror for browsing by city — Portland, Bangor, Augusta, Brunswick, and the rest — not a replacement for the official locator. Before you sign, confirm the legal name on
<a href="https://www.efficiencymaine.com/at-home/vendor-locator/">Efficiency Maine’s vendor locator</a>.
Ownership labels on our profiles follow <a href="../how-we-label-ownership/">how we label ownership</a>; they are not Efficiency Maine badges. For interview questions that go beyond rebate paperwork, use
<a href="../questions-to-ask-heat-pump-installer/">questions to ask a heat pump installer</a>.
For cold-weather capacity language, see
<a href="../cold-climate-heat-pumps/">cold-climate heat pumps</a>.</p>

<h2>What we will not invent</h2>
<p>We do not invent average installed prices for Maine heat pumps, typical wait times for a specific town, or unofficial “stackable” rebate totals that Efficiency Maine has not published on the pages we cite. Operating-cost examples on Efficiency Maine’s overview use stated fuel and electricity assumptions; those are calculator inputs, not a promise about your bill. If a number is not on the official page on the day you check, we point you there instead of guessing.</p>

<h2>Sources (as of Nov 2026)</h2>
<ul>
  <li><a href="https://www.efficiencymaine.com/at-home/residential-heat-pump-rebates/">Efficiency Maine — Residential Heat Pump Rebates</a></li>
  <li><a href="https://www.efficiencymaine.com/at-home/vendor-locator/">Efficiency Maine — Vendor locator</a></li>
  <li><a href="https://www.efficiencymaine.com/heat-pumps/">Efficiency Maine — Heat pumps overview</a></li>
</ul>
"""
    return _g(
        "efficiency-maine-heat-pump-rebate",
        "Efficiency Maine heat pump rebate: eligibility, registered vendors, and how to apply",
        "Efficiency Maine residential heat pump rebate tiers, single-zone vs multi-zone rules, and registered vendors. Figures dated Nov 2026 from Efficiency Maine.",
        inner,
        faqs,
    )


def _independent_vs_pe(as_of: str):
    faqs = [
        (
            "Does PE ownership mean worse installs?",
            "No automatic conclusion. A private-equity or platform parent is a fact about ownership and incentives, not a workmanship score. "
            "Bad Manual J practice and high-pressure sales can appear in any ownership structure. Compare bids with our "
            '<a href="../questions-to-ask-heat-pump-installer/">vetting checklist</a>.',
        ),
        (
            "Why do so many listings say unverified?",
            f"As of {as_of}, most ElectrifyRadar rows have no sourced platform, franchise, or independent evidence on file. "
            "Unverified means we did not match a documented parent — it is not a promise the company is independent. See "
            '<a href="../how-we-label-ownership/">how we label ownership</a>.',
        ),
        (
            "Is Nexstar the same as private equity?",
            "No. Nexstar describes itself as a network for contractors. We do not treat membership as private-equity ownership, and we do not publish a membership badge because we did not ingest a membership roster. "
            'See <a href="https://www.nexstarnetwork.com/about/">Nexstar’s about page</a> and our <a href="../../../methodology/">methodology</a>.',
        ),
        (
            "Can a company pay for an “independent” badge here?",
            "No. Featured placement exists as a data flag and is false on every row. Paying for a label is not offered. An independent label requires a sourced quote from the company’s own site (family ownership with a year or generation, or a named owner-operator) plus a check that no sale turned up on the checked date.",
        ),
        (
            "How do I verify ownership myself?",
            "Read the ownership field and source link on the ElectrifyRadar profile, then open that source. For a second opinion, check the company’s own site, state business filings, and named platform brand lists such as "
            '<a href="https://dealseam.com/hvac-pe-rollup-tracker-2026">DealSeam’s HVAC PE roll-up tracker</a>. '
            "If a label looks wrong, use <a href=\"../../../report-correction/\">report a correction</a>.",
        ),
    ]
    inner = f"""
<p class="quick-answer"><strong>Quick answer.</strong> Private-equity and platform roll-ups buy local HVAC brands and often keep the old name. That is not automatically bad work — and it is not visible on star ratings. ElectrifyRadar labels <strong>PE or platform-owned</strong> or <strong>Franchise</strong> only from a cited public match list; otherwise <strong>Ownership: unverified</strong>. We do not print “Independent” without a source.</p>

<h2>What each label means</h2>
<table>
  <thead><tr><th>Label</th><th>What it means</th><th>What it does not mean</th></tr></thead>
  <tbody>
    <tr><td>PE or platform-owned</td><td>Business name matched a documented consolidator / PE-backed platform list we cite on the profile</td><td>Not a quality grade; not a claim about every truck in the fleet</td></tr>
    <tr><td>Franchise</td><td>Name matched a franchise brand we cite (for example Aire Serv as described on aireserv.com)</td><td>Not proof the local owner is good or bad at heat pumps</td></tr>
    <tr><td>Independent</td><td>Company’s own site states family ownership with a year/generation or names the owner-operator, and we recorded the quote</td><td>Not awarded just because a PE list missed the name</td></tr>
    <tr><td>Ownership: unverified</td><td>Default when no sourced platform, franchise, or independent evidence matched</td><td>Not a confirmation of independence</td></tr>
    <tr><td>Self-reported by the business</td><td>Optional dashed label after a reviewed claim-form answer</td><td>Does not replace a sourced label; not proof of independence</td></tr>
  </tbody>
</table>

<h2>Why homeowners ask</h2>
<p>DealSeam’s July 2026 HVAC roll-up tracker (page last updated 28 July 2026; we read it {as_of}) describes private equity as a large buyer of HVAC, plumbing, and electrical companies and cites outside sources such as WSJ/PitchBook, IBISWorld, Forbes, and Capstone Partners for market counts. Those are DealSeam’s citations, not a census ElectrifyRadar performed. The tracker’s named platforms are the list we match. Read
<a href="https://dealseam.com/hvac-pe-rollup-tracker-2026">the tracker</a>
and our
<a href="../../../platforms/">platforms page</a>.</p>
<p>Coaching networks are not on that list. Nexstar membership is not a match term.</p>

<h2>Steps when you compare local companies</h2>
<ol>
  <li>Search your city on ElectrifyRadar and open the ownership field plus its source link.</li>
  <li>Still collect Manual J quotes from two or three program-roster installers — ownership does not replace sizing. Use
  <a href="../questions-to-ask-heat-pump-installer/">questions to ask</a>.</li>
  <li>Ask who answers warranty and service calls in years five through ten.</li>
  <li>Compare bids on equipment, capacity at design temperature, and rebate paperwork regardless of ownership.</li>
  <li>If a label looks wrong, send a public source via
  <a href="../../../report-correction/">report a correction</a>
  or <a href="../../../claim/">claim a listing</a>.</li>
</ol>

<h2>Sales behavior vs ownership fact</h2>
<p>Homeowner forums often describe high-pressure same-day closes or tablet-only pitches. Those are sales behaviors you can screen for in an interview. They are separate from the ownership label. A locally owned shop can use hard sales tactics; a platform-owned shop can produce a careful Manual J. Judge the written bid.</p>

<h2>Related pages</h2>
<p><a href="../how-we-label-ownership/">How we label ownership</a> ·
<a href="../../../methodology/">Methodology</a> ·
<a href="../../../platforms/">PE platforms and franchise brands</a> ·
state hubs
<a href="../../ma/">MA</a>,
<a href="../../me/">ME</a>,
<a href="../../ny/">NY</a>,
<a href="../../ca/">CA</a>,
<a href="../../mn/">MN</a>.</p>

<h2>How a name gets a PE or franchise label here</h2>
<ol>
  <li>We start from the official program or license roster for the state (Mass Save HPIN, Efficiency Maine vendors, NYS Clean Heat, California TECH / CSLB, Minnesota mechanical-bond holders).</li>
  <li>We match the business name against documented consolidator / PE-backed platform lists we cite — primarily DealSeam’s HVAC PE roll-up tracker — or against franchise brand descriptions we cite (for example Aire Serv).</li>
  <li>On a match, the profile shows <strong>PE or platform-owned</strong> or <strong>Franchise</strong> with a source link. No match and no independent source quote means <strong>Ownership: unverified</strong>.</li>
  <li>An <strong>Independent</strong> label requires a sourced quote from the company’s own site (family ownership with a year or generation, or a named owner-operator) plus a check that no sale turned up on the checked date. Missing the PE list is not enough.</li>
  <li>Featured placement is a data flag and is false on every row. Paying for a label is not offered.</li>
</ol>
<p>Full rules live on <a href="../how-we-label-ownership/">how we label ownership</a> and the <a href="../../../methodology/">methodology</a> page. Platform brand names we track are summarized on <a href="../../../platforms/">platforms</a>.</p>

<h2>What to ask in the interview (ownership-aware)</h2>
<ul class="checklist">
  <li>Who owns the company today, and has ownership changed in the last five years?</li>
  <li>Who answers warranty and service calls in years five through ten?</li>
  <li>Is the crew on the quote employed by this legal entity or by a sibling brand?</li>
  <li>Will the contract, permits, and rebate filings use the same legal name as the official finder?</li>
  <li>Can they share Manual J, model numbers, and capacity at design temperature in writing?</li>
</ul>
<p>Those questions work the same whether the label is PE-platform, franchise, independent, or unverified. Ownership is context; the written bid is the decision. Use
<a href="../questions-to-ask-heat-pump-installer/">questions to ask a heat pump installer</a>
for the full sizing and rebate script.</p>

<h2>Neutral language we keep on purpose</h2>
<p>This guide does not name specific acquired companies as “bad,” does not invent market-share percentages, and does not treat private equity as automatically harmful. DealSeam and similar trackers are third-party compilations; we cite them as match lists, not as moral scorecards. If a homeowner forum story describes high-pressure sales, treat that as a sales-behavior screen you can run in an interview — separate from the ownership field on our profile pages.</p>

<h2>Sources (as of Nov 2026)</h2>
<ul>
  <li><a href="https://dealseam.com/hvac-pe-rollup-tracker-2026">DealSeam — HVAC PE roll-up tracker (2026)</a> (page last updated 28 July 2026)</li>
  <li><a href="https://www.nexstarnetwork.com/about/">Nexstar — About</a> (network ≠ PE match term)</li>
  <li><a href="https://www.aireserv.com/">Aire Serv</a> (franchise description used for the franchise label)</li>
  <li><a href="../../../methodology/">ElectrifyRadar methodology</a></li>
</ul>
"""
    return _g(
        "independent-vs-pe-hvac",
        "PE-owned vs independent HVAC: what homeowners should know (and how we label it)",
        "What PE or platform-owned, franchise, independent, and unverified mean on ElectrifyRadar — sourced labels only, no paid badges.",
        inner,
        faqs,
    )


def _cold_climate(as_of: str):
    faqs = [
        (
            "What temperature do cold-climate units work to?",
            "There is no single magic number for every product. Efficiency Maine’s heat pump page (checked "
            f"{as_of}) says many heat pumps provide efficient heating down to −22°F or lower, regardless of windchill, and that the program rebates only the highest performing units. "
            "ENERGY STAR’s cold-climate criteria (key product criteria page) include a COP at 5°F of at least 1.75 and heating capacity at 5°F of at least 70% of capacity at 47°F, among other metrics. "
            "Ask your installer for capacity at your town’s design temperature, not a viral video’s headline number.",
        ),
        (
            "Do I still need a furnace?",
            "It depends on load, capacity at design temperature, and program rules. Mass Save partial-home projects keep fossil backup with integrated controls; whole-home projects use heat pumps as the sole source. "
            "Efficiency Maine requires heat pumps as primary heat and limits how a furnace or boiler may remain for emergency backup. Get that plan in writing on the quote.",
        ),
        (
            "Mini-split vs ducted in a cold climate?",
            "Both can be cold-climate products. Ductless heads suit homes without useful ducts; ducted systems use the same refrigeration cycle through ducts. "
            "What matters is capacity at design temperature, head or register placement, and whether the equipment is on your rebate program’s qualified list. See "
            '<a href="../ductless-mini-split-installers/">ductless mini-split installers</a>.',
        ),
        (
            "Why do rebate programs care about cold-climate ratings?",
            "Northern programs want equipment that still delivers heat when outdoor temperatures drop. Mass Save requires ENERGY STAR Cold Climate equipment on its QPL. "
            "Minnesota’s state heat pump rebate page defines eligible equipment for that program as an ENERGY STAR certified, cold-climate rated air-source heat pump. "
            "Efficiency Maine rebates only its highest performing listed units.",
        ),
        (
            "Where do I find installers used to cold-climate jobs in my state?",
            'Use ElectrifyRadar’s <a href="../../me/">Maine</a>, <a href="../../mn/">Minnesota</a>, <a href="../../ma/">Massachusetts</a>, and <a href="../../ny/">New York</a> directories, then confirm program registration on the official finder linked from each '
            '<a href="../rebates/">rebate guide</a>.',
        ),
    ]
    inner = f"""
<p class="quick-answer"><strong>Quick answer.</strong> Cold-climate heat pumps are selected for heating capacity at a low outdoor design temperature, not only for mild-weather efficiency labels. Northern programs (Mass Save, Efficiency Maine, Minnesota’s cold-climate ASHP definition, NYS Clean Heat) already assume this class of equipment. Whether your house works depends on load calculation, capacity at design temperature, and backup — get that from an installer, not a viral video.</p>

<h2>What “cold climate” means in practice</h2>
<p>Capacity falls as outdoor air gets colder. The useful question is whether the machine still covers the Manual J load at your design temperature, and what backs it up if it does not. ENERGY STAR’s cold-climate designation for air-source heat pumps includes low-ambient performance tests (including COP and capacity retention at 5°F) on the
<a href="https://www.energystar.gov/products/heating_cooling/heat_pumps_air_source/key_product_criteria">key product criteria page</a>.</p>

<h2>State × program cues</h2>
<table>
  <thead><tr><th>State</th><th>Cold-climate cue on the program page</th><th>Our directory</th><th>Official starting point</th></tr></thead>
  <tbody>
    <tr>
      <td>Massachusetts</td>
      <td>Mass Save ASHP rebates require ENERGY STAR Cold Climate equipment on the Mass Save QPL (page checked {as_of})</td>
      <td><a href="../../ma/">/us/ma/</a></td>
      <td><a href="https://www.masssave.com/residential/rebates-offers-services/heating-and-cooling/heat-pumps/air-source-heat-pumps">Mass Save ASHP</a> · <a href="../rebates/ma/">rebate notes</a> · <a href="../mass-save-heat-pump-rebate/">full guide</a></td>
    </tr>
    <tr>
      <td>Maine</td>
      <td>Efficiency Maine says many units heat efficiently to −22°F or lower and rebates only highest performing listed units (checked {as_of})</td>
      <td><a href="../../me/">/us/me/</a></td>
      <td><a href="https://www.efficiencymaine.com/heat-pumps/">Efficiency Maine heat pumps</a> · <a href="../rebates/me/">rebate notes</a> · <a href="../efficiency-maine-heat-pump-rebate/">full guide</a></td>
    </tr>
    <tr>
      <td>Minnesota</td>
      <td>Commerce page (checked {as_of}; status update 12 October 2026): state rebate not launched yet; eligible “heat pump” for that future rebate means ENERGY STAR certified, cold-climate rated ASHP; $4,000 lesser-of amount is stated on the page</td>
      <td><a href="../../mn/">/us/mn/</a></td>
      <td><a href="https://mn.gov/commerce/energy/consumer/energy-programs/heat-pump.jsp">MN Commerce heat pump rebate</a> · <a href="../rebates/mn/">rebate notes</a></td>
    </tr>
    <tr>
      <td>New York</td>
      <td>NYS Clean Heat promotes heat pumps statewide with rebates and financing; utility-specific dollar amounts live with participating utilities (hub checked {as_of})</td>
      <td><a href="../../ny/">/us/ny/</a></td>
      <td><a href="https://cleanheat.ny.gov/">cleanheat.ny.gov</a> · <a href="../rebates/ny/">rebate notes</a></td>
    </tr>
  </tbody>
</table>
<p>Minnesota note: our Minnesota names are mechanical-bond holders from DLI, not the future approved-contractor list Commerce says will publish before launch. Do not treat a bond listing as state-rebate approval.</p>

<h2>Steps for a northern house</h2>
<ol>
  <li><strong>Find your climate / design temperature</strong> with the installer (Manual J design conditions for your town).</li>
  <li><strong>Require capacity at that temperature on the quote,</strong> compared with the heating load — see
  <a href="../questions-to-ask-heat-pump-installer/">questions to ask</a>.</li>
  <li><strong>Confirm program QPL / cold-climate rating</strong> for the exact models.</li>
  <li><strong>Decide backup strategy</strong> (remove, disconnect, integrated control, or emergency-only) under your program’s rules.</li>
  <li><strong>Pick roster installers</strong> in
  <a href="../../me/">ME</a>,
  <a href="../../mn/">MN</a>,
  <a href="../../ma/">MA</a>, or
  <a href="../../ny/">NY</a>.</li>
</ol>

<p>Efficiency Maine also reports that more than 200,000 heat pumps have been installed in Maine homes and businesses and that they are now more common than oil heat in new homes, citing the 2021 Maine New Construction Baseline Assessment
(<a href="https://www.efficiencymaine.com/heat-pumps/">heat pumps overview</a>, checked {as_of}).</p>

<h2>Design temperature beats brochure temperature</h2>
<p>Manufacturer tables often highlight capacity at 47 °F. Your town’s Manual J design temperature may be far colder. Ask the installer to circle the heating capacity (BTU/h) at that design temperature on the manufacturer’s extended performance table, then compare it with the calculated load. If capacity is short, the written plan should say whether you keep backup heat, add another head or outdoor unit, or accept a partial-displacement design. Square-footage rules of thumb skip this step.</p>

<h2>Checklist for a northern bid</h2>
<ul class="checklist">
  <li>Manual J (or equivalent) with outdoor design temperature named for your town</li>
  <li>Heating capacity at that temperature from the manufacturer table</li>
  <li>Full vs partial displacement stated in writing</li>
  <li>Backup furnace/boiler plan matches the rebate program’s primary-heat rules</li>
  <li>Equipment on the program’s qualified / cold-climate list (Mass Save QPL, Efficiency Maine list, MN ENERGY STAR cold-climate definition when that rebate launches, utility Clean Heat rules in NY)</li>
  <li>Defrost behavior and condensate / drain plan discussed for winter operation</li>
  <li>Electrical panel capacity checked for heat-pump plus any resistance backup</li>
  <li>Same questions asked of two or three program-roster installers</li>
</ul>

<h2>Where to shortlist installers used to cold winters</h2>
<p>Browse <a href="../../me/">Maine</a>, <a href="../../mn/">Minnesota</a>, <a href="../../ma/">Massachusetts</a>, and <a href="../../ny/">New York</a> city pages, then confirm each name on the official finder linked from the matching
<a href="../rebates/">rebate guide</a>.
Interview them with
<a href="../questions-to-ask-heat-pump-installer/">questions to ask a heat pump installer</a>.
For Mass Save dollar amounts and HPIN rules see
<a href="../mass-save-heat-pump-rebate/">Mass Save heat pump rebate</a>;
for Efficiency Maine tiers and registered vendors see
<a href="../efficiency-maine-heat-pump-rebate/">Efficiency Maine heat pump rebate</a>.
Ownership labels follow
<a href="../how-we-label-ownership/">how we label ownership</a>
and are not cold-climate performance scores.</p>

<h2>What viral videos skip</h2>
<p>A video filmed at one outdoor temperature is not a load calculation for your house. Windchill is not the same as the dry-bulb temperature used in capacity tables — Efficiency Maine’s heat pump page notes performance relative to air temperature regardless of windchill. We do not invent “works to −X °F” claims beyond what the cited program or ENERGY STAR criteria pages state. When a number is missing, we point you to the official page dated on this guide.</p>

<h2>Sources (as of Nov 2026)</h2>
<ul>
  <li><a href="https://www.efficiencymaine.com/heat-pumps/">Efficiency Maine — Heat pumps</a></li>
  <li><a href="https://mn.gov/commerce/energy/consumer/energy-programs/heat-pump.jsp">Minnesota Commerce — Residential Heat Pump Rebate Program</a></li>
  <li><a href="https://www.masssave.com/residential/rebates-offers-services/heating-and-cooling/heat-pumps/air-source-heat-pumps">Mass Save — Air Source Heat Pumps</a></li>
  <li><a href="https://cleanheat.ny.gov/">NYS Clean Heat</a></li>
  <li><a href="https://www.energystar.gov/products/heating_cooling/heat_pumps_air_source/key_product_criteria">ENERGY STAR — Heat pump key product criteria</a></li>
</ul>
"""
    return _g(
        "cold-climate-heat-pumps",
        "Do cold-climate heat pumps work in New England and Minnesota?",
        "How cold-climate heat pumps are defined by Mass Save, Efficiency Maine, Minnesota Commerce, NYS Clean Heat, and ENERGY STAR — with links to northern installer directories.",
        inner,
        faqs,
    )


def _stubs(as_of: str):
    # Remaining thin guides (unchanged substance; keep available on /us/guides/).
    return [
        _g(
            "how-we-label-ownership",
            "How we label ownership",
            "The rules ElectrifyRadar uses before it calls an installer platform-owned, a franchise, or unverified.",
            f"""
            <p>Every listing starts as <strong>Ownership: unverified</strong>. That sentence means: no documented private-equity platform or franchise parent was matched in our dataset as of the date on the page. It does not mean we investigated the company’s owners, and it does not mean the company is independent.</p>
            <p>A listing becomes <strong>PE or platform-owned</strong> or <strong>Franchise</strong> only when the business name matches a term in our platform file. The file records the parent, the match term, the source URL, and the day we read the source. The profile links that source. The current source for platforms is <a href="https://dealseam.com/hvac-pe-rollup-tracker-2026">DealSeam’s 2026 PE roll-up tracker</a> (page last updated 28 July 2026; we read it {as_of}). Aire Serv is labeled a franchise because <a href="https://www.aireserv.com/">aireserv.com</a> describes Aire Serv as a Neighborly company whose work is done by franchise companies.</p>
            <p>Matches are conservative. “Comfort Systems” is a common local name and is not treated as Comfort Systems USA. “Champion” is not treated as Champions Group. “ARS” alone is not treated as Rescue Rooter. “Service Experts” counts only when the name starts with those words, so a sentence like “heating service experts” does not match. Nexstar is not a match term.</p>
            <p>An independent label is used only when the company’s own site states family ownership with a year or generation, or names the owner-operator, and we record the quote and the page. A claim form answer is not that source. If we later publish what a business submitted, it is shown as self-reported by the business, in a different style from a sourced label. See the <a href="../../../methodology/">methodology</a>.</p>
            <p>Featured placement exists as a data flag and is false on every row. Paying for a label is not offered.</p>
            <p>Related: <a href="../independent-vs-pe-hvac/">PE-owned vs independent HVAC</a>.</p>
            """,
            [],
        ),
        _g(
            "manual-j-load-calculation",
            "Manual J load calculation",
            "What a Manual J load calculation is, and why this directory does not award the badge unless a source says so.",
            """
            <p>Manual J is the Air Conditioning Contractors of America procedure for estimating a home’s heating and cooling load. The result is what a heat pump should be sized to. A unit that is too large short-cycles. A unit that is too small runs continuously and still misses the design temperature. Ductless heads in the wrong rooms have the same problem at the scale of one room.</p>
            <p>A serious installer can show the load calculation, the outdoor design temperature they used, and how the capacity at that temperature compares with the load. “We put in what the last house got” is not a load calculation.</p>
            <p>This directory has a Manual J field. It is true only when the public source says the installer performed or claimed Manual J. The Mass Save network file, the Efficiency Maine locator, the NYS Clean Heat finder, the TECH Clean California contractor file, and the Minnesota mechanical-bond export do not say that. Every launch listing therefore reads “Manual J: not in source.” An empty badge is not an accusation. It is the absence of a record.</p>
            <p>Use the checklist in <a href="../questions-to-ask-heat-pump-installer/">questions to ask a heat pump installer</a>.</p>
            """,
            [],
        ),
        _g(
            "heat-pump-installation-cost",
            "Heat pump installation cost",
            "Why ElectrifyRadar does not publish an unsourced heat pump installation price.",
            f"""
            <p>People search for a single heat pump installation cost. The public files behind this directory do not support one. A ductless single zone, a cold-climate ducted system with new ductwork, and a heat pump water heater are different projects. Electrical panel work may or may not be in the price.</p>
            <p>The TECH Clean California contractor file we publish from (ContractorProjectData_2026-10-20) does not include project cost. TECH’s separate anonymized installation datasets do, and those downloads are behind a request form on <a href="https://techcleanca.com/heat-pump-data/download-data/">TECH’s download page</a>. We did not ingest that file, so we do not reprint a cost range from it.</p>
            <p>What we can cite is an operating-cost comparison, not an install price. Efficiency Maine’s heat pump page, checked {as_of}, says its home heating cost comparison was current as of 11 September 2026 and lists these assumptions: propane at $3.20 a gallon, 93% combustion efficiency, 90% distribution efficiency, electricity at $0.26 per kWh, and a heat pump COP of 3.15 with 100% distribution efficiency. The page says your results may differ. See <a href="https://www.efficiencymaine.com/heat-pumps/">Efficiency Maine’s heat pump page</a>.</p>
            <p>Ask two or three installers for a price that names the equipment, the load calculation, electrical work, and what happens to the old furnace or boiler. Use the <a href="../questions-to-ask-heat-pump-installer/">vetting checklist</a> and the <a href="../rebates/">rebate guides</a> for the program that actually applies to the house.</p>
            """,
            [],
        ),
        _g(
            "heat-pump-vs-furnace",
            "Heat pump vs furnace",
            "How a heat pump differs from a furnace, without an unsourced savings promise.",
            """
            <p>A furnace makes heat by burning fuel, or by electric resistance, and pushes it through ducts. A heat pump moves heat. In heating season it moves heat from outdoors in. In cooling season the same machine moves heat out. There is no flue on a heat-pump-only system.</p>
            <p>In a cold climate the comparison is not “heat pump versus a furnace that ran last year.” It is capacity at the design temperature, the backup you keep, the ductwork you already have, and the price of electricity versus the fuel you would have burned. Efficiency Maine publishes a comparison with stated fuel and electricity assumptions. Those assumptions are on our <a href="../heat-pump-installation-cost/">cost page</a>, dated, and they are not a promise about your house.</p>
            <p>Some Mass Save Heat Pump Installer Network contractors also list conventional furnaces and boilers in the equipment field of the state file. That is a service the file records. It is not a recommendation to keep a furnace.</p>
            <p>Related: <a href="../cold-climate-heat-pumps/">cold-climate heat pumps</a>.</p>
            """,
            [],
        ),
        _g(
            "ductless-mini-split-installers",
            "Ductless mini-split installers",
            "What a ductless mini-split is, and where this directory shows installers who list that work.",
            """
            <p>A ductless mini-split is a heat pump with an outdoor unit and one or more indoor heads, connected by refrigerant lines, with no ducts. It is the usual retrofit where a house has radiators, baseboard, or no ductwork worth keeping. A ducted heat pump uses the same refrigeration cycle and sends air through ducts.</p>
            <p>The Mass Save network file has an equipment field. Contractors who checked “Ductless Air Source Heat Pumps” carry that phrase on their profile under services. The Efficiency Maine locator’s Heat Pumps category includes contractors who showed a heat pump service; the profile lists the services the locator printed for that vendor. NYS Clean Heat’s ASHP installer service covers air-source heat pumps, ducted and ductless, and the profile names the service the finder returned.</p>
            <p>We do not publish a ductless installation price. The files we used do not state one. Start with the city pages in <a href="../../ma/">Massachusetts</a>, <a href="../../me/">Maine</a>, and <a href="../../ny/">New York</a>, and ask for a load calculation. See <a href="../manual-j-load-calculation/">Manual J</a> and <a href="../questions-to-ask-heat-pump-installer/">questions to ask</a>.</p>
            """,
            [],
        ),
        _g(
            "heat-pump-rebates",
            "Heat pump rebates",
            "How state heat pump rebates differ, and where to read the official page for each launch state.",
            """
            <p>There is no single national heat pump rebate with one dollar amount. A state program, a utility, a federal tax credit, and a local air-quality grant can stack, expire, or pause independently. This site keeps a page per launch state and a last-checked date.</p>
            <ul>
              <li><a href="../rebates/ma/">Massachusetts</a> · deep dive: <a href="../mass-save-heat-pump-rebate/">Mass Save heat pump rebate</a></li>
              <li><a href="../rebates/me/">Maine</a> · deep dive: <a href="../efficiency-maine-heat-pump-rebate/">Efficiency Maine heat pump rebate</a></li>
              <li><a href="../rebates/ny/">New York</a></li>
              <li><a href="../rebates/ca/">California</a></li>
              <li><a href="../rebates/ct/">Connecticut</a></li>
              <li><a href="../rebates/ri/">Rhode Island</a></li>
              <li><a href="../rebates/vt/">Vermont</a></li>
              <li><a href="../rebates/mn/">Minnesota</a></li>
            </ul>
            <p>If a program page did not state a dollar amount on the day we checked it, the state page says so and links the official page instead of guessing.</p>
            """,
            [],
        ),
        _g(
            "best-heat-pump-brands",
            "Heat pump brands",
            "Why this site does not rank heat pump brands.",
            """
            <p>ElectrifyRadar does not publish a best-brands ranking. A ranking would need a method, a dataset, and a date. We do not have a test lab, and we do not take manufacturer placement.</p>
            <p>What a homeowner can verify: the equipment is on the rebate program’s qualified list, the capacity at the design temperature covers the Manual J load, and the installer is willing to name the model on the quote. Efficiency Maine points contractors and homeowners to its rebate-eligible equipment list from the <a href="https://www.efficiencymaine.com/at-home/residential-forms/">residential forms page</a>. Cold-climate criteria for the Minnesota state rebate are on the <a href="https://mn.gov/commerce/energy/consumer/energy-programs/heat-pump.jsp">Commerce program page</a>.</p>
            <p>An installer profile may later show an OEM affiliation when that affiliation comes from a public source. This release does not copy OEM locator results. Those sites generally prohibit scraping, and a brand badge is not an ownership label.</p>
            """,
            [],
        ),
    ]
