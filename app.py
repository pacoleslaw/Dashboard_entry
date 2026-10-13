"""
Main Dash Application for "Philippines in Focus: People, Places, and Progress".
Faithfully reproduces the official Philippine Statistics Authority reference dashboard.
"""
import gzip
from flask import request
import dash
from dash import html, dcc, Input, Output, State, ALL, ctx

# Core Utilities
from utils.data_loader import load_population_data, get_entity_by_code
from utils.geography import get_regions, get_provinces

# Components
from components.header import render_header
from components.sidebar import render_sidebar
from components.kpi_cards import render_kpi_cards
from components.map import preload_map_geojson, get_choropleth_data

# Pages
from components.demographics import build_demographics_pyramid_figure, build_demographics_age_bar_figure
from pages.overview import render_overview_page
from pages.population import render_population_page
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
handler = server

# -----------------------------------------------------------------------------
# PERFORMANCE OPTIMIZATION: Transparent Gzip Response Compression
# Compresses responses >1KB for clients accepting gzip (98% reduction on wire)
# -----------------------------------------------------------------------------
@server.after_request
def compress_response(response):
    if response.direct_passthrough:
        return response
    if (
        response.status_code < 300
        and "gzip" in request.headers.get("Accept-Encoding", "")
        and "Content-Encoding" not in response.headers
        and (
            response.mimetype.startswith("application/json")
            or response.mimetype.startswith("text/")
            or response.mimetype.startswith("application/javascript")
        )
    ):
        data = response.get_data()
        if len(data) > 1024:
            compressed = gzip.compress(data, compresslevel=5)
            response.set_data(compressed)
            response.headers["Content-Encoding"] = "gzip"
            response.headers["Content-Length"] = len(compressed)
    return response

# Pre-load data and boundaries into memory once at application startup
load_population_data()
preload_map_geojson()

# Pre-warm frequently accessed choropleth and page caches for instant first clicks
get_choropleth_data("PH000000000", "region", "total_pop")
get_choropleth_data("PH000000000", "region", "households")
get_choropleth_data("PH000000000", "region", "housing")

# Root Application Layout matching the reference image structure
app.layout = html.Div([
    # Shared State Stores
    dcc.Store(id="store-selected-code", data="PH000000000"),
    dcc.Store(id="store-active-page", data="overview"),
    dcc.Store(id="store-map-indicator", data="total_pop"),
    dcc.Store(id="store-map-level", data="region"),
    dcc.Store(id="store-compare-a", data="PH040000000"),
    dcc.Store(id="store-compare-b", data="PH130000000"),
    dcc.Store(id="store-map-manual-nav", data=False),
    dcc.Store(id="store-map-viewport", data=None),
    dcc.Store(id="nav-scroll-dummy-output", data=0),

    # Main Wrapper
    html.Div([
        # 1. Top PSA Header
        render_header(),

        # Main Two-Column Structure: Sidebar (Left) + Content (Right)
        html.Div([
            # Left Sidebar
            html.Div(id="sidebar-container", children=render_sidebar("overview", "ALL", "ALL")),

            # Right Content Area
            html.Div([
                # Top Row: 4 KPI Cards
                html.Div(id="kpi-cards-container", children=render_kpi_cards("PH000000000", "overview")),

                # Middle: Active Page View
                html.Main(id="page-content", children=render_overview_page("PH000000000", "total_pop")),

                # Bottom: Clean Reference Footer Bar
                html.Footer([
                    html.Div(
                        "Philippine Statistics Authority | 2020 Census of Population and Housing",
                        className="ref-footer-center"
                    )
                ], className="ref-clean-footer")
            ], className="ref-content-area")
        ], className="ref-main-layout")
    ], className="dashboard-page-wrapper")
])

