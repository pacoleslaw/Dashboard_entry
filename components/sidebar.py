"""
Sidebar Component reproducing the exact left sidebar from the reference image.
"""
from dash import html, dcc
from utils.geography import get_regions, get_provinces

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

    nav_items = [
        {"id": "nav-overview", "page": "overview", "icon": "/assets/icons/users.svg", "label": "Population"},
        {"id": "nav-households", "page": "households", "icon": "/assets/icons/house.svg", "label": "Households"},
        {"id": "nav-housing", "page": "housing", "icon": "/assets/icons/building.svg", "label": "Housing"},
        {"id": "nav-people", "page": "people", "icon": "/assets/icons/chart.svg", "label": "Demographics"}
    ]

    return html.Aside([
        # 1. Dark Blue Navigation Block
        html.Div([
            html.Div([
                html.Button([
                    html.Img(src=item["icon"], style={"width": "18px", "height": "18px", "filter": "brightness(0) invert(1)"}),
                    html.Span(item["label"])
                ],
                id=item["id"],
                className=f"ref-nav-btn {'active' if active_page == item['page'] else ''}",
                n_clicks=0
                )
                for item in nav_items
            ])
        ], className="ref-nav-card"),

        # 2. White Filters Card
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/filter.svg", style={"width": "16px", "height": "16px"}),
                html.Span("Filters", style={"fontWeight": "700", "fontSize": "0.95rem", "color": "var(--psa-navy)"})
            ], className="ref-filter-title"),

            # Region
            html.Div([
                html.Label("Region", className="ref-filter-label"),
                dcc.Dropdown(
                    id="filter-region-dropdown",
                    options=region_options,
                    value=selected_region if selected_region else "ALL",
                    placeholder="All Regions",
                    clearable=False,
                    style={"fontSize": "0.82rem"}
                )
            ], className="ref-filter-group"),

            # Province
            html.Div([
                html.Label("Province", className="ref-filter-label"),
                dcc.Dropdown(
                    id="filter-province-dropdown",
                    options=prov_options,
                    value=selected_province if selected_province else "ALL",
                    placeholder="All Provinces",
                    clearable=False,
                    style={"fontSize": "0.82rem"}
                )
            ], className="ref-filter-group"),

            # City/Municipality
            html.Div([
                html.Label("City/Municipality", className="ref-filter-label"),
                dcc.Dropdown(
                    id="filter-city-dropdown",
                    options=[{"label": "All Cities/Municipalities", "value": "ALL"}],
                    value="ALL",
                    clearable=False,
                    style={"fontSize": "0.82rem"}
                )
            ], className="ref-filter-group"),

            # Year
            html.Div([
                html.Label("Year", className="ref-filter-label"),
                dcc.Dropdown(
                    id="filter-year-dropdown",
                    options=[{"label": "2020 (Latest Available)", "value": "2020"}],
                    value="2020",
                    clearable=False,
                    disabled=True,
                    style={"fontSize": "0.82rem"}
                )
            ], className="ref-filter-group"),

            # Hidden Reset for callbacks
            html.Button(
                "Reset Filters",
                id="btn-reset-filters",
                style={"display": "none"}
            )
        ], className="ref-filter-card"),

        # 3. White Data Source Card
        html.Div([
            html.Div([
                html.Div("i", className="ref-source-icon"),
                html.Span("Data Source", className="ref-source-title")
            ], className="ref-source-header"),
            html.P(
                "PSA, 2020 Census of Population and Housing (CPH)",
                className="ref-source-desc"
            ),
            html.A(
                ["Visit PSA Source ", html.Span("↗", style={"fontSize": "0.85rem"})],
                href="https://psa.gov.ph/statistics/population-and-housing",
                target="_blank",
                rel="noopener noreferrer",
                className="ref-source-link"
            )
        ], className="ref-source-card"),

        # 4. Bottom-most sidebar note
        html.Div([
            html.P("Source: Philippine Statistics Authority", style={"fontWeight": "600", "marginBottom": "2px"}),
            html.P("2020 Census of Population and Housing", style={"marginBottom": "2px"}),
            html.A(
                "(https://psa.gov.ph/statistics/)",
                href="https://psa.gov.ph/statistics/population-and-housing",
                target="_blank",
                style={"color": "#60a5fa", "textDecoration": "none"}
            )
        ], className="ref-sidebar-foot-note")
    ], className="ref-sidebar")
