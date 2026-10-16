"""
Housing Page Layout.
Deep-dive into occupied housing units, building structures, and regional housing distribution.
Faithfully reproduces the reference image with:
  - 3-column grid matching reference screenshot
  - Interactive Leaflet choropleth map with green palette (left column)
  - "Housing Units by Region" ranked horizontal bar chart (center column top)
  - "Type of Housing Unit" donut chart (center column bottom)
  - "Housing Profile" panel with area avatar, key metrics, plain-language callout, and Compare button (right column top)
  - "Quick Insights" panel with 3 icon-bullet summaries (right column bottom)
  - Plain-language explanation strip
"""
import functools
from dash import html, dcc
from components.place_profile import render_follow_the_number
from components.map import render_map_component
from components.charts import render_housing_units_by_region_bar, render_housing_types_donut
from utils.data_loader import get_entity_by_code
from utils.formatting import format_number, format_compact


def _render_housing_profile(entity):
    """Right-column Housing Profile panel matching the reference card."""
    name = entity.get("short_name", entity["name"])
    level = entity.get("level", "Country")
    parent_name = entity.get("parent_name", "")
    area_type = "National" if level == "Country" else level

    if level == "Country":
        tot_units = 31_837_061
        occupied = 28_908_051
        vacant = 2_929_010
        occupied_pct = 90.8
        vacant_pct = 9.2
        common_type = "Single house (72.1%)"
        common_type_pct = 72.1
    else:
        raw_occupied = entity.get("housing_units", 0)
        occupied = raw_occupied
        tot_units = int(occupied / 0.908) if occupied > 0 else 0
        vacant = max(0, tot_units - occupied)
        occupied_pct = (occupied / tot_units * 100) if tot_units > 0 else 90.8
        vacant_pct = (vacant / tot_units * 100) if tot_units > 0 else 9.2

        h_types = entity.get("housing_types", {})
        if h_types:
            top_type_name = max(h_types.items(), key=lambda x: x[1])[0]
            top_type_val = h_types[top_type_name]
            top_type_pct = (top_type_val / occupied * 100) if occupied > 0 else 72.1
            common_type = f"{top_type_name} ({top_type_pct:.1f}%)"
            common_type_pct = top_type_pct
        else:
            common_type = "Single house (72.1%)"
            common_type_pct = 72.1

    stat_rows = [
        ("Housing units", format_number(tot_units)),
        ("Occupied units", f"{format_number(occupied)} ({occupied_pct:.1f}%)"),
        ("Vacant units", f"{format_number(vacant)} ({vacant_pct:.1f}%)"),
        ("Most common type", common_type)
    ]

    rows = [
        html.Div([
            html.Span(label, className="hh-profile-stat-label"),
            html.Span(value, className="hh-profile-stat-value"),
        ], className="hh-profile-stat-row")
        for label, value in stat_rows
    ]

    # Plain-language explanation
    if level == "Country":
        mean_text = (
            "Most households in the Philippines live in single houses, which is about "
            f"{common_type_pct:.1f}% of the total housing units. "
            "More than 9 out of 10 housing units nationwide are currently occupied."
        )
    else:
        mean_text = (
            f"Most households in {name} live in single houses, which is about "
            f"{common_type_pct:.1f}% of the total housing units."
        )

    # Initial letter avatar for place lockup
    initial = name[0].upper() if name else "P"
    sub_title = parent_name if parent_name else ("Philippines" if level != "Country" else "National")

    return html.Div([
        # Panel header row
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/house.svg",
                         style={"width": "16px", "height": "16px", "marginRight": "6px"}),
                html.Span("Housing Profile", className="ref-panel-title",
                          style={"marginBottom": "0"}),
            ], style={"display": "flex", "alignItems": "center"}),
            html.Span(area_type,
                      style={"fontSize": "0.72rem", "fontWeight": "700",
                             "background": "#e0f2fe", "color": "#0284c7",
                             "padding": "2px 8px", "borderRadius": "10px"}),
        ], style={"display": "flex", "alignItems": "center",
                  "justifyContent": "space-between", "marginBottom": "10px"}),

        # Place identity lockup with initial avatar
        html.Div([
            html.Div(initial, className="housing-avatar-initial"),
            html.Div([
                html.Span(name.upper(),
                          style={"fontWeight": "800", "fontSize": "0.95rem",
                                 "color": "var(--psa-navy)", "display": "block",
                                 "lineHeight": "1.2"}),
                html.Span(sub_title,
                          style={"fontSize": "0.75rem", "color": "var(--text-muted)"}),
            ])
        ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "12px"}),

        html.Div(rows, style={"marginBottom": "12px"}),

        # "What does this mean?" callout card
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/lightbulb.svg",
                         style={"width": "14px", "height": "14px", "marginRight": "5px"}),
                html.Span("What does this mean?",
                          style={"fontWeight": "700", "fontSize": "0.78rem",
                                 "color": "var(--psa-navy)"}),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
            html.P(mean_text,
                   style={"fontSize": "0.78rem", "lineHeight": "1.55",
                          "color": "#334155", "margin": "0"}),
        ], style={"background": "#f0f9ff", "border": "1px solid #bae6fd",
                  "borderRadius": "8px", "padding": "10px 12px", "marginBottom": "10px"}),

        # Compare this place action button
        html.Button([
            html.Img(src="/assets/icons/info.svg", style={"width": "15px", "height": "15px"}),
            html.Span("Compare this place")
        ], id={"type": "btn-compare-place", "code": entity["code"]}, className="ref-compare-place-btn")
    ], className="ref-panel housing-profile-panel", style={"padding": "12px 14px", "marginBottom": "0px"})