# -----------------------------------------------------------------------------
# CLIENTSIDE CALLBACK: Smooth Horizontal Scroll for Mobile Nav Pills
# -----------------------------------------------------------------------------
app.clientside_callback(
    """
    function(left_clicks, right_clicks) {
        var trig = window.dash_clientside.callback_context.triggered[0];
        if (!trig) return window.dash_clientside.no_update;
        var el = document.getElementById("ref-nav-scroll-container");
        if (!el) return window.dash_clientside.no_update;
        if (trig.prop_id.indexOf("btn-nav-scroll-left") !== -1) {
            el.scrollBy({left: -180, behavior: "smooth"});
        } else if (trig.prop_id.indexOf("btn-nav-scroll-right") !== -1) {
            el.scrollBy({left: 180, behavior: "smooth"});
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("nav-scroll-dummy-output", "data"),
    Input("btn-nav-scroll-left", "n_clicks"),
    Input("btn-nav-scroll-right", "n_clicks"),
    prevent_initial_call=True
)

# -----------------------------------------------------------------------------
# CLIENTSIDE CALLBACK 1: Instant Navigation Page Routing (0ms server latency)
# -----------------------------------------------------------------------------
app.clientside_callback(
    """
    function(n_clicks, compare_clicks, mobile_val) {
        var trig = window.dash_clientside.callback_context.triggered;
        if (!trig || !trig.length) return window.dash_clientside.no_update;
        var propId = trig[0].prop_id;
        if (!propId) return window.dash_clientside.no_update;
        var trigId = propId.split('.')[0];

        if (trigId === "mobile-nav-page-select" && mobile_val) {
            return mobile_val === "population" ? "overview" : mobile_val;
        }
        try {
            var parsed = JSON.parse(trigId);
            if (parsed.page) {
                return parsed.page === "population" ? "overview" : parsed.page;
            }
            if (parsed.type === "btn-compare-place") {
                return "compare";
            }
        } catch(e) {}
        return window.dash_clientside.no_update;
    }
    """,
    Output("store-active-page", "data"),
    Input({"type": "nav-btn", "page": ALL, "source": ALL}, "n_clicks"),
    Input({"type": "btn-compare-place", "code": ALL}, "n_clicks"),
    Input("mobile-nav-page-select", "value"),
    prevent_initial_call=True
)

# -----------------------------------------------------------------------------
# CLIENTSIDE CALLBACK 2: Map Indicator Toggle (Instant)
# -----------------------------------------------------------------------------
app.clientside_callback(
    """
    function(vals) {
        if (!vals || !vals.length) return window.dash_clientside.no_update;
        for (var i = 0; i < vals.length; i++) {
            if (vals[i]) return vals[i];
        }
        return "total_pop";
    }
    """,
    Output("store-map-indicator", "data"),
    Input({"type": "map-indicator-dropdown", "id": ALL}, "value"),
    prevent_initial_call=True
)

# -----------------------------------------------------------------------------
# CLIENTSIDE CALLBACK 2B: 2020 CPH Highlights Modal Toggle (Instant)
# -----------------------------------------------------------------------------
app.clientside_callback(
    """
    function(open_clicks, close_clicks, backdrop_clicks) {
        var trig = window.dash_clientside.callback_context.triggered;
        if (!trig || !trig.length) return window.dash_clientside.no_update;
        var propId = trig[0].prop_id;
        if (propId.indexOf("btn-open-cph-modal") !== -1) {
            return [{"display": "flex"}];
        }
        if (propId.indexOf("btn-close-cph-modal") !== -1 || propId.indexOf("cph-modal-backdrop") !== -1) {
            return [{"display": "none"}];
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output({"type": "cph-highlights-modal", "id": ALL}, "style"),
    Input({"type": "btn-open-cph-modal", "id": ALL}, "n_clicks"),
    Input({"type": "btn-close-cph-modal", "id": ALL}, "n_clicks"),
    Input({"type": "cph-modal-backdrop", "id": ALL}, "n_clicks"),
    prevent_initial_call=True
)

# -----------------------------------------------------------------------------
# CALLBACK 3: Comparison Places Dropdowns
# -----------------------------------------------------------------------------
@app.callback(
    Output("store-compare-a", "data"),
    Output("store-compare-b", "data"),
    Input("compare-dropdown-a", "value"),
    Input("compare-dropdown-b", "value"),
    Input({"type": "btn-compare-place", "code": ALL}, "n_clicks"),
    State("store-compare-a", "data"),
    State("store-compare-b", "data"),
    prevent_initial_call=True
)
def handle_compare_dropdowns(val_a, val_b, compare_clicks, current_a, current_b):
    trig = ctx.triggered_id
    if isinstance(trig, dict) and trig.get("type") == "btn-compare-place":
        if any(c for c in compare_clicks if c):
            return trig.get("code", current_a), current_b
    return val_a or current_a or "PH040000000", val_b or current_b or "PH130000000"

# -----------------------------------------------------------------------------
# CALLBACK 4: Unified Geographic State Management (Bi-directional Linkage)
# Dynamic components use pattern matching (ALL) so the callback never blocks
# when elements are only present on specific pages.
# -----------------------------------------------------------------------------
@app.callback(
    Output("store-selected-code", "data"),
    Input({"type": "choropleth-geojson", "id": ALL}, "clickData"),
    Input({"type": "population-bar-chart", "id": ALL}, "clickData"),
    Input({"type": "households-bar-chart", "id": ALL}, "clickData"),
    Input({"type": "housing-bar-chart", "id": ALL}, "clickData"),
    Input({"type": "housing-filter-region", "id": ALL}, "value"),
    Input({"type": "housing-filter-prov", "id": ALL}, "value"),
    Input({"type": "hh-filter-region", "id": ALL}, "value"),
    Input({"type": "hh-filter-prov", "id": ALL}, "value"),
    Input({"type": "hh-filter-city", "id": ALL}, "value"),
    Input({"type": "pop-filter-region", "id": ALL}, "value"),
    Input({"type": "pop-filter-prov", "id": ALL}, "value"),
    Input({"type": "pop-filter-city", "id": ALL}, "value"),
    Input({"type": "demo-filter-region", "id": ALL}, "value"),
    Input({"type": "demo-filter-prov", "id": ALL}, "value"),
    Input({"type": "demo-filter-city", "id": ALL}, "value"),
    Input({"type": "crumb-btn", "code": ALL}, "n_clicks"),
    Input("filter-region-dropdown", "value"),
    Input("filter-province-dropdown", "value"),
    Input("btn-reset-filters", "n_clicks"),
    State("store-selected-code", "data"),
    prevent_initial_call=True
)
def handle_geo_selection(map_clicks, chart_clicks, hh_clicks, housing_clicks,
                         housing_reg_vals, housing_prov_vals,
                         hh_reg_vals, hh_prov_vals, hh_city_vals,
                         pop_reg_vals, pop_prov_vals, pop_city_vals,
                         demo_reg_vals, demo_prov_vals, demo_city_vals,
                         crumb_clicks, filter_region, filter_prov, reset_clicks, current_code):
    trig = ctx.triggered_id

    # 1. Reset button clicked
    if trig == "btn-reset-filters":
        return "PH000000000"

    # 2. Pattern-matched components
    if isinstance(trig, dict):
        comp_type = trig.get("type")

        # Map clicked (MAP -> CHARTS)
        if comp_type == "choropleth-geojson":
            for map_click in map_clicks:
                if map_click:
                    props = map_click.get("properties", {})
                    code = props.get("code") or props.get("ADM1_PCODE") or props.get("ADM2_PCODE")
                    if code:
                        if "_MUNI_" in code:
                            return code.split("_MUNI_")[0]
                        return code

        # Population Bar Chart clicked (CHARTS -> MAP)
        elif comp_type == "population-bar-chart":
            for chart_click in chart_clicks:
                if chart_click:
                    points = chart_click.get("points", [])
                    if points:
                        customdata = points[0].get("customdata")
                        if customdata:
                            return customdata

        # Households Bar Chart clicked
        elif comp_type == "households-bar-chart":
            for hh_click in hh_clicks:
                if hh_click:
                    points = hh_click.get("points", [])
                    if points:
                        code = points[0].get("customdata")
                        if code and code != "PH000000000":
                            return code

        # Housing Bar Chart clicked
        elif comp_type == "housing-bar-chart":
            for h_click in housing_clicks:
                if h_click:
                    points = h_click.get("points", [])
                    if points:
                        code = points[0].get("customdata")
                        if code and code != "PH000000000":
                            return code

        # Housing Explore Bar Region dropdown
        elif comp_type == "housing-filter-region":
            for r_val in housing_reg_vals:
                if r_val and r_val != "ALL":
                    return r_val
            return "PH000000000"

        # Housing Explore Bar Province dropdown
        elif comp_type == "housing-filter-prov":
            for p_val in housing_prov_vals:
                if p_val and p_val != "ALL":
                    return p_val

        # Household Explore Bar Region dropdown
        elif comp_type == "hh-filter-region":
            for r_val in hh_reg_vals:
                if r_val and r_val != "ALL":
                    return r_val
            return "PH000000000"

        # Household Explore Bar Province dropdown
        elif comp_type == "hh-filter-prov":
            for p_val in hh_prov_vals:
                if p_val and p_val != "ALL":
                    return p_val

        # Household Explore Bar City/Municipality dropdown
        elif comp_type == "hh-filter-city":
            for c_val in hh_city_vals:
                if c_val and c_val != "ALL":
                    return c_val

        # Population Explore Bar Region dropdown
        elif comp_type == "pop-filter-region":
            for r_val in pop_reg_vals:
                if r_val and r_val != "ALL":
                    return r_val
            return "PH000000000"

        # Population Explore Bar Province dropdown
        elif comp_type == "pop-filter-prov":
            for p_val in pop_prov_vals:
                if p_val and p_val != "ALL":
                    return p_val

        # Population Explore Bar City/Municipality dropdown
        elif comp_type == "pop-filter-city":
            for c_val in pop_city_vals:
                if c_val and c_val != "ALL":
                    return c_val

        # Demographics Explore Bar Region dropdown
        elif comp_type == "demo-filter-region":
            for r_val in demo_reg_vals:
                if r_val and r_val != "ALL":
                    return r_val
            return "PH000000000"

        # Demographics Explore Bar Province dropdown
        elif comp_type == "demo-filter-prov":
            for p_val in demo_prov_vals:
                if p_val and p_val != "ALL":
                    return p_val
            for r_val in demo_reg_vals:
                if r_val and r_val != "ALL":
                    return r_val
            return "PH000000000"

        # Demographics Explore Bar City/Municipality dropdown
        elif comp_type == "demo-filter-city":
            for c_val in demo_city_vals:
                if c_val and c_val != "ALL":
                    return c_val

        # Breadcrumb clicked
        elif comp_type == "crumb-btn":
            if any(c for c in crumb_clicks if c):
                return trig.get("code", "PH000000000")

    # 3. Sidebar province filter changed
    if trig == "filter-province-dropdown":
        if filter_prov and filter_prov != "ALL":
            return filter_prov
        elif filter_region and filter_region != "ALL":
            return filter_region

    # 4. Sidebar region filter changed
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
    Input({"type": "btn-level", "level": ALL}, "n_clicks"),
    Input("store-selected-code", "data"),
    State("store-map-level", "data"),
    prevent_initial_call=True
)
def handle_map_level_change(level_clicks, sel_code, current_level):
    trig = ctx.triggered_id
    is_ncr = (sel_code == "PH130000000" or (sel_code and sel_code.startswith("PH13")))

    if isinstance(trig, dict) and trig.get("type") == "btn-level":
        level = trig.get("level")
        if level == "region":
            return "region"
        elif level == "province":
            if is_ncr:
                return "municity"
            return "province"
        elif level == "municity":
            return "municity"

    elif trig == "store-selected-code":
        entity = get_entity_by_code(sel_code)
        if entity["level"] == "Country":
            return "region"
        elif entity["level"] == "Region":
            if is_ncr or entity.get("short_name") == "NCR":
                return "municity"
            return "province"
        else:
            return "municity"
    return current_level or "region"

# -----------------------------------------------------------------------------
# CALLBACK 6: Map Navigation & Viewport State Tracking
# -----------------------------------------------------------------------------
@app.callback(
    Output("store-map-manual-nav", "data"),
    Output("store-map-viewport", "data"),
    Input({"type": "interactive-map", "id": ALL}, "viewport"),
    Input("store-selected-code", "data"),
    Input("store-map-level", "data"),
    Input({"type": "btn-recenter-map", "id": ALL}, "n_clicks"),
    Input("btn-reset-filters", "n_clicks"),
    State("store-map-manual-nav", "data"),
    State("store-map-viewport", "data"),
    prevent_initial_call=True
)
def handle_map_navigation_state(viewports, sel_code, map_level, recenter_clicks, n_reset, current_manual, current_vp):
    trig = ctx.triggered_id
    if trig in ("store-selected-code", "store-map-level", "btn-reset-filters"):
        return False, None
    if isinstance(trig, dict):
        if trig.get("type") == "btn-recenter-map":
            return False, None
        if trig.get("type") == "interactive-map":
            for vp in viewports:
                if vp:
                    return True, vp
    return current_manual, current_vp

# -----------------------------------------------------------------------------
# CALLBACK 7: Master UI Re-render
# Only listens to persistent root dcc.Store components so it NEVER blocks
# when switching between pages.
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
    Input("store-compare-b", "data"),
    State("store-map-manual-nav", "data"),
    State("store-map-viewport", "data"),
    prevent_initial_call=True
)
def render_main_ui(selected_code, active_page, indicator, map_level, comp_a, comp_b, manual_nav, viewport):
    try:
        trig = ctx.triggered_id
    except Exception:
        trig = None
    code = selected_code or "PH000000000"
    page = active_page or "overview"
    ind = indicator or "total_pop"
    m_level = map_level or "region"
    entity = get_entity_by_code(code)

    # If the user selected an entity, level, or changed page -> auto-center item view (manual_nav=False)
    if trig in ("store-selected-code", "store-map-level", "store-active-page"):
        use_manual = False
        use_vp = None
    else:
        use_manual = bool(manual_nav)
        use_vp = viewport if use_manual else None

    if entity["level"] == "Country":
        sel_region = "ALL"
        sel_prov = "ALL"
    elif entity["level"] == "Region":
        sel_region = entity["code"]
        sel_prov = "ALL"
    else:
        sel_region = entity.get("parent_code", "ALL")
        sel_prov = entity["code"]

    kpis = render_kpi_cards(code, page)

    if page in ("overview", "population"):
        content = render_overview_page(code, ind, m_level, use_manual, use_vp)
    elif page == "households":
        content = render_households_page(code, "households", m_level, use_manual, use_vp)
    elif page == "housing":
        content = render_housing_page(code, "housing", m_level, use_manual, use_vp)
    elif page in ("people", "demographics"):
        content = render_people_page(code)
    elif page == "places":
        content = render_places_page(code, ind, m_level, use_manual, use_vp)
    elif page == "compare":
        content = render_compare_page(comp_a or "PH040000000", comp_b or "PH130000000")
    elif page == "definitions":
        content = render_definitions_page()
    else:
        content = render_overview_page(code, ind, m_level, use_manual, use_vp)

    sidebar = render_sidebar(page, sel_region, sel_prov)

    return kpis, content, sidebar


