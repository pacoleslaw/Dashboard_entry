"""
Quick Insights and Did You Know Components reproducing the exact layout from the reference image.
"""
from dash import html
from utils.data_loader import get_entity_by_code
from utils.formatting import format_compact, format_number
from utils.narratives import get_did_you_know

def render_quick_insights(selected_code="PH000000000"):
    entity = get_entity_by_code(selected_code)
    level = entity["level"]
    name = entity["name"]
    tot_pop = entity["total_pop"]
    avg_hh = entity.get("avg_household_size", 4.1)

    # Dynamic 4 bullets tailored to the reference design
    if level == "Country":
        bullets = [
            ("/assets/icons/insight_users.svg", "The Philippines' population reached 109.0 million in 2020, up by 1.2% from 2015."),
            ("/assets/icons/insight_house.svg", "An average household has 3.9 members, slightly lower than 2015 (4.0)."),
            ("/assets/icons/insight_building.svg", "Single houses remain the most common type of housing unit (72.1%)."),
            ("/assets/icons/insight_trend.svg", "NCR has the highest population, followed by Region IV-A and Region III.")
        ]
    else:
        bullets = [
            ("/assets/icons/insight_users.svg", f"{name} had {format_compact(tot_pop)} ({format_number(tot_pop)}) residents in the 2020 Census."),
            ("/assets/icons/insight_house.svg", f"An average household in this area has {avg_hh:.1f} persons ({format_compact(entity.get('total_households', 0))} households)."),
            ("/assets/icons/insight_building.svg", f"Occupied housing units total {format_compact(entity.get('housing_units', 0))} with single houses as the primary structure."),
            ("/assets/icons/insight_trend.svg", f"Accounts for {entity['nat_share']:.1f}% of the Philippine national population.")
        ]

    return html.Div([
        html.Div([
            html.Img(src="/assets/icons/lightbulb.svg", alt="Insights", style={"width": "16px", "height": "16px"}),
            html.Span("Quick Insights", className="ref-panel-title", style={"marginBottom": "0"})
        ], style={"display": "flex", "alignItems": "center", "gap": "6px", "marginBottom": "10px"}),

        html.Div([
            html.Div([
                html.Div(
                    html.Img(src=icon_path, style={"width": "18px", "height": "18px"}),
                    className="ref-insight-icon-box"
                ),
                html.P(text, className="ref-insight-text")
            ], className="ref-insight-item")
            for icon_path, text in bullets
        ])
    ], className="ref-panel", style={"padding": "12px 14px", "marginBottom": "0px"})

def render_did_you_know(selected_code="PH000000000"):
    entity = get_entity_by_code(selected_code)
    if entity["level"] == "Country":
        text = "The NCR has the largest share of the total population, with 12.7% or 13.9 million people."
    else:
        dyk = get_did_you_know(selected_code)
        text = dyk["text"]

    return html.Div([
        html.Div(
            html.Img(src="/assets/icons/lightbulb.svg", alt="Did you know", style={"width": "22px", "height": "22px"}),
            className="ref-dyk-icon"
        ),
        html.Div([
            html.Div("Did you know?", className="ref-dyk-title"),
            html.P(text, className="ref-dyk-text")
        ])
    ], className="ref-did-you-know")
