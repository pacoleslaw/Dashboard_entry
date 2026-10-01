"""
Chart Components for Population, Household, and Housing Analysis.
Provides horizontal bar charts, top 5 tables, sex distributions,
and donut charts for Household Size and Housing Units.
"""
from dash import html, dcc
import plotly.graph_objects as go
from utils.data_loader import get_entity_by_code
from utils.geography import get_regions, get_provinces
from utils.formatting import format_number, format_compact, format_percentage

def render_population_bar_chart(selected_code="PH000000000"):
    """
    Render horizontal bar chart for regions or provinces.
    Clicking a bar fires clickData to update the dashboard and zoom the map!
    """
    curr = get_entity_by_code(selected_code)

    if curr["level"] == "Country":
        chart_title = "Population by Region"
        # Reference official breakdown: Top 9 + Others
        items = [
            {"name": "NCR", "pop": 13_876_293, "share": 12.7, "code": "PH130000000", "is_other": False},
            {"name": "Region IV-A", "pop": 12_112_972, "share": 11.1, "code": "PH040000000", "is_other": False},
            {"name": "Region III", "pop": 8_789_258, "share": 8.1, "code": "PH030000000", "is_other": False},
            {"name": "Region VII", "pop": 6_829_885, "share": 6.3, "code": "PH070000000", "is_other": False},
            {"name": "Region XI", "pop": 6_276_762, "share": 5.8, "code": "PH110000000", "is_other": False},
            {"name": "Region VI", "pop": 5_967_708, "share": 5.5, "code": "PH060000000", "is_other": False},
            {"name": "Region X", "pop": 5_840_052, "share": 5.4, "code": "PH100000000", "is_other": False},
            {"name": "Region XII", "pop": 5_518_624, "share": 5.1, "code": "PH120000000", "is_other": False},
            {"name": "Region VIII", "pop": 4_943_347, "share": 4.5, "code": "PH080000000", "is_other": False},
            {"name": "Others", "pop": 38_799_042, "share": 35.6, "code": "PH000000000", "is_other": True}
        ]
        display_items_rev = list(reversed(items))
        y_names = [e["name"] for e in display_items_rev]
        x_pops = [e["pop"] for e in display_items_rev]
        customdata = [e["code"] for e in display_items_rev]
        labels = [f"{format_number(e['pop'])} ({e['share']:.1f}%)" for e in display_items_rev]
        colors = ["#cbd5e1" if e["is_other"] else ("#0284c7" if e["code"] == selected_code else "#6ba4e8") for e in display_items_rev]
    else:
        reg_code = curr["code"] if curr["level"] == "Region" else curr.get("parent_code", "PH130000000")
        parent = get_entity_by_code(reg_code)
        entities = get_provinces(reg_code)
        chart_title = f"Population Distribution in {parent['name']}"
        sorted_items = sorted(entities, key=lambda x: x["total_pop"], reverse=True)[:10]
        display_items_rev = list(reversed(sorted_items))
        y_names = [e["short_name"] for e in display_items_rev]
        x_pops = [e["total_pop"] for e in display_items_rev]
        customdata = [e["code"] for e in display_items_rev]
        labels = [f"{format_number(e['total_pop'])} ({e['nat_share']:.1f}%)" for e in display_items_rev]
        colors = ["#ffb703" if e["code"] == selected_code else "#6ba4e8" for e in display_items_rev]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=y_names,
        x=x_pops,
        orientation='h',
        text=labels,
        textposition='outside',
        textfont=dict(size=9.5, color="#1e293b", family="Inter, sans-serif"),
        marker=dict(color=colors, line=dict(color="#ffffff", width=1)),
        customdata=customdata,
        hovertemplate="<b>%{y}</b><br>Population: %{x:,}<extra></extra>"
    ))

    max_x = max(x_pops) if x_pops else 1000000
    fig.update_layout(
        title=dict(
            text=f"<b>{chart_title}</b>",
            font=dict(size=12, color="#002d62", family="Outfit, sans-serif"),
            x=0.02
        ),
        margin=dict(l=10, r=105, t=32, b=15),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            range=[0, max_x * 1.55]
        ),
        yaxis=dict(
            autorange=True,
            showgrid=False,
            tickfont=dict(size=9.5, family="Inter, sans-serif")
        ),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=290,
        clickmode="event+select"
    )

    return dcc.Graph(
        id="population-bar-chart",
        figure=fig,
        config={"displayModeBar": False, "responsive": True}
    )

