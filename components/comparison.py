"""
Compare Places Component.
Allows side-by-side comparison of two geographic areas across official population,
sex distribution, dependency ratios, and age groups without normative ranking.
"""
from dash import html, dcc
import plotly.graph_objects as go
from utils.data_loader import load_population_data, get_entity_by_code
from utils.calculations import compare_two_entities
from utils.formatting import format_number, format_percentage, format_compact

def render_comparison_interface(code_a="PH040000000", code_b="PH130000000"):
    entities = load_population_data()
    # Options grouped or sorted
    options = [{"label": f"{e['name']} ({e['level']})", "value": e["code"]} for e in entities if e["level"] != "Country"]

    comp = compare_two_entities(code_a, code_b)
    ea = comp["entity_a"]
    eb = comp["entity_b"]

    # Comparative table rows
    metrics = [
        ("Total Population", format_number(ea["total_pop"]), format_number(eb["total_pop"])),
        ("National Population Share", f"{ea['nat_share']:.2f}%", f"{eb['nat_share']:.2f}%"),
        ("Male Population", f"{format_number(ea['male_pop'])} ({ea['male_share']:.1f}%)", f"{format_number(eb['male_pop'])} ({eb['male_share']:.1f}%)"),
        ("Female Population", f"{format_number(ea['female_pop'])} ({ea['female_share']:.1f}%)", f"{format_number(eb['female_pop'])} ({eb['female_share']:.1f}%)"),
        ("Sex Ratio (Males/100 Females)", f"{ea['sex_ratio']:.1f}", f"{eb['sex_ratio']:.1f}"),
        ("Age Dependency Ratio", f"{ea['dependency_ratio']:.1f}", f"{eb['dependency_ratio']:.1f}"),
        ("Working-Age Share (15-64)", f"{ea['working_share']:.1f}%", f"{eb['working_share']:.1f}%"),
        ("Children Share (Under 15)", f"{ea['young_share']:.1f}%", f"{eb['young_share']:.1f}%"),
        ("Senior Share (65+)", f"{ea['elderly_share']:.1f}%", f"{eb['elderly_share']:.1f}%"),
    ]

    # Side-by-side grouped bar chart of age groups
    age_groups = ea["age_groups"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=age_groups,
        y=[ea["age_both"].get(g, 0) for g in age_groups],
        name=ea["short_name"],
        marker=dict(color="#2563eb")
    ))
    fig.add_trace(go.Bar(
        x=age_groups,
        y=[eb["age_both"].get(g, 0) for g in age_groups],
        name=eb["short_name"],
        marker=dict(color="#d97706")
    ))
    fig.update_layout(
        title=dict(
            text=f"<b>Age Cohort Distribution: {ea['short_name']} vs {eb['short_name']}</b>",
            font=dict(size=13, color="#002d62", family="Outfit, sans-serif"),
            x=0.02
        ),
        barmode='group',
        margin=dict(l=30, r=20, t=40, b=50),
        xaxis=dict(tickangle=-45, tickfont=dict(size=9, family="Inter, sans-serif")),
        yaxis=dict(title="Persons", tickformat=","),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=320
    )

    return html.Div([
        # Selection Bar
        html.Div([
            html.Div([
                html.Label("PLACE A", style={"fontWeight": "700", "fontSize": "0.78rem", "color": "#1d4ed8"}),
                dcc.Dropdown(
                    id={"type": "compare-dropdown-a", "id": "main"},
                    options=options,
                    value=code_a,
                    clearable=False,
                    style={"fontSize": "0.82rem"}
                )
            ], className="compare-select-col"),

            html.Div([
                html.Span("VS", className="compare-vs-text")
            ], className="compare-vs-badge"),

            html.Div([
                html.Label("PLACE B", style={"fontWeight": "700", "fontSize": "0.78rem", "color": "#b45309"}),
                dcc.Dropdown(
                    id={"type": "compare-dropdown-b", "id": "main"},
                    options=options,
                    value=code_b,
                    clearable=False,
                    style={"fontSize": "0.82rem"}
                )
            ], className="compare-select-col")
        ], className="compare-select-bar"),

        # Summary Banner
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/info.svg", style={"width": "16px", "height": "16px", "marginRight": "8px", "verticalAlign": "middle"}),
                html.Span(
                    f"Comparing {ea['name']} ({format_compact(ea['total_pop'])}) and {eb['name']} ({format_compact(eb['total_pop'])}). "
                    f"Difference: {format_number(comp['pop_difference'])} residents ({comp['pop_diff_pct']:+.1f}%). "
                    "All indicators are purely descriptive and derived from the 2020 CPH.",
                    style={"fontSize": "0.82rem", "color": "#1e293b"}
                )
            ])
        ], style={"background": "#eff6ff", "border": "1px solid #bfdbfe", "borderRadius": "var(--radius-sm)", "padding": "10px 14px", "marginBottom": "16px"}),

        # Comparison Table (Horizontal scroll wrapper for mobile)
        html.Div([
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Indicator", style={"width": "40%", "minWidth": "140px"}),
                    html.Th(ea["name"], style={"width": "30%", "minWidth": "100px", "color": "#1d4ed8", "textAlign": "right"}),
                    html.Th(eb["name"], style={"width": "30%", "minWidth": "100px", "color": "#b45309", "textAlign": "right"})
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(m[0], style={"fontWeight": "600"}),
                        html.Td(m[1], style={"textAlign": "right", "fontWeight": "600"}),
                        html.Td(m[2], style={"textAlign": "right", "fontWeight": "600"})
                    ], style={"backgroundColor": "#f8fafc" if i % 2 == 0 else "#ffffff"})
                    for i, m in enumerate(metrics)
                ])
            ], style={"width": "100%", "borderCollapse": "collapse", "fontSize": "0.82rem", "border": "1px solid var(--border-color)"})
        ], className="ref-table-responsive"),

        # Age Breakdown Chart
        dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True})
    ], className="panel-card")
