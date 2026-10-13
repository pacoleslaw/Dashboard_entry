"""
Households Page Layout.
Deep-dive into household population, average household size, and occupant distributions.

Features:
  - 3-column aligned grid matching the reference design system
  - Column 1: Interactive Leaflet choropleth map for households
  - Column 2: Ranked "Households by Region" bar chart + "Household Size Distribution" donut chart
  - Column 3: "Household Profile" summary panel + "Quick Insights" highlights
  - Plain-language "What does this mean?" comparison strip
"""
import functools
from dash import html, dcc
from components.place_profile import render_follow_the_number
from components.map import render_map_component
from components.charts import render_household_size_donut, render_households_by_region_bar
from utils.data_loader import get_entity_by_code
from utils.formatting import format_number, format_compact


def _render_household_profile(entity):
    """Right-column Household Profile panel matching the reference card."""
    name = entity.get("short_name", entity["name"])
    level = entity["level"]
    tot_hh = entity.get("total_households", 0)
    avg_size = entity.get("avg_household_size", 0)
    hh_pop = entity.get("household_pop", 0)
    parent_share = entity.get("parent_share", 0)
    parent_name = entity.get("parent_name", "")
    nat_total_hh = get_entity_by_code("PH000000000").get("total_households", 1) or 1
    area_type = entity.get("area_type", "")
    if not area_type:
        area_type = "National" if level == "Country" else level

    stat_rows = [
        ("Households", format_number(tot_hh)),
        ("Avg. household size", f"{avg_size:.1f} persons"),
        ("Population per household",
         f"{hh_pop / tot_hh:.1f} persons" if tot_hh else "—"),
        ("Share of national HH",
         f"{tot_hh / nat_total_hh * 100:.1f}%"),
    ]
    if level != "Country" and parent_share:
        stat_rows.append(("Share of province/region", f"{parent_share:.1f}%"))

    rows = [
        html.Div([
            html.Span(label, className="hh-profile-stat-label"),
            html.Span(value, className="hh-profile-stat-value"),
        ], className="hh-profile-stat-row")
        for label, value in stat_rows
    ]

    # Plain-language household-size insight
    nat_avg = 4.1
    diff = avg_size - nat_avg
    if level == "Country":
        insight_text = (
            "On average, each Filipino household has 4.1 members in 2020. "
            "This is slightly lower than the 2015 average of 4.4, reflecting "
            "a long-term trend toward smaller family units across the country."
        )
    elif diff > 0.2:
        insight_text = (
            f"On average, each household in {name} has {avg_size:.1f} members — "
            f"larger than the national average of {nat_avg} persons per household. "
            "This may reflect multi-generational living arrangements common in this area."
        )
    elif diff < -0.2:
        insight_text = (
            f"On average, each household in {name} has {avg_size:.1f} members — "
            f"smaller than the national average of {nat_avg} persons per household, "
            "suggesting a higher proportion of single-person or nuclear family households."
        )
    else:
        insight_text = (
            f"On average, each household in {name} has {avg_size:.1f} members, "
            f"close to the national average of {nat_avg} persons per household (2020 CPH)."
        )

    return html.Div([
        # Panel header row
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/house.svg",
                         style={"width": "16px", "height": "16px", "marginRight": "6px"}),
                html.Span("Household Profile", className="ref-panel-title",
                          style={"marginBottom": "0"}),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Span(area_type,
                      style={"fontSize": "0.72rem", "fontWeight": "700",
                             "background": "#e0f2fe", "color": "#0284c7",
                             "padding": "2px 8px", "borderRadius": "10px"}),
        ], style={"display": "flex", "alignItems": "center",
                  "justifyContent": "space-between", "marginBottom": "10px"}),

        html.Div([
            html.Span(name,
                      style={"fontWeight": "800", "fontSize": "0.98rem",
                             "color": "var(--psa-navy)", "display": "block",
                             "marginBottom": "2px"}),
            html.Span(parent_name,
                      style={"fontSize": "0.75rem", "color": "var(--text-muted)"}),
        ], style={"marginBottom": "10px"}),

        html.Div(rows, style={"marginBottom": "10px"}),

        # What does this mean? block
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/lightbulb.svg",
                         style={"width": "14px", "height": "14px", "marginRight": "5px"}),
                html.Span("What does this mean?",
                          style={"fontWeight": "700", "fontSize": "0.78rem",
                                 "color": "var(--psa-navy)"}),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
            html.P(insight_text,
                   style={"fontSize": "0.78rem", "lineHeight": "1.55",
                          "color": "#334155", "margin": "0"}),
        ], style={"background": "#f8fafc", "border": "1px solid var(--border-color)",
                  "borderRadius": "8px", "padding": "10px 12px", "marginBottom": "10px"}),

        # Compare this place action button
        html.Button([
            html.Img(src="/assets/icons/compare.svg", style={"width": "15px", "height": "15px"}),
            html.Span("Compare this place")
        ], id={"type": "btn-compare-place", "code": entity["code"]}, className="ref-compare-place-btn")
    ], className="ref-panel hh-profile-panel", style={"padding": "12px 14px", "marginBottom": "0px"})


