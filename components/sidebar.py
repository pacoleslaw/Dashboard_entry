"""
Sidebar Component reproducing the exact left sidebar from the reference design.
Features:
- Full-height dark navy column
- Navigation items: Overview, People, Households, Housing, Demographics, Places, Compare Places, Data & Definitions
- Active indicator state matching the bright blue pill styling
- Clean Data Source section at the bottom
- Preserved hidden filter elements to prevent breaking any Dash callbacks
"""
import functools
from dash import html, dcc
from utils.geography import get_regions, get_provinces


@functools.lru_cache(maxsize=64)
def render_sidebar(active_page="overview", selected_region=None, selected_province=None):
    regions = get_regions()
    region_options = [{"label": "All Regions", "value": "ALL"}] + [
        {"label": r["name"], "value": r["code"]} for r in regions
    ]

    if selected_region and selected_region != "ALL":
        subunits = get_provinces(selected_region)
        prov_options = [{"label": "All Provinces", "value": "ALL"}] + [
            {"label": s["name"], "value": s["code"]} for s in subunits
        ]
    else:
        prov_options = [{"label": "All Provinces", "value": "ALL"}]

    primary_nav_items = [
        {"id": "nav-overview", "page": "overview", "icon": "/assets/icons/home.svg", "label": "Overview"},
        {"id": "nav-households", "page": "households", "icon": "/assets/icons/family.svg", "label": "Households"},
        {"id": "nav-housing", "page": "housing", "icon": "/assets/icons/house.svg", "label": "Housing"},
        {"id": "nav-demographics", "page": "people", "icon": "/assets/icons/demographics.svg", "label": "Demographics"}
    ]

    secondary_nav_items = [
        {"id": "nav-places", "page": "places", "icon": "/assets/icons/pin.svg", "label": "Places"},
        {"id": "nav-compare", "page": "compare", "icon": "/assets/icons/compare.svg", "label": "Compare Places"},
        {"id": "nav-definitions", "page": "definitions", "icon": "/assets/icons/definitions.svg", "label": "Data & Definitions"}
    ]

    def is_item_active(item_page, item_label):
        if item_label == "Overview" and active_page in ("overview", "population"):
            return True
        if item_label == "Households" and active_page == "households":
            return True
        if item_label == "Housing" and active_page == "housing":
            return True
        if item_label == "Demographics" and active_page in ("people", "demographics"):
            return True
        if item_label == "Places" and active_page == "places":
            return True
        if item_label == "Compare Places" and active_page == "compare":
            return True
        if item_label == "Data & Definitions" and active_page == "definitions":
            return True
        return False

    nav_options = [
        {"label": "Overview", "value": "overview"},
        {"label": "Households", "value": "households"},
        {"label": "Housing", "value": "housing"},
        {"label": "Demographics", "value": "people"},
        {"label": "Places", "value": "places"},
        {"label": "Compare Places", "value": "compare"},
        {"label": "Data & Definitions", "value": "definitions"}
    ]

    mobile_val = active_page
    if mobile_val == "demographics":
        mobile_val = "people"
    elif mobile_val == "population":
        mobile_val = "overview"

    return html.Aside([
        # Mobile-Only Quick Page Selector Dropdown
        html.Div([
            html.Div([
                html.Span("NAVIGATE", className="mobile-nav-title-text"),
                html.Span("Select a dashboard view", className="mobile-nav-sub-text")
            ], className="mobile-nav-label-box"),
            dcc.Dropdown(
                id="mobile-nav-page-select",
                options=nav_options,
                value=mobile_val,
                clearable=False,
                searchable=False,
                className="mobile-nav-dropdown"
            )
        ], className="mobile-nav-dropdown-bar"),

        # Scrollable Navigation Pill Bar Wrapper with Arrows
        html.Div([
            html.Button("‹", id="btn-nav-scroll-left", className="ref-nav-arrow-btn", title="Scroll left", n_clicks=0),
            html.Div([
                # 1. Primary Navigation Group
                html.Div([
                    html.Button([
                        html.Span(
                            html.Img(src=item["icon"], className="ref-nav-icon-img", alt=item["label"]),
                            className="ref-nav-icon"
                        ),
                        html.Span(item["label"], className="ref-nav-label")
                    ],
                    id={"type": "nav-btn", "page": item["page"], "source": f"sidebar-{item['id']}"},
                    className=f"ref-nav-btn {'active' if is_item_active(item['page'], item['label']) else ''}",
                    n_clicks=0
                    )
                    for item in primary_nav_items
                ], className="ref-nav-list"),

                # Spacing between groups (hidden on mobile/tablet)
                html.Div(className="ref-sidebar-group-gap"),

                # 2. Secondary Exploration Group
                html.Div([
                    html.Button([
                        html.Span(
                            html.Img(src=item["icon"], className="ref-nav-icon-img", alt=item["label"]),
                            className="ref-nav-icon"
                        ),
                        html.Span(item["label"], className="ref-nav-label")
                    ],
                    id={"type": "nav-btn", "page": item["page"], "source": f"sidebar-{item['id']}"},
                    className=f"ref-nav-btn {'active' if is_item_active(item['page'], item['label']) else ''}",
                    n_clicks=0
                    )
                    for item in secondary_nav_items
                ], className="ref-nav-list")
            ], id="ref-nav-scroll-container", className="ref-nav-section"),
            html.Button("›", id="btn-nav-scroll-right", className="ref-nav-arrow-btn", title="Scroll right", n_clicks=0),
        ], className="ref-nav-scroll-wrapper"),

        # 3. Bottom Data Source Section (matching reference design)
        html.Div([
            html.Div("DATA SOURCE", className="ref-source-badge-title"),
            html.Div("Philippine Statistics Authority", className="ref-source-agency"),
            html.Div("2020 Census of Population and Housing", className="ref-source-subtitle"),
            html.A([
                html.Img(src="/assets/icons/datasource.svg", style={"width": "12px", "height": "12px", "filter": "brightness(0) invert(1)"}),
                html.Span("View PSA Source"),
                html.Span("→", style={"fontSize": "0.85rem", "fontWeight": "600"})
            ],
            href="https://psa.gov.ph/content/age-and-sex-distribution-philippine-population-2020-census-population-and-housing",
            target="_blank",
            rel="noopener noreferrer",
            className="ref-source-link-clean"
            )
        ], className="ref-sidebar-bottom-source"),

        # 4. Hidden filter elements to keep existing Dash callbacks intact
        html.Div([
            dcc.Dropdown(
                id="filter-region-dropdown",
                options=region_options,
                value=selected_region if selected_region else "ALL",
                clearable=False
            ),
            dcc.Dropdown(
                id="filter-province-dropdown",
                options=prov_options,
                value=selected_province if selected_province else "ALL",
                clearable=False
            ),
            dcc.Dropdown(
                id="filter-city-dropdown",
                options=[{"label": "All Cities/Municipalities", "value": "ALL"}],
                value="ALL",
                clearable=False
            ),
            dcc.Dropdown(
                id="filter-year-dropdown",
                options=[{"label": "2020", "value": "2020"}],
                value="2020",
                clearable=False
            ),
            html.Button("Reset Filters", id="btn-reset-filters")
        ], style={"display": "none"})
    ], className="ref-sidebar")
