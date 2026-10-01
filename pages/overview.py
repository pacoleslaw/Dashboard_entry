"""
Overview Page Layout reproducing the exact 3-column visual composition of the reference image:
Column 1: Interactive Map
Column 2: Population Bar Chart, Top 5 Table, Did You Know?
Column 3: Household Size Donut, Housing Types Donut, Quick Insights
"""
from dash import html
from components.place_profile import render_follow_the_number
from components.map import render_map_component
from components.charts import (
    render_population_bar_chart,
    render_top_areas_table,
    render_household_size_donut,
    render_housing_types_donut
)
from components.insights import render_quick_insights, render_did_you_know

def render_overview_page(selected_code="PH000000000", indicator="total_pop", map_level="region"):
    elements = []

    # Only show breadcrumbs when drilled down into a region or province
    if selected_code != "PH000000000":
        elements.append(render_follow_the_number(selected_code))

    # 3-Column Grid matching the reference image exactly
    elements.append(
        html.Div([
            # Column 1: Interactive Map (Left)
            html.Div([
                render_map_component(selected_code, indicator, map_level)
            ], style={"minWidth": "0"}),

            # Column 2: Bar Chart, Top 5 Table, Did You Know (Center)
            html.Div([
                # Population Bar Chart
                html.Div([
                    render_population_bar_chart(selected_code)
                ], className="ref-panel", style={"padding": "10px 12px", "marginBottom": "10px"}),

                # Top 5 Table
                render_top_areas_table(selected_code),

                # Did You Know Callout Card
                render_did_you_know(selected_code)
            ], style={"minWidth": "0"}),

            # Column 3: Donut Charts & Quick Insights (Right)
            html.Div([
                # Household Size Donut
                render_household_size_donut(selected_code),

                # Housing Units Donut
                render_housing_types_donut(selected_code),

                # Quick Insights Card
                render_quick_insights(selected_code)
            ], style={"minWidth": "0"})
        ], className="ref-overview-grid")
    )

    return html.Div(elements)
