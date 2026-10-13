"""
People & Demographics Page Layout.
Faithfully reproduces the reference UI with:
- Demographics Top Header: Badge, Title ('DEMOGRAPHICS'), Subtitle ('Who makes up the population?')
  and 'EXPLORE THIS AREA' 4-dropdown cascade (Country, Region, Province, City/Municipality)
- 4 Top KPI Cards directly aligned with the 4 columns below:
  [TOTAL POPULATION] [• MALE] [• FEMALE] [• MEDIAN AGE]
- 4-Column Content Grid:
  - Column 1: Population Pyramid (bilateral bars, View By/Age Group dropdowns, zoom/recenter controls)
  - Column 2: Population by Age Group (horizontal bar chart with 17 gradient bars and percentage labels)
  - Column 3: Population by Sex (donut chart with center total population and 'What does this mean?' info callout)
  - Column 4: Explore a Place (metrics table, callout box, Compare button) & Quick Insights (3 icon bullets)
"""
import functools
from dash import html
from components.demographics import (
    render_demographics_top_header,
    render_demographics_kpi_cards,
    render_demographics_pyramid_card,
    render_demographics_age_bar_card,
    render_demographics_sex_donut_card,
    render_demographics_profile_insights_card
)

@functools.lru_cache(maxsize=32)
def render_people_page(selected_code="PH000000000"):
    """Renders the complete redesigned Demographics page matching the reference image."""
    return html.Div([
        # 1. Top Header with 4-dropdown explore cascade
        render_demographics_top_header(selected_code),

        # 2. 4 Top KPI Cards aligned with the 4 columns below
        render_demographics_kpi_cards(selected_code),

        # 3. 4-Column Main Content Grid
        html.Div([
            # Column 1: Population Pyramid
            render_demographics_pyramid_card(selected_code),

            # Column 2: Population by Age Group
            render_demographics_age_bar_card(selected_code),

            # Column 3: Population by Sex
            render_demographics_sex_donut_card(selected_code),

            # Column 4: Explore a Place & Quick Insights
            render_demographics_profile_insights_card(selected_code),
        ], className="demo-content-grid")
    ], style={"display": "flex", "flexDirection": "column"})
