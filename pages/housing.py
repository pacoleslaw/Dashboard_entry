"""
Housing Page Layout.
Deep-dive into occupied housing units and types of building structures.
"""
from dash import html, dcc
import plotly.graph_objects as go
from components.place_profile import render_follow_the_number
from components.charts import render_housing_types_donut
from utils.data_loader import get_entity_by_code
from utils.formatting import format_number, format_compact

def render_housing_page(selected_code="PH000000000"):
    entity = get_entity_by_code(selected_code)
    tot_units = entity.get("housing_units", 0)
    h_types = entity.get("housing_types", {})

    single = h_types.get("Single House", 0)
    duplex = h_types.get("Duplex", 0)
    apt = h_types.get("Apartment/Condo", 0)
    others = h_types.get("Others", 0)

    # Bar chart of building types
    labels = list(h_types.keys())
    values = list(h_types.values())

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=labels,
        y=values,
        text=[f"{format_compact(v)} ({(v / tot_units)*100:.1f}%)" if tot_units > 0 else "0" for v in values],
        textposition='outside',
        marker=dict(color=["#2563eb", "#0284c7", "#f97316", "#8b5cf6"])
    ))
    fig_bar.update_layout(
        title=dict(text=f"<b>Housing Units by Building Structure: {entity['name']}</b>", font=dict(size=13, color="#002d62", family="Outfit, sans-serif")),
        margin=dict(l=20, r=20, t=35, b=30),
        yaxis=dict(title="Housing Units", tickformat=","),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=320
    )

    return html.Div([
        render_follow_the_number(selected_code),

        # Top Summary Badges
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/building.svg", alt="Building", style={"width": "24px", "height": "24px"}),
                html.Div([
                    html.Span("TOTAL HOUSING UNITS", className="kpi-label"),
                    html.Span(format_number(tot_units), className="kpi-value", style={"fontSize": "1.4rem"}),
                    html.Span("Occupied Housing Units", className="kpi-subtext")
                ])
            ], className="kpi-card", style={"flex": "1"}),

            html.Div([
                html.Img(src="/assets/icons/house.svg", alt="Single Houses", style={"width": "24px", "height": "24px"}),
                html.Div([
                    html.Span("SINGLE HOUSES", className="kpi-label"),
                    html.Span(format_number(single), className="kpi-value", style={"fontSize": "1.4rem"}),
                    html.Span(f"{(single / tot_units)*100:.1f}% of all units" if tot_units > 0 else "", className="kpi-subtext")
                ])
            ], className="kpi-card", style={"flex": "1"}),

            html.Div([
                html.Img(src="/assets/icons/building.svg", alt="Multi-Unit", style={"width": "24px", "height": "24px"}),
                html.Div([
                    html.Span("MULTI-UNIT RESIDENTIAL", className="kpi-label"),
                    html.Span(format_number(duplex + apt), className="kpi-value", style={"fontSize": "1.4rem"}),
                    html.Span(f"{((duplex + apt) / tot_units)*100:.1f}% of all units" if tot_units > 0 else "", className="kpi-subtext")
                ])
            ], className="kpi-card", style={"flex": "1"})
        ], style={"display": "flex", "gap": "16px", "marginBottom": "20px", "flexWrap": "wrap"}),

        # Two-column layout
        html.Div([
            html.Div([
                render_housing_types_donut(selected_code),
                html.Div([
                    html.Div([
                        html.Img(src="/assets/icons/chart.svg", alt="Table", style={"width": "15px", "height": "15px", "marginRight": "6px"}),
                        html.Span(f"Building Type Breakdown ({entity['name']})", style={"fontWeight": "700", "fontSize": "0.85rem", "color": "var(--psa-navy)"})
                    ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
                    html.Table([
                        html.Thead(html.Tr([
                            html.Th("Building Structure Type"),
                            html.Th("Occupied Units", style={"textAlign": "right"}),
                            html.Th("Share (%)", style={"textAlign": "right"})
                        ])),
                        html.Tbody([
                            html.Tr([
                                html.Td(k, style={"fontWeight": "600"}),
                                html.Td(format_number(v), style={"textAlign": "right"}),
                                html.Td(f"{(v / tot_units)*100:.1f}%" if tot_units > 0 else "0%", style={"textAlign": "right", "fontWeight": "600"})
                            ], style={"backgroundColor": "#f8fafc" if i % 2 == 0 else "#ffffff"})
                            for i, (k, v) in enumerate(h_types.items())
                        ])
                    ], style={"width": "100%", "borderCollapse": "collapse", "fontSize": "0.82rem", "border": "1px solid var(--border-color)"})
                ], className="panel-card")
            ], style={"flex": "1", "minWidth": "340px"}),

            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_bar, config={"displayModeBar": False, "responsive": True})
                ], className="panel-card")
            ], style={"flex": "1.2", "minWidth": "360px"})
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"})
    ])
