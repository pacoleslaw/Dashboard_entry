"""
Quick Insights Component reproducing the exact layout and content from the reference image.
Features:
- Header: Lightbulb icon + "Quick Insights" with subtitle "Key highlights from the data"
- 3 interactive insight rows with icons, titles, summaries, and right chevrons:
  1. People
  2. Households
  3. Geographic Coverage
- Bottom promo banner: "Discover more about People, Places and Progress →"
"""
from dash import html
from utils.data_loader import get_entity_by_code
from utils.formatting import format_compact, format_number
from utils.narratives import get_did_you_know


def render_quick_insights(selected_code="PH000000000"):
    entity = get_entity_by_code(selected_code)
    level = entity["level"]
    name = entity.get("short_name", entity["name"])

    if level == "Country":
        people_desc = "The Philippines has 109.0 million people, with 14.9% living in Region IV-A (CALABARZON)."
        hh_desc = "There are 26.4 million households in the Philippines, with an average of 4.1 persons per household."
        geo_desc = "You can explore the data from the national level down to the city/municipality level."
    else:
        tot_pop = entity["total_pop"]
        tot_hh = entity.get("total_households", 0)
        avg_hh = entity.get("avg_household_size", 0.0)
        people_desc = f"{name} has {format_compact(tot_pop)} people ({format_number(tot_pop)}), accounting for {entity.get('nat_share', 0.0):.1f}% of the Philippine population."
        hh_desc = f"There are {format_compact(tot_hh)} households in this area with an average of {avg_hh:.1f} persons per household."
        geo_desc = f"You can explore constituent provinces, cities and municipalities under {name}."

    items = [
        {
            "id": "insight-people",
            "page": "people",
            "icon": "/assets/icons/users.svg",
            "badge_color": "#1a73e8",
            "title": "People",
            "text": people_desc
        },
        {
            "id": "insight-households",
            "page": "households",
            "icon": "/assets/icons/house.svg",
            "badge_color": "#059669",
            "title": "Households",
            "text": hh_desc
        },
        {
            "id": "insight-geo",
            "page": "places",
            "icon": "/assets/icons/pin.svg",
            "badge_color": "#0284c7",
            "title": "Geographic Coverage",
            "text": geo_desc
        }
    ]

    return html.Div([
        # Header
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/lightbulb.svg", alt="Insights", style={"width": "20px", "height": "20px"}),
                html.Span("Quick Insights", className="ref-qi-title")
            ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),
            html.Div("Key highlights from the data", className="ref-qi-subtitle")
        ], style={"marginBottom": "16px"}),

        # Insight Items List
        html.Div([
            html.Button([
                html.Div(
                    html.Img(src=item["icon"], style={"width": "18px", "height": "18px", "filter": "brightness(0) invert(1)"}),
                    className="ref-qi-icon-badge",
                    style={"backgroundColor": item["badge_color"]}
                ),
                html.Div([
                    html.Div(item["title"], className="ref-qi-item-title"),
                    html.Div(item["text"], className="ref-qi-item-text")
                ], className="ref-qi-item-body"),
                html.Div("›", className="ref-qi-chevron")
            ],
            id={"type": "nav-btn", "page": item["page"], "source": f"insight-{item['id']}"},
            className="ref-qi-item-btn",
            title=f"Explore {item['title']}"
            )
            for item in items
        ], className="ref-qi-list"),

        # Bottom Promo Banner
        html.Button([
            html.Div(
                html.Img(src="/assets/icons/chart.svg", style={"width": "18px", "height": "18px", "filter": "brightness(0) invert(1)"}),
                className="ref-qi-promo-icon-badge"
            ),
            html.Span("Discover more about People, Places and Progress", className="ref-qi-promo-text"),
            html.Span("→", className="ref-qi-promo-arrow")
        ],
        id={"type": "nav-btn", "page": "places", "source": "insight-promo"},
        className="ref-qi-promo-card",
        title="Discover more in Places"
        )
    ], className="ref-panel ref-quick-insights-panel")


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
