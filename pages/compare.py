"""
Compare Places Page Layout.
Facilitates side-by-side descriptive comparison between any two geographic locations.
"""
import functools
from dash import html
from components.comparison import render_comparison_interface

@functools.lru_cache(maxsize=32)
def render_compare_page(code_a="PH040000000", code_b="PH130000000"):
    return html.Div([
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/chart.svg", style={"width": "22px", "height": "22px", "marginRight": "8px", "verticalAlign": "middle"}),
                html.Span("Compare Places (Descriptive Analysis)", className="panel-title")
            ], className="panel-header"),
            html.P(
                "Select the Philippines or any two regions, provinces, or highly urbanized cities to view side-by-side demographic indicators. "
                "All comparisons are strictly factual and derived from official PSA 2020 CPH records.",
                style={"fontSize": "0.85rem", "color": "var(--text-muted)", "marginBottom": "16px"}
            ),
            render_comparison_interface(code_a, code_b)
        ])
    ])