def render_top_areas_table(selected_code="PH000000000"):
    """Render top 5 areas by population in a clean styled table."""
    curr = get_entity_by_code(selected_code)
    if curr["level"] == "Country":
        table_title = "Top 5 Regions by Population"
        rows_data = [
            (1, "NCR", "13,876,293", "12.7%"),
            (2, "Region IV-A", "12,112,972", "11.1%"),
            (3, "Region III", "8,789,258", "8.1%"),
            (4, "Region VII", "6,829,885", "6.3%"),
            (5, "Region XI", "6,276,762", "5.8%")
        ]
        label_col = "Region"
    else:
        reg_code = curr["code"] if curr["level"] == "Region" else curr.get("parent_code", "PH130000000")
        peers = get_provinces(reg_code)
        table_title = f"Top Areas in {get_entity_by_code(reg_code)['name']}"
        sorted_peers = sorted(peers, key=lambda x: x["total_pop"], reverse=True)[:5]
        rows_data = [
            (rank, p["name"], format_number(p["total_pop"]), f"{p['nat_share']:.1f}%")
            for rank, p in enumerate(sorted_peers, 1)
        ]
        label_col = "Area Name"

    rows = []
    for rank, name, pop_str, share_str in rows_data:
        rows.append(html.Tr([
            html.Td(str(rank), style={"fontWeight": "600", "color": "#0284c7", "padding": "5px 8px"}),
            html.Td(name, style={"fontWeight": "500", "padding": "5px 8px"}),
            html.Td(pop_str, style={"textAlign": "right", "padding": "5px 8px"}),
            html.Td(share_str, style={"textAlign": "right", "fontWeight": "600", "padding": "5px 8px"})
        ], style={"borderBottom": "1px solid #f1f5f9"}))

    return html.Div([
        html.Div([
            html.Img(src="/assets/icons/chart.svg", alt="Chart", style={"width": "15px", "height": "15px", "marginRight": "6px"}),
            html.Span(table_title, style={"fontWeight": "700", "fontSize": "0.82rem", "color": "var(--psa-navy)"})
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Rank", style={"width": "15%", "padding": "4px 8px", "background": "#f8fafc", "color": "#475569", "fontSize": "0.74rem"}),
                html.Th(label_col, style={"width": "42%", "padding": "4px 8px", "background": "#f8fafc", "color": "#475569", "fontSize": "0.74rem"}),
                html.Th("Population", style={"textAlign": "right", "width": "28%", "padding": "4px 8px", "background": "#f8fafc", "color": "#475569", "fontSize": "0.74rem"}),
                html.Th("Share", style={"textAlign": "right", "width": "15%", "padding": "4px 8px", "background": "#f8fafc", "color": "#475569", "fontSize": "0.74rem"})
            ])),
            html.Tbody(rows)
        ], style={
            "width": "100%",
            "borderCollapse": "collapse",
            "fontSize": "0.76rem",
            "border": "1px solid var(--border-color)",
            "borderRadius": "6px",
            "overflow": "hidden"
        })
    ], className="ref-panel", style={"padding": "10px 12px", "marginBottom": "10px"})

def render_household_size_donut(selected_code="PH000000000"):
    """
    Render Household Size Distribution donut chart matching reference exactly.
    """
    curr = get_entity_by_code(selected_code)
    if curr["level"] == "Country":
        labels = ["1 person", "2 persons", "3 persons", "4 persons", "5+ persons"]
        values = [8.7, 18.4, 23.1, 24.8, 24.9]
        legend_labels = ["1 person    8.7%", "2 persons  18.4%", "3 persons  23.1%", "4 persons  24.8%", "5+ persons 24.9%"]
        center_num = "28.2M"
    else:
        hh_sizes = curr.get("household_sizes", {})
        labels = list(hh_sizes.keys())
        values = list(hh_sizes.values())
        tot_hh = sum(values) if values else 1
        legend_labels = [f"{l}  {v/tot_hh*100:.1f}%" for l, v in zip(labels, values)]
        center_num = format_compact(curr.get("total_households", 1))

    colors = ["#1e3a8a", "#38bdf8", "#059669", "#f59e0b", "#ea580c"]

    fig = go.Figure(data=[go.Pie(
        labels=legend_labels,
        values=values,
        hole=0.64,
        domain=dict(x=[0.0, 0.70]),
        marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
        textinfo='none',
        hovertemplate="<b>%{label}</b><extra></extra>",
        sort=False
    )])

    center_text = f"<b>{center_num}</b><br><span style='font-size:10px; color:#64748b;'>Households</span>"

    fig.update_layout(
        title=dict(
            text="<b>Household Size Distribution</b>",
            font=dict(size=12, color="#002d62", family="Outfit, sans-serif"),
            x=0.02
        ),
        annotations=[dict(text=center_text, x=0.25, y=0.5, font_size=12, showarrow=False)],
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=0.60,
            font=dict(size=9.5, family="Inter, sans-serif")
        ),
        margin=dict(l=5, r=10, t=30, b=5),
        height=185,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff"
    )

    return html.Div([
        dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True})
    ], className="ref-panel", style={"padding": "8px 12px", "marginBottom": "10px"})

