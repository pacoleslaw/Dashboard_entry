"""
Main Dash Application for "Philippines in Focus: People, Places, and Progress".
Faithfully reproduces the official Philippine Statistics Authority reference dashboard.
"""
import dash
from dash import html, dcc, Input, Output, State, ALL, ctx

# Core Utilities
from utils.data_loader import load_population_data, get_entity_by_code
from utils.geography import get_regions, get_provinces

# Components
from components.header import render_header
from components.sidebar import render_sidebar
from components.kpi_cards import render_kpi_cards

# Pages
from pages.overview import render_overview_page
from pages.households import render_households_page
from pages.housing import render_housing_page
from pages.people import render_people_page
from pages.places import render_places_page
from pages.compare import render_compare_page
from pages.definitions import render_definitions_page

app = dash.Dash(
    __name__,
    title="Population and Housing Statistics | Philippine Statistics Authority",
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}]
)
server = app.server

# Pre-load data once at application startup
load_population_data()

# Root Application Layout matching the reference image structure
app.layout = html.Div([
    # Shared State Stores
    dcc.Store(id="store-selected-code", data="PH000000000"),
    dcc.Store(id="store-active-page", data="overview"),
    dcc.Store(id="store-map-indicator", data="total_pop"),
    dcc.Store(id="store-map-level", data="region"),
    dcc.Store(id="store-compare-a", data="PH040000000"),
    dcc.Store(id="store-compare-b", data="PH130000000"),

    # Main Wrapper
    html.Div([
        # 1. Top White Header
        render_header(),

        # 2. Main Two-Column Structure: Sidebar (Left) + Content (Right)
        html.Div([
            # Left Sidebar
            html.Div(id="sidebar-container", children=render_sidebar("overview", "ALL", "ALL")),

            # Right Content Area
            html.Div([
                # Top Row: 4 KPI Cards
                html.Div(id="kpi-cards-container", children=render_kpi_cards("PH000000000")),

                # Middle: Active Page View (3-Column Overview by default)
                html.Main(id="page-content", children=render_overview_page("PH000000000", "total_pop")),

                # Bottom: Dark Navy Footer Bar matching reference image
                html.Footer([
                    html.Div(
                        "Source: Philippine Statistics Authority | 2020 Census of Population and Housing",
                        style={"fontWeight": "500", "color": "#cbd5e1"}
                    ),
                    html.A(
                        ["Visit PSA Website ", html.Span("↗", style={"fontSize": "0.85rem"})],
                        href="https://psa.gov.ph",
                        target="_blank",
                        rel="noopener noreferrer",
                        className="ref-footer-btn"
                    )
                ], className="ref-bottom-footer")
            ], className="ref-content-area")
        ], className="ref-main-layout")
    ], className="dashboard-page-wrapper")
])

# -----------------------------------------------------------------------------
# CALLBACK 1: Navigation Page Routing
# -----------------------------------------------------------------------------
@app.callback(
    Output("store-active-page", "data"),
    Input("nav-overview", "n_clicks"),
    Input("nav-households", "n_clicks"),
    Input("nav-housing", "n_clicks"),
    Input("nav-people", "n_clicks"),
    prevent_initial_call=True
)
def handle_navigation(n_ov, n_hh, n_ho, n_pe):
    trig = ctx.triggered_id
    if trig == "nav-overview":
        return "overview"
    elif trig == "nav-households":
        return "households"
    elif trig == "nav-housing":
        return "housing"
    elif trig == "nav-people":
        return "people"
    return "overview"

# -----------------------------------------------------------------------------
# CALLBACK 2: Map Indicator Toggle
# -----------------------------------------------------------------------------
@app.callback(
    Output("store-map-indicator", "data"),
    Input("map-indicator-dropdown", "value"),
    prevent_initial_call=True
)
def handle_indicator_change(val):
    return val if val else "total_pop"

# -----------------------------------------------------------------------------
# CALLBACK 3: Comparison Places Dropdowns
# -----------------------------------------------------------------------------
@app.callback(
    Output("store-compare-a", "data"),
    Output("store-compare-b", "data"),
    Input("compare-dropdown-a", "value"),
    Input("compare-dropdown-b", "value"),
    prevent_initial_call=True
)
def handle_compare_dropdowns(val_a, val_b):
    return val_a or "PH040000000", val_b or "PH130000000"