def _render_household_quick_insights(entity):
    """Right-column Quick Insights panel matching the reference card."""
    level = entity.get("level", "Country")
    name = entity.get("short_name", entity["name"])
    tot_hh = entity.get("total_households", 0)
    avg_size = entity.get("avg_household_size", 0.0)

    if level == "Country":
        bullets = [
            ("/assets/icons/insight_house.svg", "The Philippines recorded 26.4 million households in the 2020 CPH."),
            ("/assets/icons/insight_users.svg", "Average household size is 4.1 persons per household nationwide."),
            ("/assets/icons/insight_trend.svg", "Region IV-A (CALABARZON) has the largest household count with 4.1 million.")
        ]
    else:
        bullets = [
            ("/assets/icons/insight_house.svg", f"{name} has {format_compact(tot_hh)} ({format_number(tot_hh)}) enumerated households."),
            ("/assets/icons/insight_users.svg", f"Average household size in {name} is {avg_size:.1f} persons per household."),
            ("/assets/icons/insight_trend.svg", f"{name} accounts for {entity.get('nat_share', 0.0):.1f}% of total households in the Philippines.")
        ]

    return html.Div([
        html.Div([
            html.Img(src="/assets/icons/lightbulb.svg", alt="Insights", style={"width": "16px", "height": "16px"}),
            html.Span("Quick Insights", className="ref-panel-title", style={"marginBottom": "0"})
        ], style={"display": "flex", "alignItems": "center", "gap": "6px", "marginBottom": "10px"}),

        html.Div([
            html.Div([
                html.Div(
                    html.Img(src=icon_path, style={"width": "18px", "height": "18px"}),
                    className="ref-insight-icon-box"
                ),
                html.P(text, className="ref-insight-text")
            ], className="ref-insight-item")
            for icon_path, text in bullets
        ])
    ], className="ref-panel hh-quick-insights-panel", style={"padding": "12px 14px", "marginBottom": "0px"})


def _build_households_layout(selected_code="PH000000000", indicator="households", map_level="region", manual_nav=False, viewport=None):
    entity = get_entity_by_code(selected_code)
    tot_hh = entity.get("total_households", 0)
    avg_size = entity.get("avg_household_size", 0)
    name = entity.get("short_name", entity["name"])

    # ── Plain-language comparison strip ───────────────────────────────────
    nat_avg = 4.1
    diff = avg_size - nat_avg
    if entity["level"] == "Country":
        strip_text = (
            f"The Philippines has {format_number(tot_hh)} households as of the 2020 Census "
            f"(reference date: May 1, 2020). On average, each household has {avg_size:.1f} members — "
            "a slight decline from 4.4 in 2015, reflecting a continuing trend toward smaller family sizes."
        )
    elif diff > 0.2:
        strip_text = (
            f"{name} has {format_number(tot_hh)} households with an average of {avg_size:.1f} persons each — "
            f"above the national average of {nat_avg}. Larger households often reflect multi-generational "
            "living or the presence of extended family members in the same dwelling."
        )
    elif diff < -0.2:
        strip_text = (
            f"{name} has {format_number(tot_hh)} households with an average of {avg_size:.1f} persons each — "
            f"below the national average of {nat_avg}. Smaller households may indicate a greater share of "
            "single-person or couple-only units, often seen in highly urbanised areas."
        )
    else:
        strip_text = (
            f"{name} has {format_number(tot_hh)} households with an average of {avg_size:.1f} persons each, "
            f"close to the national average of {nat_avg} persons per household recorded in the 2020 CPH."
        )

    plain_language_strip = html.Div([
        html.Div([
            html.Img(src="/assets/icons/lightbulb.svg",
                     style={"width": "20px", "height": "20px",
                            "marginRight": "10px", "flexShrink": "0"}),
            html.Div([
                html.Span("What does this mean? ",
                          style={"fontWeight": "700", "color": "var(--psa-navy)",
                                 "marginRight": "4px"}),
                html.Span(strip_text, style={"color": "#334155"}),
            ]),
        ], style={"display": "flex", "alignItems": "flex-start"}),
    ], className="hh-plain-language-strip")

    # ── Final layout ──────────────────────────────────────────────────────
    elements = []
    if selected_code != "PH000000000":
        elements.append(render_follow_the_number(selected_code))

    elements.append(
        # 3-column content grid matching Overview & Population composition
        html.Div([
            # Column 1: Interactive Map (Left)
            html.Div([
                render_map_component(selected_code, "households", map_level, manual_nav, viewport)
            ], className="page-col-map", style={"minWidth": "0"}),

            # Column 2: Households Bar Chart & Donut Chart (Center)
            html.Div([
                html.Div([
                    render_households_by_region_bar(selected_code),
                ], className="ref-panel", style={"padding": "10px 12px", "marginBottom": "0px"}),
                render_household_size_donut(selected_code),
            ], className="page-col-center", style={"minWidth": "0"}),

            # Column 3: Household Profile & Quick Insights (Right)
            html.Div([
                _render_household_profile(entity),
                _render_household_quick_insights(entity),
            ], className="page-col-right", style={"minWidth": "0"})
        ], className="ref-overview-grid ref-households-grid")
    )

    elements.append(plain_language_strip)

    return html.Div(elements)


@functools.lru_cache(maxsize=32)
def _render_households_cached(selected_code, indicator, map_level):
    return _build_households_layout(selected_code, indicator, map_level, False, None)


def render_households_page(selected_code="PH000000000", indicator="households", map_level="region", manual_nav=False, viewport=None):
    if not manual_nav or viewport is None:
        return _render_households_cached(selected_code, indicator, map_level)
    return _build_households_layout(selected_code, indicator, map_level, manual_nav, viewport)