def render_housing_types_donut(selected_code="PH000000000"):
    """
    Render Type of Housing Units donut chart matching reference exactly.
    """
    curr = get_entity_by_code(selected_code)
    if curr["level"] == "Country":
        labels = ["Single House", "Duplex", "Apartment/Accessoria", "Others"]
        values = [72.1, 6.9, 9.8, 11.2]
        legend_labels = ["Single House       72.1%", "Duplex               6.9%", "Apartment/Accessoria 9.8%", "Others              11.2%"]
        center_num = "27.3M"
    else:
        h_types = curr.get("housing_types", {})
        labels = list(h_types.keys())
        values = list(h_types.values())
        tot_units = sum(values) if values else 1
        legend_labels = [f"{l}  {v/tot_units*100:.1f}%" for l, v in zip(labels, values)]
        center_num = format_compact(curr.get("housing_units", 1))

    colors = ["#9333ea", "#38bdf8", "#f97316", "#10b981"]

    fig = go.Figure(data=[go.Pie(
        labels=legend_labels,
        values=values,
        hole=0.64,
        domain=dict(x=[0.0, 0.90]), 
        marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
        textinfo='none',
        hovertemplate="<b>%{label}</b><extra></extra>",
        sort=False
    )])

    center_text = f"<b>{center_num}</b><br><span style='font-size:10px; color:#64748b;'>Housing Units</span>"

    fig.update_layout(
        title=dict(
            text="<b>Type of Housing Units</b>",
            font=dict(size=12, color="#002d62", family="Outfit, sans-serif"),
            x=0.02
        ),
        annotations=[dict(text=center_text, x=0.32, y=0.5, font_size=12, showarrow=False)],
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=0.74,
            font=dict(size=9.5, family="Inter, sans-serif")
        ),
        margin=dict(l=5, r=10, t=30, b=5),
        height=185,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff"
    )

    return html.Div([
        dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True})
    ], className="ref-panel", style={"padding": "8px 12px", "marginBottom": "10px"})

def render_sex_distribution_chart(selected_code="PH000000000"):
    """Render 100% stacked horizontal bar comparing male vs female counts and shares."""
    entity = get_entity_by_code(selected_code)
    m = entity["male_pop"]
    f = entity["female_pop"]
    m_pct = entity["male_share"]
    f_pct = entity["female_share"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=["Sex"],
        x=[m],
        name=f"Male ({m_pct:.1f}%)",
        orientation='h',
        marker=dict(color="#0284c7"),
        text=f"Male: {format_compact(m)} ({m_pct:.1f}%)",
        textposition="inside",
        textfont=dict(color="#ffffff", size=12, family="Inter, sans-serif"),
        hovertemplate="<b>Male</b>: %{x:,} (" + f"{m_pct:.1f}%)<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        y=["Sex"],
        x=[f],
        name=f"Female ({f_pct:.1f}%)",
        orientation='h',
        marker=dict(color="#db2777"),
        text=f"Female: {format_compact(f)} ({f_pct:.1f}%)",
        textposition="inside",
        textfont=dict(color="#ffffff", size=12, family="Inter, sans-serif"),
        hovertemplate="<b>Female</b>: %{x:,} (" + f"{f_pct:.1f}%)<extra></extra>"
    ))

    fig.update_layout(
        barmode='stack',
        height=120,
        margin=dict(l=10, r=10, t=10, b=25),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showticklabels=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=11)),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff"
    )

    return html.Div([
        html.Div([
            html.Img(src="/assets/icons/users.svg", alt="Sex Distribution", style={"width": "16px", "height": "16px", "marginRight": "6px"}),
            html.Span("Population by Sex", style={"fontWeight": "700", "fontSize": "0.85rem", "color": "var(--psa-navy)"})
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "4px"}),
        dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True})
    ], className="panel-card", style={"padding": "12px 14px", "marginBottom": "0px"})
