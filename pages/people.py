"""
People & Demographics Page Layout.
Answers 'Who lives in the Philippines?' using 2020 CPH Age & Sex data.
Includes Population Pyramid, Age cohorts, Sex breakdown, and Dependency metrics.
"""
from dash import html
from components.place_profile import render_follow_the_number
from components.population_pyramid import render_population_pyramid, render_age_distribution_chart
from components.charts import render_sex_distribution_chart
from utils.data_loader import get_entity_by_code
from utils.formatting import format_number, format_percentage

def render_people_page(selected_code="PH000000000"):
    entity = get_entity_by_code(selected_code)

    tot = entity["total_pop"]
    m = entity["male_pop"]
    f = entity["female_pop"]
    young = entity["young_pop"]
    work = entity["working_pop"]
    old = entity["elderly_pop"]

    return html.Div([
        render_follow_the_number(selected_code),

        # Demographics Summary Cards
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/users.svg", alt="Children", style={"width": "24px", "height": "24px"}),
                html.Div([
                    html.Span("CHILDREN (0-14)", className="kpi-label"),
                    html.Span(format_number(young), className="kpi-value", style={"fontSize": "1.3rem"}),
                    html.Span(f"{entity['young_share']:.1f}% of total population", className="kpi-subtext")
                ])
            ], className="kpi-card", style={"flex": "1"}),

            html.Div([
                html.Img(src="/assets/icons/users.svg", alt="Working Age", style={"width": "24px", "height": "24px"}),
                html.Div([
                    html.Span("WORKING-AGE (15-64)", className="kpi-label"),
                    html.Span(format_number(work), className="kpi-value", style={"fontSize": "1.3rem"}),
                    html.Span(f"{entity['working_share']:.1f}% of total population", className="kpi-subtext")
                ])
            ], className="kpi-card", style={"flex": "1"}),

            html.Div([
                html.Img(src="/assets/icons/family.svg", alt="Seniors", style={"width": "24px", "height": "24px"}),
                html.Div([
                    html.Span("SENIORS (65+)", className="kpi-label"),
                    html.Span(format_number(old), className="kpi-value", style={"fontSize": "1.3rem"}),
                    html.Span(f"{entity['elderly_share']:.1f}% of total population", className="kpi-subtext")
                ])
            ], className="kpi-card", style={"flex": "1"}),

            html.Div([
                html.Img(src="/assets/icons/chart.svg", alt="Dependency", style={"width": "24px", "height": "24px"}),
                html.Div([
                    html.Span("DEPENDENCY RATIO", className="kpi-label"),
                    html.Span(f"{entity['dependency_ratio']:.1f}", className="kpi-value", style={"fontSize": "1.3rem"}),
                    html.Span("Dependents per 100 working-age", className="kpi-subtext")
                ])
            ], className="kpi-card", style={"flex": "1"})
        ], style={"display": "flex", "gap": "16px", "marginBottom": "20px", "flexWrap": "wrap"}),

        # Two-column layout for Pyramid & Age chart
        html.Div([
            html.Div([
                render_population_pyramid(selected_code)
            ], style={"flex": "1.2", "minWidth": "380px"}),

            html.Div([
                render_sex_distribution_chart(selected_code),
                html.Div(style={"height": "16px"}),
                render_age_distribution_chart(selected_code)
            ], style={"flex": "1", "minWidth": "340px"})
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"})
    ])
