"""
Overview Page Layout combining Overview and Population:
1. Top: Aligned 3-Column Visual Composition:
   - Column 1: Interactive Map (with full controls, legend, and header)
   - Column 2: Regional/Provincial Population Bar Chart, Top 5 Areas Table, Did You Know?
   - Column 3: Quick Insights (People, Households, Geographic Coverage, Discover More)
2. Bottom: 4 Exploration Navigation Cards:
   - Explore Banner, Demographics (People), Households, Housing
"""
import functools
from dash import html
from components.place_profile import render_follow_the_number
from components.map import render_map_component
from components.charts import (
    render_population_bar_chart,
    render_top_areas_table
)
from components.insights import render_quick_insights, render_did_you_know


def _build_overview_layout(selected_code="PH000000000", indicator="total_pop", map_level="region", manual_nav=False, viewport=None):
    elements = []

    # Only show breadcrumbs when drilled down into a region or province
    if selected_code != "PH000000000":
        elements.append(render_follow_the_number(selected_code))

    # 1. Main Middle Section: 3-Column Grid with aligned card bottoms matching reference
    elements.append(
        html.Div([
            # Column 1: Interactive Map (Left)
            html.Div([
                render_map_component(selected_code, indicator, map_level, manual_nav, viewport, overview_mode=False)
            ], className="pop-col-map", style={"minWidth": "0"}),

            # Column 2: Bar Chart, Top 5 Table, Did You Know (Center)
            html.Div([
                # Population Bar Chart
                html.Div([
                    render_population_bar_chart(selected_code, height=170, indicator=indicator)
                ], className="ref-panel pop-panel-barchart"),

                # Top 5 Table
                render_top_areas_table(selected_code, indicator=indicator),

                # Did You Know Callout Card
                render_did_you_know(selected_code)
            ], className="pop-col-center", style={"minWidth": "0"}),

            # Column 3: Quick Insights (Right)
            html.Div([
                render_quick_insights(selected_code)
            ], className="pop-col-insights", style={"minWidth": "0"})
        ], className="ref-overview-grid ref-population-grid")
    )

    # 2. Bottom Section: 3 Exploration Navigation Cards
    elements.append(
        html.Div([
            # Card 1: Demographics (People)
            html.Div([
                html.Div([
                    html.Div(
                        html.Img(src="/assets/icons/users.svg", alt="Demographics", style={"width": "18px", "height": "18px", "filter": "brightness(0) invert(1)"}),
                        className="feature-nav-badge",
                        style={"backgroundColor": "#1a73e8"}
                    ),
                    html.H4("Who lives in the Philippines?", className="feature-nav-title")
                ], className="feature-nav-header-row"),
                html.P("Explore population by age, sex and more.", className="feature-nav-desc"),
                html.Button(
                    ["Go to Demographics", html.Span(" →", style={"fontSize": "0.9rem", "marginLeft": "4px"})],
                    id={"type": "nav-btn", "page": "people", "source": "overview-card-people"},
                    className="feature-nav-btn"
                )
            ], className="ref-panel feature-nav-card"),

            # Card 3: Households
            html.Div([
                html.Div([
                    html.Div(
                        html.Img(src="/assets/icons/house.svg", alt="Households", style={"width": "18px", "height": "18px", "filter": "brightness(0) invert(1)"}),
                        className="feature-nav-badge",
                        style={"backgroundColor": "#059669"}
                    ),
                    html.H4("How do Filipino households look?", className="feature-nav-title")
                ], className="feature-nav-header-row"),
                html.P("Explore household numbers and household size.", className="feature-nav-desc"),
                html.Button(
                    ["Go to Households", html.Span(" →", style={"fontSize": "0.9rem", "marginLeft": "4px"})],
                    id={"type": "nav-btn", "page": "households", "source": "overview-card-households"},
                    className="feature-nav-btn"
                )
            ], className="ref-panel feature-nav-card"),

            # Card 4: Housing
            html.Div([
                html.Div([
                    html.Div(
                        html.Img(src="/assets/icons/building.svg", alt="Housing", style={"width": "18px", "height": "18px", "filter": "brightness(0) invert(1)"}),
                        className="feature-nav-badge",
                        style={"backgroundColor": "#8b5cf6"}
                    ),
                    html.H4("What do people live in?", className="feature-nav-title")
                ], className="feature-nav-header-row"),
                html.P("Explore housing units and housing characteristics.", className="feature-nav-desc"),
                html.Button(
                    ["Go to Housing", html.Span(" →", style={"fontSize": "0.9rem", "marginLeft": "4px"})],
                    id={"type": "nav-btn", "page": "housing", "source": "overview-card-housing"},
                    className="feature-nav-btn"
                )
            ], className="ref-panel feature-nav-card")
        ], className="ref-overview-bottom-grid")
    )

    return html.Div(elements, className="ref-overview-page-wrapper")


@functools.lru_cache(maxsize=32)
def _render_overview_cached(selected_code, indicator, map_level):
    return _build_overview_layout(selected_code, indicator, map_level, False, None)


def render_overview_page(selected_code="PH000000000", indicator="total_pop", map_level="region", manual_nav=False, viewport=None):
    if not manual_nav or viewport is None:
        return _render_overview_cached(selected_code, indicator, map_level)
    return _build_overview_layout(selected_code, indicator, map_level, manual_nav, viewport)
