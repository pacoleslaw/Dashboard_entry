"""
Households Page Layout.
Deep-dive into household population, average household size, and occupant distributions.
"""
from dash import html, dcc
import plotly.graph_objects as go
from components.place_profile import render_follow_the_number
from components.charts import render_household_size_donut
from utils.data_loader import get_entity_by_code
from utils.geography import get_regions, get_provinces
from utils.formatting import format_number, format_compact

def render_households_page(selected_code="PH000000000"):
    entity = get_entity_by_code(selected_code)
    tot_hh = entity["total_households"]
    hh_pop = entity["household_pop"]
    avg_size = entity["avg_household_size"]
    hh_sizes = entity.get("household_sizes", {})

    # Peer chart for Average Household Size
    if entity["level"] == "Country":
        peers = get_regions()
        title_peers = "Average Household Size by Region (persons)"
    else:
        reg_code = entity["code"] if entity["level"] == "Region" else entity.get("parent_code", "PH130000000")
        peers = get_provinces(reg_code)
        title_peers = f"Average Household Size in {get_entity_by_code(reg_code)['name']}"

    sorted_peers = sorted(peers, key=lambda x: x.get("avg_household_size", 0), reverse=True)[:15]
    rev_peers = list(reversed(sorted_peers))

    fig_peer = go.Figure()
    fig_peer.add_trace(go.Bar(
        y=[p["short_name"] for p in rev_peers],
        x=[p.get("avg_household_size", 0) for p in rev_peers],
        orientation='h',
        text=[f"{p.get('avg_household_size', 0):.1f}" for p in rev_peers],
        textposition='outside',
        marker=dict(color=["#f59e0b" if p["code"] == selected_code else "#059669" for p in rev_peers])
    ))
    fig_peer.update_layout(
        title=dict(text=f"<b>{title_peers}</b>", font=dict(size=13, color="#002d62", family="Outfit, sans-serif")),
        margin=dict(l=10, r=40, t=35, b=20),
        xaxis=dict(title="Persons per Household", range=[0, 6]),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=320
    )

    return html.Div([
        render_follow_the_number(selected_code),

        # Top Summary Badges
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/house.svg", style={"width": "28px", "height": "28px", "objectFit": "contain"}),
                html.Div([
                    html.Span("TOTAL HOUSEHOLDS", className="kpi-label"),
                    html.Span(format_number(tot_hh), className="kpi-value", style={"fontSize": "1.4rem"}),
                    html.Span("Enumerated in 2020 CPH", className="kpi-subtext")
                ])
            ], className="kpi-card", style={"flex": "1"}),

            html.Div([
                html.Img(src="/assets/icons/users.svg", style={"width": "28px", "height": "28px", "objectFit": "contain"}),
                html.Div([
                    html.Span("HOUSEHOLD POPULATION", className="kpi-label"),
                    html.Span(format_number(hh_pop), className="kpi-value", style={"fontSize": "1.4rem"}),
                    html.Span("Excludes institutional quarters", className="kpi-subtext")
                ])
            ], className="kpi-card", style={"flex": "1"}),

            html.Div([
                html.Img(src="/assets/icons/family.svg", style={"width": "28px", "height": "28px", "objectFit": "contain"}),
                html.Div([
                    html.Span("AVERAGE HOUSEHOLD SIZE", className="kpi-label"),
                    html.Span(f"{avg_size:.1f} persons", className="kpi-value", style={"fontSize": "1.4rem"}),
                    html.Span("Persons per household", className="kpi-subtext")
                ])
            ], className="kpi-card", style={"flex": "1"})
        ], style={"display": "flex", "gap": "16px", "marginBottom": "20px", "flexWrap": "wrap"}),

        # Two-column layout
        html.Div([
            html.Div([
                render_household_size_donut(selected_code),
                html.Div([
                    html.Div([
                        html.Img(src="/assets/icons/chart.svg", style={"width": "18px", "height": "18px", "marginRight": "6px", "verticalAlign": "middle"}),
                        html.Span(f"Household Size Breakdown ({entity['name']})", style={"fontWeight": "700", "fontSize": "0.85rem", "color": "var(--psa-navy)"})
                    ], style={"marginBottom": "8px"}),
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("Household Size"),
                            html.Th("Number of Households", style={"textAlign": "right"}),
                            html.Th("Share (%)", style={"textAlign": "right"})
                        ])),
                        html.Tbody([
                            html.Tr([
                                html.Td(k, style={"fontWeight": "600"}),
                                html.Td(format_number(v), style={"textAlign": "right"}),
                                html.Td(f"{(v / tot_hh)*100:.1f}%" if tot_hh > 0 else "0%", style={"textAlign": "right", "fontWeight": "600"})
                            ], style={"backgroundColor": "#f8fafc" if i % 2 == 0 else "#ffffff"})
                            for i, (k, v) in enumerate(hh_sizes.items())
                        ])
                    ], style={"width": "100%", "borderCollapse": "collapse", "fontSize": "0.82rem", "border": "1px solid var(--border-color)"})
                ], className="panel-card")
            ], style={"flex": "1", "minWidth": "340px"}),

            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_peer, config={"displayModeBar": False, "responsive": True})
                ], className="panel-card")
            ], style={"flex": "1.2", "minWidth": "360px"})
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"})
    ])