# -----------------------------------------------------------------------------
# CALLBACK 8: Demographics Interactive Chart Toggles
# -----------------------------------------------------------------------------
@app.callback(
    Output({"type": "demo-pyramid-graph", "id": ALL}, "figure"),
    Input({"type": "demo-pyramid-view", "id": ALL}, "value"),
    Input({"type": "demo-pyramid-age-filter", "id": ALL}, "value"),
    State("store-selected-code", "data"),
    prevent_initial_call=True
)
def handle_demo_pyramid_toggle(view_vals, age_vals, selected_code):
    entity = get_entity_by_code(selected_code or "PH000000000")
    view = view_vals[0] if (view_vals and view_vals[0]) else "num"
    age_filter = age_vals[0] if (age_vals and age_vals[0]) else "all"
    return [build_demographics_pyramid_figure(entity, view, age_filter)]


@app.callback(
    Output({"type": "demo-age-bar-graph", "id": ALL}, "figure"),
    Input({"type": "demo-age-metric", "id": ALL}, "value"),
    State("store-selected-code", "data"),
    prevent_initial_call=True
)
def handle_demo_age_metric_toggle(metric_vals, selected_code):
    entity = get_entity_by_code(selected_code or "PH000000000")
    metric = metric_vals[0] if metric_vals else "total"
    return [build_demographics_age_bar_figure(entity, metric)]


if __name__ == "__main__":
    print("=" * 70)
    print("  Population and Housing Statistics | Philippine Statistics Authority")
    print("  Official 2020 Census of Population and Housing Dashboard")
    print("  Serving at http://127.0.0.1:8050/")
    print("=" * 70)
    app.run(debug=True, dev_tools_ui=False, dev_tools_props_check=False, port=8050)
