"""
Places & Geographic Exploration Page Layout.
Answers 'Where do people live?' with interactive map drill-down,
detailed Place Profile, and hierarchy exploration.
"""
from dash import html
from components.place_profile import render_follow_the_number, render_place_profile
from components.map import render_map_component
from components.charts import render_population_bar_chart

def render_places_page(selected_code="PH000000000", indicator="total_pop", map_level="region"):
    return html.Div([
        render_follow_the_number(selected_code),

        # Two-column layout: Map on left, Profile & Bars on right
        html.Div([
            html.Div([
                render_map_component(selected_code, indicator, map_level)
            ], style={"flex": "1.3", "minWidth": "380px"}),

            html.Div([
                render_place_profile(selected_code),
                html.Div([
                    render_population_bar_chart(selected_code)
                ], className="panel-card", style={"padding": "12px 16px", "marginTop": "16px"})
            ], style={"flex": "1.1", "minWidth": "340px"})
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"})
    ])
