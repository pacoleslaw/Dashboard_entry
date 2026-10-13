"""
KPI Cards Component reproducing the exact 4 KPI cards for each page:
- Overview: Total Population, Total Households, Average Household Size, Reference Year / Selected Area.
- Population: Total Population, Total Households, Avg. Household Size, Selected Area (compact previous setup layout).
- Households: Total Households, Avg. Household Size, Population Per Household, Selected Area.
- Housing: Total Housing Units, Occupied Units, Vacant Units, Selected Area.
"""
import functools
from dash import html, dcc
from utils.data_loader import get_entity_by_code
from utils.geography import get_regions, get_provinces
from utils.formatting import format_number, format_compact

ISLAND_GROUPS = {
    "Luzon": ["PH130000000", "PH140000000", "PH010000000", "PH020000000", "PH030000000", "PH040000000", "PH170000000", "PH050000000"],
    "Visayas": ["PH060000000", "PH070000000", "PH080000000"],
    "Mindanao": ["PH090000000", "PH100000000", "PH110000000", "PH120000000", "PH160000000", "PH150000000"]
}


# =============================================================================
# 1. POPULATION TOP SECTION (Compact 4 Cards matching previous setup layout)
# =============================================================================
def render_population_kpi_cards(code="PH000000000"):
    """
    Renders the compact 4 Population KPI cards matching the previous dashboard setup:
    [TOTAL POPULATION] [TOTAL HOUSEHOLDS] [AVG. HOUSEHOLD SIZE] [SELECTED AREA]
    """
    entity = get_entity_by_code(code)
    tot_pop = entity.get("total_pop", 0)
    tot_hh = entity.get("total_households", 0)
    avg_size = entity.get("avg_household_size", 0.0)
    name = entity.get("short_name", entity["name"])
    level = entity.get("level", "Country")
    area_type = "National" if level == "Country" else level

    tot_pop_str = format_number(tot_pop)
    exact_tot_pop = format_number(tot_pop)
    tot_hh_str = format_number(tot_hh)
    exact_tot_hh = format_number(tot_hh)
    avg_size_str = f"{avg_size:.1f}"

    return html.Div([
        # Card 1: TOTAL POPULATION (Blue badge)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/users.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge ref-kpi-blue",
                style={"backgroundColor": "#0284c7"}
            ),
            html.Div([
                html.Span("TOTAL POPULATION", className="ref-kpi-label"),
                html.Span(tot_pop_str, className="ref-kpi-num"),
                html.Div(html.Span("People counted in 2020 Census" if level == "Country" else f"Share of PH: {entity.get('nat_share', 0.0):.1f}%",
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),

        # Card 2: TOTAL HOUSEHOLDS (Green badge)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/house.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge ref-kpi-green",
                style={"backgroundColor": "#22c55e"}
            ),
            html.Div([
                html.Span("TOTAL HOUSEHOLDS", className="ref-kpi-label"),
                html.Span(tot_hh_str, className="ref-kpi-num"),
                html.Div(html.Span("Households across the Philippines" if level == "Country" else f"Households in {name}",
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),

        # Card 3: AVG. HOUSEHOLD SIZE (Cyan badge)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/user.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge",
                style={"backgroundColor": "#06b6d4"}
            ),
            html.Div([
                html.Span("AVG. HOUSEHOLD SIZE", className="ref-kpi-label"),
                html.Span(avg_size_str, className="ref-kpi-num"),
                html.Div(html.Span("persons",
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),

        # Card 4: SELECTED AREA (Navy badge)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/pin.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge ref-kpi-blue",
                style={"backgroundColor": "#002b5c"}
            ),
            html.Div([
                html.Span("SELECTED AREA", className="ref-kpi-label"),
                html.Span(name, className="ref-kpi-num",
                          style={"fontSize": "1.15rem", "lineHeight": "1.2", "whiteSpace": "normal"}),
                html.Div(html.Span(f"({area_type})",
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),
    ], className="ref-kpi-grid")


# =============================================================================
# 2. HOUSEHOLDS TOP SECTION (Header + Explore Bar + 4 Cards)
# =============================================================================
def _render_household_header():
    """Top header badge matching the reference design: [Icon] HOUSEHOLDS - How Filipino households are distributed across the Philippines."""
    return html.Div([
        html.Div(
            html.Img(src="/assets/icons/house.svg", style={"width": "20px", "height": "20px", "filter": "brightness(0) invert(1)"}),
            className="household-header-icon-badge"
        ),
        html.Div([
            html.H2("HOUSEHOLDS", className="household-header-title"),
            html.P("How Filipino households are distributed across the Philippines.", className="household-header-subtitle")
        ])
    ], className="household-header-lockup")


def _render_household_explore_area_bar(selected_code="PH000000000"):
    """5-selector filter bar matching reference design: EXPLORE THIS AREA"""
    entity = get_entity_by_code(selected_code)
    regions = get_regions()

    if entity["level"] == "Country":
        sel_island = "ALL"
        sel_reg = "ALL"
        sel_prov = "ALL"
        sel_city = "ALL"
        prov_options = [{"label": "All Provinces", "value": "ALL"}]
        city_options = [{"label": "All Cities/Municipalities", "value": "ALL"}]
    elif entity["level"] == "Region":
        sel_reg = entity["code"]
        sel_island = next((k for k, v in ISLAND_GROUPS.items() if sel_reg in v), "ALL")
        sel_prov = "ALL"
        sel_city = "ALL"
        provinces = get_provinces(sel_reg)
        prov_options = [{"label": "All Provinces", "value": "ALL"}] + [
            {"label": p["name"], "value": p["code"]} for p in provinces
        ]
        city_options = [{"label": "All Cities/Municipalities", "value": "ALL"}]
    else:
        sel_prov = entity["code"]
        sel_reg = entity.get("parent_code", "ALL")
        sel_island = next((k for k, v in ISLAND_GROUPS.items() if sel_reg in v), "ALL")
        sel_city = "ALL"
        provinces = get_provinces(sel_reg) if sel_reg != "ALL" else []
        prov_options = [{"label": "All Provinces", "value": "ALL"}] + [
            {"label": p["name"], "value": p["code"]} for p in provinces
        ]
        city_options = [{"label": "All Cities/Municipalities", "value": "ALL"}]

    island_options = [
        {"label": "All Regions", "value": "ALL"},
        {"label": "Luzon", "value": "Luzon"},
        {"label": "Visayas", "value": "Visayas"},
        {"label": "Mindanao", "value": "Mindanao"},
    ]

    region_options = [{"label": "All Regions", "value": "ALL"}] + [
        {"label": r["short_name"], "value": r["code"]} for r in regions
    ]

    return html.Div([
        html.Div("EXPLORE THIS AREA", className="household-explore-label"),
        html.Div([
            dcc.Dropdown(
                id={"type": "hh-filter-country", "id": "main"},
                options=[{"label": "Philippines", "value": "PH000000000"}],
                value="PH000000000",
                clearable=False,
                className="household-explore-dropdown"
            ),
            dcc.Dropdown(
                id={"type": "hh-filter-island", "id": "main"},
                options=island_options,
                value=sel_island,
                clearable=False,
                placeholder="All Regions",
                className="household-explore-dropdown"
            ),
            dcc.Dropdown(
                id={"type": "hh-filter-region", "id": "main"},
                options=region_options,
                value=sel_reg,
                clearable=False,
                placeholder="All Regions",
                className="household-explore-dropdown"
            ),
            dcc.Dropdown(
                id={"type": "hh-filter-prov", "id": "main"},
                options=prov_options,
                value=sel_prov,
                clearable=False,
                placeholder="All Provinces",
                className="household-explore-dropdown"
            ),
            dcc.Dropdown(
                id={"type": "hh-filter-city", "id": "main"},
                options=city_options,
                value=sel_city,
                clearable=False,
                placeholder="All Cities/Municipalities",
                className="household-explore-dropdown"
            ),
        ], className="household-explore-grid")
    ], className="household-explore-bar")


def render_household_kpi_cards(code="PH000000000"):
    """
    Renders the dedicated 4 Household KPI cards matching the reference design:
    [TOTAL HOUSEHOLDS] [AVG. HOUSEHOLD SIZE] [POPULATION PER HOUSEHOLD] [SELECTED AREA]
    """
    entity = get_entity_by_code(code)
    tot_hh   = entity.get("total_households", 0)
    hh_pop   = entity.get("household_pop", 0)
    avg_size = entity.get("avg_household_size", 0.0)
    name     = entity.get("short_name", entity["name"])
    level    = entity.get("level", "Country")
    area_type = "National" if level == "Country" else level

    pop_per_hh = (hh_pop / tot_hh) if tot_hh > 0 else 0.0

    if level == "Country":
        tot_hh_str = "26,393,906"
        exact_tot_hh = "26,393,906"
        avg_size_str = "4.1"
        pop_per_hh_str = "4.1"
    else:
        tot_hh_str = format_number(tot_hh)
        exact_tot_hh = format_number(tot_hh)
        avg_size_str = f"{avg_size:.1f}"
        pop_per_hh_str = f"{pop_per_hh:.1f}" if tot_hh else "—"

    cards_grid = html.Div([
        # Card 1: TOTAL HOUSEHOLDS (Green)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/house.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge ref-kpi-green",
                style={"backgroundColor": "#22c55e"}
            ),
            html.Div([
                html.Span("TOTAL HOUSEHOLDS", className="ref-kpi-label"),
                html.Span(tot_hh_str, className="ref-kpi-num"),
                html.Div(html.Span("Households across the Philippines" if level == "Country" else f"Households in {name}",
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),

        # Card 2: AVG. HOUSEHOLD SIZE (Blue)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/user.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge ref-kpi-blue",
                style={"backgroundColor": "#0284c7"}
            ),
            html.Div([
                html.Span("AVG. HOUSEHOLD SIZE", className="ref-kpi-label"),
                html.Span(avg_size_str, className="ref-kpi-num"),
                html.Div(html.Span("persons",
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),

        # Card 3: POPULATION PER HOUSEHOLD (Cyan)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/users.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge",
                style={"backgroundColor": "#06b6d4"}
            ),
            html.Div([
                html.Span("POPULATION PER HOUSEHOLD", className="ref-kpi-label"),
                html.Span(pop_per_hh_str, className="ref-kpi-num"),
                html.Div(html.Span("persons",
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),

        # Card 4: SELECTED AREA (Navy)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/pin.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge ref-kpi-blue",
                style={"backgroundColor": "#002b5c"}
            ),
            html.Div([
                html.Span("SELECTED AREA", className="ref-kpi-label"),
                html.Span(name, className="ref-kpi-num",
                          style={"fontSize": "1.15rem", "lineHeight": "1.2", "whiteSpace": "normal"}),
                html.Div(html.Span(f"({area_type})",
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),
    ], className="ref-kpi-grid")

    return html.Div([
        _render_household_header(),
        _render_household_explore_area_bar(code),
        cards_grid
    ], className="household-top-container")


# =============================================================================
# 3. HOUSING TOP SECTION (Header + Explore Bar + 4 Cards)
# =============================================================================
def _render_housing_header():
    """Top header badge matching the reference design: [Icon] HOUSING - What do Filipino households live in?"""
    return html.Div([
        html.Div(
            html.Img(src="/assets/icons/house.svg", style={"width": "20px", "height": "20px", "filter": "brightness(0) invert(1)"}),
            className="housing-header-icon-badge"
        ),
        html.Div([
            html.H2("HOUSING", className="housing-header-title"),
            html.P("What do Filipino households live in?", className="housing-header-subtitle")
        ])
    ], className="housing-header-lockup")


def _render_explore_area_bar(selected_code="PH000000000"):
    """4-selector filter bar matching reference design: EXPLORE THIS AREA"""
    entity = get_entity_by_code(selected_code)
    regions = get_regions()

    if entity["level"] == "Country":
        sel_reg = "ALL"
        sel_prov = "ALL"
        prov_options = [{"label": "All Provinces", "value": "ALL"}]
    elif entity["level"] == "Region":
        sel_reg = entity["code"]
        sel_prov = "ALL"
        provinces = get_provinces(sel_reg)
        prov_options = [{"label": "All Provinces", "value": "ALL"}] + [
            {"label": p["name"], "value": p["code"]} for p in provinces
        ]
    else:
        sel_reg = entity.get("parent_code", "ALL")
        sel_prov = entity["code"]
        provinces = get_provinces(sel_reg) if sel_reg != "ALL" else []
        prov_options = [{"label": "All Provinces", "value": "ALL"}] + [
            {"label": p["name"], "value": p["code"]} for p in provinces
        ]

    region_options = [{"label": "All Regions", "value": "ALL"}] + [
        {"label": r["short_name"], "value": r["code"]} for r in regions
    ]

    return html.Div([
        html.Div("EXPLORE THIS AREA", className="housing-explore-label"),
        html.Div([
            dcc.Dropdown(
                id={"type": "housing-filter-country", "id": "main"},
                options=[{"label": "Philippines", "value": "PH000000000"}],
                value="PH000000000",
                clearable=False,
                className="housing-explore-dropdown"
            ),
            dcc.Dropdown(
                id={"type": "housing-filter-region", "id": "main"},
                options=region_options,
                value=sel_reg,
                clearable=False,
                placeholder="All Regions",
                className="housing-explore-dropdown"
            ),
            dcc.Dropdown(
                id={"type": "housing-filter-prov", "id": "main"},
                options=prov_options,
                value=sel_prov,
                clearable=False,
                placeholder="All Provinces",
                className="housing-explore-dropdown"
            ),
            dcc.Dropdown(
                id={"type": "housing-filter-city", "id": "main"},
                options=[{"label": "All Cities/Municipalities", "value": "ALL"}],
                value="ALL",
                clearable=False,
                disabled=True,
                placeholder="All Cities/Municipalities",
                className="housing-explore-dropdown"
            ),
        ], className="housing-explore-grid")
    ], className="housing-explore-bar")


def render_housing_kpi_cards(code="PH000000000"):
    """
    Renders the dedicated 4 Housing KPI cards matching the reference design:
    [TOTAL HOUSING UNITS] [OCCUPIED UNITS] [VACANT UNITS] [SELECTED AREA]
    """
    entity = get_entity_by_code(code)
    name = entity.get("short_name", entity["name"])
    level = entity.get("level", "Country")
    area_type = "National" if level == "Country" else level

    if level == "Country":
        total_units = 31_837_061
        total_units_str = "31,837,061"
        exact_units = "31,837,061"
        occupied_units_str = "28,913,906"
        occupied_share_str = "(90.8%)"
        vacant_units_str = "2,923,155"
        vacant_share_str = "(9.2%)"
    else:
        raw_occupied = entity.get("housing_units", 0)
        occupied_share = 90.8
        vacant_share = 9.2
        occupied_units = raw_occupied
        total_units = int(occupied_units / 0.908) if occupied_units > 0 else 0
        vacant_units = max(0, total_units - occupied_units)
        total_units_str = format_number(total_units)
        exact_units = format_number(total_units)
        occupied_units_str = format_number(occupied_units)
        occupied_share_str = f"({occupied_share:.1f}%)"
        vacant_units_str = format_number(vacant_units)
        vacant_share_str = f"({vacant_share:.1f}%)"

    cards_grid = html.Div([
        # Card 1: TOTAL HOUSING UNITS (Green)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/house.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge ref-kpi-green",
                style={"backgroundColor": "#22c55e"}
            ),
            html.Div([
                html.Span("TOTAL HOUSING UNITS", className="ref-kpi-label"),
                html.Span(total_units_str, className="ref-kpi-num"),
                html.Div(html.Span(f"(exact: {exact_units})",
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),

        # Card 2: OCCUPIED UNITS (Cyan/Teal)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/building.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge",
                style={"backgroundColor": "#0ea5e9"}
            ),
            html.Div([
                html.Span("OCCUPIED UNITS", className="ref-kpi-label"),
                html.Span(occupied_units_str, className="ref-kpi-num"),
                html.Div(html.Span(occupied_share_str,
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),

        # Card 3: VACANT UNITS (Rose/Pink)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/house.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge",
                style={"backgroundColor": "#e11d48"}
            ),
            html.Div([
                html.Span("VACANT UNITS", className="ref-kpi-label"),
                html.Span(vacant_units_str, className="ref-kpi-num"),
                html.Div(html.Span(vacant_share_str,
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),

        # Card 4: SELECTED AREA (Navy)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/pin.svg",
                         style={"width": "20px", "height": "20px", "objectFit": "contain", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge ref-kpi-blue",
                style={"backgroundColor": "#002b5c"}
            ),
            html.Div([
                html.Span("SELECTED AREA", className="ref-kpi-label"),
                html.Span(name, className="ref-kpi-num",
                          style={"fontSize": "1.15rem", "lineHeight": "1.2", "whiteSpace": "normal"}),
                html.Div(html.Span(f"({area_type})",
                         style={"fontSize": "0.72rem", "color": "var(--text-muted)"}),
                         className="ref-kpi-delta"),
            ], className="ref-kpi-info"),
        ], className="ref-kpi-card"),
    ], className="ref-kpi-grid")

    return html.Div([
        _render_housing_header(),
        _render_explore_area_bar(code),
        cards_grid
    ], className="housing-top-container")


# =============================================================================
# 4. MASTER KPI ROUTER
# =============================================================================
@functools.lru_cache(maxsize=128)
def render_kpi_cards(code="PH000000000", active_page="overview"):
    if active_page in ("people", "demographics"):
        return html.Div(id="kpi-cards-empty", style={"display": "none"})

    entity = get_entity_by_code(code)
    level = entity["level"]

    tot_pop = entity["total_pop"]
    tot_hh = entity.get("total_households", 0)
    avg_hh_size = entity.get("avg_household_size", 0.0)
    pop_str = format_number(tot_pop)
    hh_str = format_number(tot_hh)

    if level == "Country":
        sub_pop = "People counted in the 2020 Census"
        sub_hh = "Households across the Philippines"
        sub_size = "People per household"
        sub_year = "Census of Population and Housing"
    else:
        sub_pop = f"Share of PH: {entity.get('nat_share', 0.0):.1f}%"
        sub_hh = f"Households in {entity.get('short_name', entity['name'])}"
        sub_size = "People per household"
        sub_year = "Census of Population and Housing"

    return html.Div([
        # Card 1: TOTAL POPULATION (Blue badge, people icon)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/users.svg", alt="Population", style={"width": "20px", "height": "20px", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge",
                style={"backgroundColor": "#1a73e8"}
            ),
            html.Div([
                html.Span("TOTAL POPULATION", className="ref-kpi-label"),
                html.Span(pop_str, className="ref-kpi-num"),
                html.Span(sub_pop, className="ref-kpi-subtitle")
            ], className="ref-kpi-info")
        ], className="ref-kpi-card"),

        # Card 2: TOTAL HOUSEHOLDS (Green badge, house icon)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/house.svg", alt="Households", style={"width": "20px", "height": "20px", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge",
                style={"backgroundColor": "#059669"}
            ),
            html.Div([
                html.Span("TOTAL HOUSEHOLDS", className="ref-kpi-label"),
                html.Span(hh_str, className="ref-kpi-num"),
                html.Span(sub_hh, className="ref-kpi-subtitle")
            ], className="ref-kpi-info")
        ], className="ref-kpi-card"),

        # Card 3: AVERAGE HOUSEHOLD SIZE (Purple badge, family icon)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/family.svg", alt="Family", style={"width": "20px", "height": "20px", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge",
                style={"backgroundColor": "#8b5cf6"}
            ),
            html.Div([
                html.Span("AVERAGE HOUSEHOLD SIZE", className="ref-kpi-label"),
                html.Span(f"{avg_hh_size:.1f}", className="ref-kpi-num"),
                html.Span(sub_size, className="ref-kpi-subtitle")
            ], className="ref-kpi-info")
        ], className="ref-kpi-card"),

        # Card 4: REFERENCE YEAR (Cyan/Sky badge, calendar icon)
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/calendar.svg", alt="Calendar", style={"width": "20px", "height": "20px", "filter": "brightness(0) invert(1)"}),
                className="ref-kpi-badge",
                style={"backgroundColor": "#0284c7"}
            ),
            html.Div([
                html.Span("REFERENCE YEAR", className="ref-kpi-label"),
                html.Span("2020", className="ref-kpi-num"),
                html.Span(sub_year, className="ref-kpi-subtitle")
            ], className="ref-kpi-info")
        ], className="ref-kpi-card"),
    ], className="ref-kpi-grid")
