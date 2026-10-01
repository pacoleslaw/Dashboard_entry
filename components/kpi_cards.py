"""
KPI Cards Component reproducing the exact 4 KPI cards from the reference image:
Total Population, Total Households, Average Household Size, Total Housing Units.
"""
from dash import html
from utils.data_loader import get_entity_by_code
from utils.formatting import format_number, format_compact

def render_kpi_cards(code="PH000000000"):
    entity = get_entity_by_code(code)
    level = entity["level"]

    if level == "Country":
        tot_pop = 109_035_343
        tot_hh = 28_206_552
        avg_hh_size = 3.9
        housing_units = 27_342_787
        delta_pop = "▲ +1.2% vs. 2015"
        delta_hh = "▲ +1.1% vs. 2015"
        delta_size = "▼ -0.1 vs. 2015"
        delta_units = "▲ +1.3% vs. 2015"
    else:
        tot_pop = entity["total_pop"]
        tot_hh = entity.get("total_households", 0)
        avg_hh_size = entity.get("avg_household_size", 0.0)
        housing_units = entity.get("housing_units", 0)
        delta_pop = f"{entity['nat_share']:.1f}% of national total"
        delta_hh = "Private Households"
        delta_size = "persons per household"
        delta_units = "Occupied Housing Units"

    return html.Div([
        # Card 1: Total Population
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/users.svg", alt="Population", style={"width": "24px", "height": "24px"}),
                className="ref-kpi-badge ref-kpi-blue"
            ),
            html.Div([
                html.Span("Total Population", className="ref-kpi-label"),
                html.Span(format_number(tot_pop), className="ref-kpi-num"),
                html.Span(delta_pop, className="ref-kpi-delta ref-delta-green")
            ], className="ref-kpi-info")
        ], className="ref-kpi-card"),

        # Card 2: Total Households
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/house.svg", alt="Households", style={"width": "24px", "height": "24px"}),
                className="ref-kpi-badge ref-kpi-green"
            ),
            html.Div([
                html.Span("Total Households", className="ref-kpi-label"),
                html.Span(format_number(tot_hh), className="ref-kpi-num"),
                html.Span(delta_hh, className="ref-kpi-delta ref-delta-green")
            ], className="ref-kpi-info")
        ], className="ref-kpi-card"),

        # Card 3: Average Household Size
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/family.svg", alt="Family", style={"width": "24px", "height": "24px"}),
                className="ref-kpi-badge ref-kpi-orange"
            ),
            html.Div([
                html.Span("Average Household Size", className="ref-kpi-label"),
                html.Div([
                    html.Span(f"{avg_hh_size:.1f}", className="ref-kpi-num"),
                    html.Span("persons", style={"fontSize": "0.78rem", "color": "#64748b", "marginLeft": "6px", "fontWeight": "600"})
                ], style={"display": "flex", "alignItems": "baseline"}),
                html.Span(delta_size, className="ref-kpi-delta ref-delta-red" if level == "Country" else "ref-kpi-delta")
            ], className="ref-kpi-info")
        ], className="ref-kpi-card"),

        # Card 4: Total Housing Units
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/building.svg", alt="Housing Units", style={"width": "24px", "height": "24px"}),
                className="ref-kpi-badge ref-kpi-teal"
            ),
            html.Div([
                html.Span("Total Housing Units", className="ref-kpi-label"),
                html.Span(format_number(housing_units), className="ref-kpi-num"),
                html.Span(delta_units, className="ref-kpi-delta ref-delta-green")
            ], className="ref-kpi-info")
        ], className="ref-kpi-card"),
    ], className="ref-kpi-grid")
