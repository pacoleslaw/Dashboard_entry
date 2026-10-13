---
name: psa-dashboard-builder
description: Build interactive, story-driven statistical dashboards from Philippine Statistics Authority (PSA) data as a single self-contained HTML file with PSA branding, a clickable choropleth map, and plain-language explanations. Make sure to use this skill whenever the user mentions PSA dashboards, census (CPH/POPCEN), Labor Force Survey, CBMS, OpenSTAT or other PSA indicators on a map, choropleth maps of the Philippines (region, province, city/municipality), statistical dashboard contests, "Philippines in Focus", or wants to turn PSA tables or shapefiles into an interactive page, even if they never say the word "dashboard".
---

# PSA Dashboard Builder

Build dashboards that let an ordinary person ask a question about a place, explore the map, and have official statistics explain what they are seeing. The target is a single, self-contained, interactive HTML file that can be published as a shareable link.

The difference between a good entry and a generic one is not more charts. It is that the map and charts drive each other, every number is explained in plain language, and every number can be traced back to a PSA source.

## Workflow

1. **Pin down the story.** Ask (or infer from the request) the one question the dashboard answers, e.g. "What does the Philippines look like, and how does my area compare?" Choose 4-6 headline indicators, not every available statistic. If the user has not named a dataset, propose one (the 2020 Census of Population and Housing is the cleanest start) and say why.
2. **Get real data.** Use files the user supplies first. Otherwise find the official PSA release (psa.gov.ph or openstat.psa.gov.ph) via search/fetch and record the exact table, reference period, and geographic level. Read `references/statistics-notes.md` before computing anything. Never type in figures from memory or copy them from a mockup image: mockups are illustrative and their numbers are often wrong. If a figure cannot be sourced, show an obvious placeholder and tell the user.
3. **Prepare geography.** Join data to boundaries by PSGC code, not by name. Match boundary vintage to data vintage. Simplify geometry so the file stays light (see `references/publishing-constraints.md`). If the user has no boundary file, ask for one; PSA/GMD staff usually have an authoritative set.
4. **Design the interaction model** (below), then build the single HTML file.
5. **Verify before delivering.** Check that selected-place totals add up to the parent total, that every indicator has a source note, that the map and charts stay in sync after each interaction type, and that the page works at phone width and in dark mode. Spot-check at least three numbers against the PSA source.
6. **Deliver.** Publish with the Artifact tool when it is available (see `references/publishing-constraints.md`), otherwise save the HTML to the outputs folder and present it. Summarize in two or three sentences: data source and reference period, what interactions exist, and anything left as a placeholder.

## Interaction model

These interactions are what make the dashboard feel like an exploration tool. Build as many as the story needs, but get the first two right before adding anything else.