# -----------------------------------------------------------------------------
# CALLBACK 4: Unified Geographic State Management (Bi-directional Linkage)
# -----------------------------------------------------------------------------
@app.callback(
    Output("store-selected-code", "data"),
    Input("choropleth-geojson", "clickData"),
    Input("population-bar-chart", "clickData"),
    Input({"type": "crumb-btn", "code": ALL}, "n_clicks"),
    Input("filter-region-dropdown", "value"),
    Input("filter-province-dropdown", "value"),
    Input("btn-reset-filters", "n_clicks"),
    State("store-selected-code", "data"),
    prevent_initial_call=True
)
def handle_geo_selection(map_click, chart_click, crumb_clicks, filter_region, filter_prov, reset_clicks, current_code):
    trig = ctx.triggered_id

    # 1. Reset button clicked
    if trig == "btn-reset-filters":
        return "PH000000000"

    # 2. Map clicked (MAP -> CHARTS)
    if trig == "choropleth-geojson" and map_click:
        props = map_click.get("properties", {})
        code = props.get("code") or props.get("ADM1_PCODE") or props.get("ADM2_PCODE")
        if code:
            if "_MUNI_" in code:
                base_code = code.split("_MUNI_")[0]
                return base_code
            return code

    # 3. Bar Chart clicked (CHARTS -> MAP)
    if trig == "population-bar-chart" and chart_click:
        points = chart_click.get("points", [])
        if points:
            customdata = points[0].get("customdata")
            if customdata:
                return customdata

    # 4. Breadcrumb clicked
    if isinstance(trig, dict) and trig.get("type") == "crumb-btn":
        if any(crumb_clicks):
            return trig.get("code", "PH000000000")

    # 5. Sidebar province filter changed
    if trig == "filter-province-dropdown":
        if filter_prov and filter_prov != "ALL":
            return filter_prov
        elif filter_region and filter_region != "ALL":
            return filter_region

    # 6. Sidebar region filter changed
    if trig == "filter-region-dropdown":
        if filter_region and filter_region != "ALL":
            return filter_region
        return "PH000000000"

    return current_code or "PH000000000"

# -----------------------------------------------------------------------------
# CALLBACK 5: Administrative Map Level Management (Region / Province / Municity)
# -----------------------------------------------------------------------------
@app.callback(
    Output("store-map-level", "data"),
    Input("btn-level-region", "n_clicks"),
    Input("btn-level-province", "n_clicks"),
    Input("btn-level-municity", "n_clicks"),
    Input("store-selected-code", "data"),
    State("store-map-level", "data"),
    prevent_initial_call=True
)
def handle_map_level_change(btn_reg, btn_prov, btn_muni, sel_code, current_level):
    trig = ctx.triggered_id
    if trig == "btn-level-region":
        return "region"
    elif trig == "btn-level-province":
        return "province"
    elif trig == "btn-level-municity":
        return "municity"
    elif trig == "store-selected-code":
        entity = get_entity_by_code(sel_code)
        if entity["level"] == "Country":
            return "region"
        elif entity["level"] == "Region":
            return "province"
        else:
            return "municity"
    return current_level or "region"

# -----------------------------------------------------------------------------
# CALLBACK 6: Master UI Re-render
# -----------------------------------------------------------------------------
@app.callback(
    Output("kpi-cards-container", "children"),
    Output("page-content", "children"),
    Output("sidebar-container", "children"),
    Input("store-selected-code", "data"),
    Input("store-active-page", "data"),
    Input("store-map-indicator", "data"),
    Input("store-map-level", "data"),
    Input("store-compare-a", "data"),
    Input("store-compare-b", "data")
)
def render_main_ui(selected_code, active_page, indicator, map_level, comp_a, comp_b):
    code = selected_code or "PH000000000"
    page = active_page or "overview"
    ind = indicator or "total_pop"
    m_level = map_level or "region"
    entity = get_entity_by_code(code)

    if entity["level"] == "Country":
        sel_region = "ALL"
        sel_prov = "ALL"
    elif entity["level"] == "Region":
        sel_region = entity["code"]
        sel_prov = "ALL"
    else:
        sel_region = entity.get("parent_code", "ALL")
        sel_prov = entity["code"]

    kpis = render_kpi_cards(code)

    if page == "overview":
        content = render_overview_page(code, ind, m_level)
    elif page == "households":
        content = render_households_page(code)
    elif page == "housing":
        content = render_housing_page(code)
    elif page == "people":
        content = render_people_page(code)
    elif page == "places":
        content = render_places_page(code, ind, m_level)
    elif page == "compare":
        content = render_compare_page(comp_a or "PH040000000", comp_b or "PH130000000")
    elif page == "definitions":
        content = render_definitions_page()
    else:
        content = render_overview_page(code, ind, m_level)

    sidebar = render_sidebar(page, sel_region, sel_prov)

    return kpis, content, sidebar

if __name__ == "__main__":
    print("=" * 70)
    print("  Population and Housing Statistics | Philippine Statistics Authority")
    print("  Official 2020 Census of Population and Housing Dashboard")
    print("  Serving at http://127.0.0.1:8050/")
    print("=" * 70)
    app.run(debug=True, dev_tools_ui=False, dev_tools_props_check=False, port=8050)