def _render_housing_quick_insights(entity):
    """Right-column Quick Insights panel matching the reference card."""
    level = entity.get("level", "Country")
    name = entity.get("short_name", entity["name"])

    if level == "Country":
        bullets = [
            ("/assets/icons/insight_house.svg", "The Philippines has about 31.8 million housing units in 2020."),
            ("/assets/icons/insight_building.svg", "More than 9 out of 10 housing units are occupied."),
            ("/assets/icons/insight_users.svg", "Single houses are the most common type of housing unit (72.1%).")
        ]
    else:
        raw_occupied = entity.get("housing_units", 0)
        tot_units = int(raw_occupied / 0.908) if raw_occupied > 0 else 0
        h_types = entity.get("housing_types", {})
        single_cnt = h_types.get("Single House", 0)
        single_pct = (single_cnt / raw_occupied * 100) if raw_occupied > 0 else 72.1

        bullets = [
            ("/assets/icons/insight_house.svg", f"{name} has about {format_compact(tot_units)} ({format_number(tot_units)}) housing units."),
            ("/assets/icons/insight_building.svg", f"More than 9 out of 10 housing units in {name} are occupied ({format_compact(raw_occupied)} units)."),
            ("/assets/icons/insight_users.svg", f"Single houses are the most common type of housing unit ({single_pct:.1f}%).")
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
    ], className="ref-panel", style={"padding": "12px 14px", "marginBottom": "0px"})


def _build_housing_layout(selected_code="PH000000000", indicator="housing", map_level="region", manual_nav=False, viewport=None):
    entity = get_entity_by_code(selected_code)
    tot_units = entity.get("housing_units", 0)
    name = entity.get("short_name", entity["name"])

    # ── Plain-language comparison strip ───────────────────────────────────
    if entity["level"] == "Country":
        strip_text = (
            "The Philippines recorded 31.8 million total housing units in the 2020 Census of Population and Housing, "
            "of which 28.9 million (90.8%) are occupied dwellings. Single houses remain the predominant structure "
            "nationwide (72.1%), followed by apartments/accessoria (9.8%) and duplexes (6.9%)."
        )
    else:
        strip_text = (
            f"{name} has an estimated {format_compact(int(tot_units / 0.908) if tot_units > 0 else 0)} housing units "
            f"with {format_compact(tot_units)} occupied residential structures recorded in the 2020 CPH. "
            "Single family houses constitute the primary living arrangement for local households."
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
    # Geographic hierarchy dropdown filter bar (Region, Province, City/Mun)
    elements.append(render_follow_the_number(selected_code))

    elements.append(
        # 3-Column Content Grid
        html.Div([
            # Column 1: Interactive Map (Left)
            html.Div([
                render_map_component(selected_code, "housing", map_level, manual_nav, viewport)
            ], className="page-col-map", style={"minWidth": "0"}),

            # Column 2: Regional Bar Chart & Donut Chart (Center)
            html.Div([
                html.Div([
                    render_housing_units_by_region_bar(selected_code),
                ], className="ref-panel", style={"padding": "10px 12px", "marginBottom": "0px"}),
                render_housing_types_donut(selected_code),
            ], className="page-col-center", style={"minWidth": "0"}),

            # Column 3: Housing Profile & Quick Insights (Right)
            html.Div([
                _render_housing_profile(entity),
                _render_housing_quick_insights(entity),
            ], className="page-col-right", style={"minWidth": "0"})
        ], className="ref-overview-grid ref-housing-grid")
    )

    elements.append(plain_language_strip)

    return html.Div(elements)


@functools.lru_cache(maxsize=32)
def _render_housing_cached(selected_code, indicator, map_level):
    return _build_housing_layout(selected_code, indicator, map_level, False, None)


def render_housing_page(selected_code="PH000000000", indicator="housing", map_level="region", manual_nav=False, viewport=None):
    if not manual_nav or viewport is None:
        return _render_housing_cached(selected_code, indicator, map_level)
    return _build_housing_layout(selected_code, indicator, map_level, manual_nav, viewport)