- **Map drives charts.** Clicking a region, province, or city/municipality sets one shared "selected place" state. KPI cards, rankings, charts, insights, and breadcrumbs all re-render from that single state. Zoom the map to the selection.
- **Charts drive map.** Clicking a bar or table row in a ranking selects that place on the map and updates everything else. Build both directions from the same state object so they cannot drift apart.
- **Drill-down hierarchy.** Philippines > Region > Province > City/Municipality, with a breadcrumb that is also navigation. Always show the parent total next to the child so users see disaggregation ("Region IV-A: X of the national Y").
- **Map variable switcher.** A dropdown (population, households, density, average household size, growth) that recolors the map and rebuilds the legend. Use classed breaks that are readable (round numbers) and label units.
- **Place profile ("Tell me about this place").** On selection of a locality, show a short generated summary instead of 20 numbers: headline figure, change since the previous census, and two or three "what stands out" lines produced by rules from the data (rank within province, above/below the parent's average, fastest/slowest growth).
- **Compare two places.** A compare mode where picking Place A and Place B highlights both on the map and shows a side-by-side table of the same indicators.
- **Time slider** only when there are at least two real reference periods in the data. Do not fake a time series.
- **"Follow the number"** (optional flourish): clicking a headline figure animates the breakdown down the hierarchy to the user's local area.

## Plain language over jargon

Lead with a sentence a non-statistician would understand, then offer the technical definition behind an info tooltip ("What does this mean?").

- Instead of "Unemployment rate 4.5%": "About 5 out of every 100 people in the labor force were unemployed." Definition in a tooltip.
- Instead of "Growth rate 1.21%": "Population is growing by about 1.2% a year." Define the rate and period in the tooltip.
- Generate insight sentences from rules and the selected data, so they stay correct for every place. Avoid claims the data cannot support (no causal language like "because of migration").

## Source transparency

Every indicator gets a small source control with: PSA publication or dataset name, reference period, geographic level, and a link to the PSA page. Add a permanent "Data & Definitions" section covering sources, reference periods, definitions, methodology notes, boundary vintage, and last-updated date. Users must be able to verify any number. Only link to PSA URLs you have actually confirmed exist.

## Visual direction

Follow PSA branding: navy, white, and orange accents with Montserrat typography. If the user supplies a PSA template or brand guide, use its exact hex values and logo placement instead of the approximations in this skill. Do not embed a logo you do not have; leave a labelled slot for the user to drop it in.

Reference layout (adapt, do not copy blindly):

- Header band with PSA identity, dashboard title, one-line tagline.
- Left rail: section navigation (People, Households/Housing, Work, Progress) and filters (region, province, city/municipality, year).
- KPI row: 3-4 cards with the headline figure and change versus the previous period, each with a source control.
- Centerpiece: the choropleth map with legend, zoom controls, and hover tooltip.
- Supporting panels: ranking bar chart, one or two composition charts (donut or stacked bar), a small ranking table, a "Quick insights" panel, and a "Did you know?" callout.
- Footer: source line and link to the PSA website.

Design rules: one story, few indicators, generous whitespace, color used for meaning (sequential palette for counts, diverging only when there is a true midpoint). Never rely on color alone: include values in tooltips and labels. Keep text at readable sizes on mobile.

## Things that quietly go wrong

- Percent change of totals versus an annualized growth rate: label which one is shown.
- Average household size computed as total population / households overstates it (institutional population is excluded from household counts). Use the published figure.
- Names that look the same but differ across vintages (renamed or newly created provinces and LGUs). Join on PSGC and note the vintage.
- Choropleths of raw counts mislead because large areas dominate visually; offer density or rates, and say so in the legend.
- Share-of-total percentages that do not sum to 100 because of rounding or a hidden "Others" category: show "Others" explicitly.


---

<!-- references/publishing-constraints.md -->

# Building the single-file HTML dashboard

Read this before writing the page. A published page runs in a locked-down environment, and a dashboard that ignores these limits publishes but silently breaks.

## Contents
- Hard constraints
- Map approach
- State architecture
- Theming and mobile
- Delivery

## Hard constraints

- **One .html file**, CSS and JS inline, under 16 MB including data.
- **Scripts** may load only from cdnjs.cloudflare.com (preferred), cdn.jsdelivr.net/npm/, cdn.tailwindcss.com, and code.jquery.com. Use the UMD/browser-global build at an exact pinned version, placed before the inline script. Check that the library works as a script alone (no separate stylesheet needed).
- **Fonts**: Google Fonts stylesheet (fonts.googleapis.com) is allowed for Montserrat. Always give a fallback stack (`Montserrat, "Segoe UI", system-ui, sans-serif`) because fonts can fail to load.
- **No remote images, no map tiles, no runtime requests** to PSA or anywhere else. Everything the page shows is embedded at build time: data as inline JSON, geometry as inline GeoJSON/TopoJSON, images and logos as data: URIs.
- **No window.storage, no fetch to api.anthropic.com**. Those only work in the chat preview, not on a published page. Browser localStorage is available but optional; wrap every use in try/catch and render correctly when it is empty. Use it only for per-viewer conveniences (e.g. last selected tab).
- Downloads (e.g. "export CSV") need a runtime capability on a published page. Check the Artifact tool's capabilities action before promising a download button.

Because the data is a snapshot, state the "as of" date and reference period in the Data & Definitions section.

## Map approach

Draw the choropleth with SVG using d3-geo (pinned UMD from cdnjs) and inline TopoJSON/GeoJSON. No tile basemap, so the map needs no network.

- Project with `d3.geoMercator().fitSize([w, h], featureCollection)` and re-fit on selection to zoom. Animate with a CSS or d3 transition on the transform.
- Add a PSGC code to every feature's properties and join to the data by that key.
- **Simplify geometry.** Rough budgets: regions under ~300 KB, provinces under ~1 MB. City/municipality level for the whole country is large (1,600+ units), so simplify aggressively and quantize coordinates; or embed only the layer the current view needs (all regions + provinces, and municipalities grouped by province, rendered on demand from the inline data). Tools like mapshaper or topojson-server/topojson-simplify via npm can do the simplification in the build step; QGIS "Simplify" also works.
- Keep islands. Over-simplifying removes small islands and makes provinces look wrong; check visually, especially Palawan, Sulu, Batanes, and the Visayas.
- Provide a legend with classed breaks and units, a hover tooltip, keyboard focus on regions, and a reset-zoom control.
- Add a "no data / not available" fill, distinct from the lowest class.

## State architecture

Use one state object, for example `{ level, placeCode, compareCode, indicator, year }`, and one `render()` that redraws every panel from it. Map clicks, chart clicks, filter dropdowns, breadcrumb clicks, and the compare picker all just update the state and call `render()`. This is what guarantees the two-way interaction stays consistent.

Precompute parent/child relationships and rankings once at load.

## Theming and mobile

- Define colors as CSS variables on :root with a dark-mode override under `@media (prefers-color-scheme: dark)`, and give `body` an explicit background.
- Include `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">` and pad for safe-area insets.
- Collapse the left rail to a top menu on narrow screens; let wide tables scroll inside their own container, never the page body.

## Delivery

- Publish with the Artifact tool using the .html file path; republish the same file to update the same artifact. Keep the same favicon emoji when republishing.
- If publishing is unavailable, save to the outputs folder and present the file.


---

<!-- references/statistics-notes.md -->

# PSA statistics handling notes

Read before computing, labeling, or comparing any figures. When anything here conflicts with a figure or definition published by PSA, PSA's published version wins, and you should say which one you used.

## Contents
- Where to get data
- Reference periods
- Growth rates and changes
- Households and household size
- Geography and codes
- Honest presentation

## Where to get data

- PSA main site (psa.gov.ph) for official releases and press-release tables; OpenSTAT (openstat.psa.gov.ph) for downloadable tables by geography.
- Prefer the user's own files (Excel tables, boundary shapefiles) over anything you find online.
- Record for each table: title, release/publication, reference period, geographic level, and the URL you actually retrieved it from. These feed the source controls in the dashboard.
- Do not recall census figures from memory and do not reuse numbers shown in a mockup. Fetch or ask.

## Reference periods

Census reference dates differ and matter when annualizing:

- 2020 Census of Population and Housing (CPH): May 1, 2020
- 2015 Census of Population (POPCEN): August 1, 2015
- 2010 CPH: May 1, 2010

So 2015 to 2020 spans about 4.75 years, not 5. Labor Force Survey and other surveys have their own reference periods (monthly, quarterly, annual); show the period next to the figure.

## Growth rates and changes

- Distinguish **percent change over the period** from the **average annual growth rate**. Label whichever you display, and never write "+1.2% vs. 2015" if the number is an annual rate.
- State the formula and the number of years in the tooltip. Validate your computed rate against a rate PSA publishes for a known geography (for example the national rate) before using it everywhere; use PSA's published rate when one exists for that area.
- A change between two censuses is only comparable when the geography is the same; see below.

## Households and household size

- Use the published average household size. Total population divided by number of households is not the same thing, because household counts cover the household population and exclude institutional living quarters.
- Housing units, occupied housing units, and households are three different counts. Do not mix them in one ratio.

## Geography and codes

- Join on PSGC codes, never on names. Names get respelled, renamed, and duplicated.
- Check boundary vintage against data vintage. Administrative units have been created, split, renamed, or moved between regions across census years (for example, the 2022 split of Maguindanao into two provinces and the creation of the BARMM region, with its own boundary history). For multi-year comparisons, use a consistent geography or show only places that exist in both periods, and note it.
- Do not mix levels in one ranking (regions with provinces, for example).
- NCR has no provinces in the usual sense; decide deliberately how districts/cities are shown in the drill-down (typically city level under NCR).

## Honest presentation

- Show the data as published. Do not smooth, impute, or extrapolate. If a value is not available or suppressed, show "not available", never zero.
- Rankings and "Others": show an explicit "Others" bar when listing only the top N, and make sure shares sum sensibly. Note rounding.
- Generated insight text must be derived from the data in view: rank, share, difference from parent, direction of change. Avoid causal claims.
- Dashboards for official statistics should be neutral in tone. No advocacy language.
