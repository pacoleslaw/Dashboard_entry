"""
Chart Components for Population, Household, and Housing Analysis.
Provides horizontal bar charts, top 5 tables, sex distributions,
and donut charts for Household Size and Housing Units.
"""
import functools
from dash import html, dcc
import plotly.graph_objects as go
from utils.data_loader import get_entity_by_code
from utils.geography import get_regions, get_provinces
from utils.formatting import format_number, format_compact, format_percentage

def get_map_indicator_color(val, indicator="total_pop", is_other=False):
    """
    Get the exact color matching the map's choropleth legend brackets.
    Follows:
    - total_pop:
        > 5,000,000: #b91c1c (Deep Red)
        2,000,001 – 5,000,000: #f97316 (Vibrant Orange)
        1,000,001 – 2,000,000: #fe9929 (Warm Amber)
        500,000 – 1,000,000: #fec44f (Golden Yellow)
        < 500,000: #fee08b (Light Cream Yellow)
    - households:
        > 1,000,000: #0052a5
        500,001 – 1,000,000: #1976d2
        200,001 – 500,000: #42a5f5
        50,001 – 200,000: #90caf9
        ≤ 50,000: #e3f2fd
    - housing:
        > 1,000,000: #065f46
        500,001 – 1,000,000: #059669
        200,001 – 500,000: #10b981
        50,001 – 200,000: #34d399
        ≤ 50,000: #a7f3d0
    """
    if is_other:
        return "#cbd5e1"

    # Convert values in millions (e.g. 13.9) to absolute numbers
    num = val * 1_000_000 if (isinstance(val, (int, float)) and val < 1000) else val

    if indicator == "households":
        if num > 1_000_000:
            return "#0052a5"
        elif num > 500_000:
            return "#1976d2"
        elif num > 200_000:
            return "#42a5f5"
        elif num > 50_000:
            return "#90caf9"
        else:
            return "#e3f2fd"
    elif indicator in ("housing", "housing_units"):
        if num > 1_000_000:
            return "#065f46"
        elif num > 500_000:
            return "#059669"
        elif num > 200_000:
            return "#10b981"
        elif num > 50_000:
            return "#34d399"
        else:
            return "#a7f3d0"
    else:
        # Default: total_pop (Exact map choropleth tiers)
        if num > 5_000_000:
            return "#b91c1c"
        elif num > 2_000_000:
            return "#f97316"
        elif num > 1_000_000:
            return "#fe9929"
        elif num >= 500_000:
            return "#fec44f"
        else:
            return "#fee08b"


@functools.lru_cache(maxsize=64)
def render_population_bar_chart(selected_code="PH000000000", height=350, indicator="total_pop"):
    """
    Render horizontal bar chart for regions matching the reference image.
    Features:
    - Ranked regions with exact numbers: NCR (13.9M), Region IV-A (16.2M), Region III (12.1M), etc.
    - Bars colored dynamically according to the choropleth map brackets (>5M: #b91c1c, 2M-5M: #f97316, etc.)
    - Scrollable bar chart container for all regions
    """
    curr = get_entity_by_code(selected_code)

    if curr["level"] == "Country":
        chart_title = "Population by Region"
        chart_subtitle = "Total population (2020) • 17 Regions (Scroll to explore)"
        regions = get_regions()
        sorted_regions = sorted(regions, key=lambda x: x["total_pop"], reverse=True)
        items = [
            {
                "name": r["short_name"],
                "pop": r["total_pop"] / 1_000_000,
                "label": f"{r['total_pop'] / 1_000_000:.1f}M",
                "code": r["code"],
                "raw_pop": r["total_pop"]
            }
            for r in sorted_regions
        ]
        # In Plotly horizontal bar chart, bottom item in list is at bottom of chart, so reverse to have top rank at top
        display_items_rev = list(reversed(items))
        y_names = [e["name"] for e in display_items_rev]
        x_pops = [e["pop"] for e in display_items_rev]
        customdata = [e["code"] for e in display_items_rev]
        labels = [e["label"] for e in display_items_rev]
        colors = [get_map_indicator_color(e["raw_pop"], indicator=indicator) for e in display_items_rev]
        border_colors = ["#002b5c" if (e["code"] == selected_code and selected_code != "PH000000000") else "#ffffff" for e in display_items_rev]
        border_widths = [2.5 if (e["code"] == selected_code and selected_code != "PH000000000") else 1.0 for e in display_items_rev]
        max_val = max(x_pops) * 1.25 if x_pops else 20
        plot_height = len(items) * 26 + 24
    else:
        reg_code = curr["code"] if curr["level"] == "Region" else curr.get("parent_code", "PH130000000")
        parent = get_entity_by_code(reg_code)
        entities = get_provinces(reg_code)
        chart_title = f"Population Distribution in {parent.get('short_name', parent['name'])}"
        chart_subtitle = f"Total population (2020) • {len(entities)} Areas"
        sorted_items = sorted(entities, key=lambda x: x["total_pop"], reverse=True)
        display_items_rev = list(reversed(sorted_items))
        y_names = [e["short_name"] for e in display_items_rev]
        x_pops = [e["total_pop"] / 1_000_000 for e in display_items_rev]
        customdata = [e["code"] for e in display_items_rev]
        labels = [format_compact(e["total_pop"]) for e in display_items_rev]
        colors = [get_map_indicator_color(e["total_pop"], indicator=indicator) for e in display_items_rev]
        border_colors = ["#002b5c" if e["code"] == selected_code else "#ffffff" for e in display_items_rev]
        border_widths = [2.5 if e["code"] == selected_code else 1.0 for e in display_items_rev]
        max_val = max(x_pops) * 1.25 if x_pops else 10
        plot_height = max(height, len(display_items_rev) * 26 + 24)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=y_names,
        x=x_pops,
        orientation='h',
        text=labels,
        textposition='outside',
        textfont=dict(size=9.5, color="#334155", family="Inter, sans-serif"),
        marker=dict(color=colors, line=dict(color=border_colors, width=border_widths)),
        customdata=customdata,
        hovertemplate="<b>%{y}</b>: %{text}<extra></extra>",
        cliponaxis=False
    ))

    fig.update_layout(
        margin=dict(l=76, r=42, t=8, b=8),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, max_val]
        ),
        yaxis=dict(
            autorange=True,
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=9.5, family="Inter, sans-serif", color="#334155")
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=plot_height,
        clickmode="event+select"
    )

    return html.Div([
        # Chart Header
        html.Div([
            html.Div(chart_title, style={"fontSize": "0.98rem", "fontWeight": "700", "color": "#0f172a"}),
            html.Div(chart_subtitle, style={"fontSize": "0.78rem", "color": "#64748b", "marginTop": "2px"}),
        ], style={"marginBottom": "6px"}),

        # Scrollable Bar Graph Container
        html.Div([
            dcc.Graph(
                id={"type": "population-bar-chart", "id": "main"},
                figure=fig,
                config={"displayModeBar": False, "responsive": True, "scrollZoom": False},
                style={"height": f"{plot_height}px", "width": "100%"}
            )
        ], className="ref-chart-scroll-box", style={
            "maxHeight": f"{height}px",
            "overflowY": "auto",
            "overflowX": "hidden",
            "paddingRight": "2px"
        })
    ], className="ref-overview-chart-container")

@functools.lru_cache(maxsize=64)
def render_top_areas_table(selected_code="PH000000000", indicator="total_pop"):
    """Render top 5 areas by population in a clean styled table with map-coordinated color dots."""
    curr = get_entity_by_code(selected_code)
    if curr["level"] == "Country":
        table_title = "Top 5 Regions by Population"
        regions = get_regions()
        sorted_regions = sorted(regions, key=lambda x: x["total_pop"], reverse=True)[:5]
        rows_data = [
            (rank, r["short_name"], format_number(r["total_pop"]), f"{r['nat_share']:.1f}%", r["total_pop"])
            for rank, r in enumerate(sorted_regions, 1)
        ]
        label_col = "Region"
    else:
        reg_code = curr["code"] if curr["level"] == "Region" else curr.get("parent_code", "PH130000000")
        peers = get_provinces(reg_code)
        table_title = f"Top Areas in {get_entity_by_code(reg_code)['name']}"
        sorted_peers = sorted(peers, key=lambda x: x["total_pop"], reverse=True)[:5]
        rows_data = [
            (rank, p["name"], format_number(p["total_pop"]), f"{p['nat_share']:.1f}%", p["total_pop"])
            for rank, p in enumerate(sorted_peers, 1)
        ]
        label_col = "Area Name"

    rows = []
    for rank, name, pop_str, share_str, raw_pop in rows_data:
        b_color = get_map_indicator_color(raw_pop, indicator=indicator)
        rows.append(html.Tr([
            html.Td([
                html.Span(style={
                    "display": "inline-block",
                    "width": "8px",
                    "height": "8px",
                    "borderRadius": "50%",
                    "backgroundColor": b_color,
                    "marginRight": "6px",
                    "verticalAlign": "middle"
                }),
                html.Span(str(rank), style={"fontWeight": "700", "color": "#1e293b", "verticalAlign": "middle"})
            ], style={"padding": "5px 8px", "whiteSpace": "nowrap"}),
            html.Td(name, style={"fontWeight": "500", "padding": "5px 8px"}),
            html.Td(pop_str, style={"textAlign": "right", "padding": "5px 8px"}),
            html.Td(share_str, style={"textAlign": "right", "fontWeight": "600", "color": b_color, "padding": "5px 8px"})
        ], style={"borderBottom": "1px solid #f1f5f9"}))

    return html.Div([
        html.Div([
            html.Img(src="/assets/icons/chart.svg", alt="Chart", style={"width": "15px", "height": "15px", "marginRight": "6px"}),
            html.Span(table_title, style={"fontWeight": "700", "fontSize": "0.82rem", "color": "var(--psa-navy)"})
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "6px"}),
        html.Div([
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Rank", style={"width": "15%", "minWidth": "36px", "padding": "4px 8px", "background": "#f8fafc", "color": "#475569", "fontSize": "0.74rem"}),
                    html.Th(label_col, style={"width": "42%", "minWidth": "100px", "padding": "4px 8px", "background": "#f8fafc", "color": "#475569", "fontSize": "0.74rem"}),
                    html.Th("Population", style={"textAlign": "right", "width": "28%", "minWidth": "80px", "padding": "4px 8px", "background": "#f8fafc", "color": "#475569", "fontSize": "0.74rem"}),
                    html.Th("Share", style={"textAlign": "right", "width": "15%", "minWidth": "50px", "padding": "4px 8px", "background": "#f8fafc", "color": "#475569", "fontSize": "0.74rem"})
                ])),
                html.Tbody(rows)
            ], style={
                "width": "100%",
                "borderCollapse": "collapse",
                "fontSize": "0.76rem",
                "border": "1px solid var(--border-color)",
                "borderRadius": "6px"
            })
        ], className="ref-table-responsive", style={"overflowX": "auto", "width": "100%"})
    ], className="ref-panel pop-panel-table", style={"padding": "10px 12px", "marginBottom": "10px"})

@functools.lru_cache(maxsize=64)
def render_household_size_donut(selected_code="PH000000000"):
    """
    Render Household Size Distribution donut chart matching reference exactly.
    """
    curr = get_entity_by_code(selected_code)
    if curr["level"] == "Country":
        labels = ["1 person", "2 persons", "3 persons", "4 persons", "5+ persons"]
        values = [8.7, 18.4, 23.1, 24.8, 24.9]
        legend_labels = ["1 person    8.7%", "2 persons  18.4%", "3 persons  23.1%", "4 persons  24.8%", "5+ persons 24.9%"]
        center_num = "26.4M"
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
        domain=dict(x=[0.05, 0.95]),
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
        annotations=[dict(text=center_text, x=0.5, y=0.5, font_size=11, showarrow=False)],
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.08,
            xanchor="center",
            x=0.5,
            font=dict(size=9.5, family="Inter, sans-serif")
        ),
        margin=dict(l=5, r=5, t=30, b=10),
        height=250,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff"
    )

    return html.Div([
        dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True})
    ], className="ref-panel", style={"padding": "8px 12px", "marginBottom": "10px"})

@functools.lru_cache(maxsize=64)
def render_households_by_region_bar(selected_code="PH000000000"):
    """
    Render horizontal ranked bar chart of total_households by region or province.
    Clicking a bar fires clickData to update the shared state (same pattern as population bar).
    """
    curr = get_entity_by_code(selected_code)

    if curr["level"] == "Country":
        chart_title = "Households by Region"
        items = get_regions()
        sorted_items = sorted(items, key=lambda x: x.get("total_households", 0), reverse=True)
        display = list(reversed(sorted_items))
        y_names = [(n["short_name"][:18] + "…") if len(n["short_name"]) > 20 else n["short_name"] for n in display]
        x_vals = [n.get("total_households", 0) for n in display]
        customdata = [n["code"] for n in display]
        nat_total = get_entity_by_code("PH000000000").get("total_households", 1) or 1
        labels = [f"{format_compact(n.get('total_households', 0))} ({n.get('total_households', 0)/nat_total*100:.1f}%)" for n in display]
        colors = [
            get_map_indicator_color(n.get("total_households", 0), indicator="households")
            for n in display
        ]
        border_colors = ["#002b5c" if (n["code"] == selected_code and selected_code != "PH000000000") else "#ffffff" for n in display]
        border_widths = [2.5 if (n["code"] == selected_code and selected_code != "PH000000000") else 1.0 for n in display]
        plot_height = len(sorted_items) * 26 + 24
    else:
        reg_code = curr["code"] if curr["level"] == "Region" else curr.get("parent_code", "PH130000000")
        parent = get_entity_by_code(reg_code)
        peers = get_provinces(reg_code)
        chart_title = f"Households in {parent['short_name']}"
        sorted_items = sorted(peers, key=lambda x: x.get("total_households", 0), reverse=True)
        display = list(reversed(sorted_items))
        y_names = [(n["short_name"][:18] + "…") if len(n["short_name"]) > 20 else n["short_name"] for n in display]
        x_vals = [n.get("total_households", 0) for n in display]
        customdata = [n["code"] for n in display]
        reg_total = parent.get("total_households", 1) or 1
        labels = [f"{format_compact(n.get('total_households', 0))} ({n.get('total_households', 0)/reg_total*100:.1f}%)" for n in display]
        colors = [
            get_map_indicator_color(n.get("total_households", 0), indicator="households")
            for n in display
        ]
        border_colors = ["#002b5c" if n["code"] == selected_code else "#ffffff" for n in display]
        border_widths = [2.5 if n["code"] == selected_code else 1.0 for n in display]
        plot_height = max(310, len(sorted_items) * 26 + 24)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=y_names,
        x=x_vals,
        orientation='h',
        text=labels,
        textposition='outside',
        textfont=dict(size=9.5, color="#1e293b", family="Inter, sans-serif"),
        marker=dict(color=colors, line=dict(color=border_colors, width=border_widths)),
        customdata=customdata,
        hovertemplate="<b>%{y}</b><br>Households: %{x:,}<extra></extra>",
        cliponaxis=False
    ))

    max_x = max(x_vals) if x_vals else 1
    fig.update_layout(
        title=dict(
            text=f"<b>{chart_title}</b>",
            font=dict(size=12, color="#002d62", family="Outfit, sans-serif"),
            x=0.02
        ),
        margin=dict(l=10, r=65, t=32, b=15),
        xaxis=dict(showgrid=False, showticklabels=False, range=[0, max_x * 1.35]),
        yaxis=dict(autorange=True, showgrid=False, tickfont=dict(size=9.5, family="Inter, sans-serif")),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=plot_height,
        clickmode="event+select"
    )

    return html.Div([
        dcc.Graph(
            id={"type": "households-bar-chart", "id": "main"},
            figure=fig,
            config={"displayModeBar": False, "responsive": True, "scrollZoom": False},
            style={"height": f"{plot_height}px", "width": "100%"}
        )
    ], className="ref-chart-scroll-box", style={"maxHeight": "310px", "overflowY": "auto", "overflowX": "hidden"})

@functools.lru_cache(maxsize=64)
def render_housing_units_by_region_bar(selected_code="PH000000000"):
    """
    Render horizontal ranked bar chart of housing_units by region or province.
    Clicking a bar fires clickData to update the shared state (MAP & DASHBOARD).
    """
    curr = get_entity_by_code(selected_code)

    if curr["level"] == "Country":
        chart_title = "Housing Units by Region"
        items = get_regions()
        sorted_items = sorted(items, key=lambda x: x.get("housing_units", 0), reverse=True)
        display = list(reversed(sorted_items))
        y_names = [n["short_name"] for n in display]
        x_vals = [n.get("housing_units", 0) for n in display]
        customdata = [n["code"] for n in display]
        nat_total = get_entity_by_code("PH000000000").get("housing_units", 1) or 1
        labels = [f"{format_compact(n.get('housing_units', 0))} ({n.get('housing_units', 0)/nat_total*100:.1f}%)" for n in display]
        colors = [
            get_map_indicator_color(n.get("housing_units", 0), indicator="housing")
            for n in display
        ]
        border_colors = ["#002b5c" if (n["code"] == selected_code and selected_code != "PH000000000") else "#ffffff" for n in display]
        border_widths = [2.5 if (n["code"] == selected_code and selected_code != "PH000000000") else 1.0 for n in display]
        plot_height = len(sorted_items) * 26 + 24
    else:
        reg_code = curr["code"] if curr["level"] == "Region" else curr.get("parent_code", "PH130000000")
        parent = get_entity_by_code(reg_code)
        peers = get_provinces(reg_code)
        chart_title = f"Housing Units in {parent['short_name']}"
        sorted_items = sorted(peers, key=lambda x: x.get("housing_units", 0), reverse=True)
        display = list(reversed(sorted_items))
        y_names = [(n["short_name"][:18] + "…") if len(n["short_name"]) > 20 else n["short_name"] for n in display]
        x_vals = [n.get("housing_units", 0) for n in display]
        customdata = [n["code"] for n in display]
        reg_total = parent.get("housing_units", 1) or 1
        labels = [f"{format_compact(n.get('housing_units', 0))} ({n.get('housing_units', 0)/reg_total*100:.1f}%)" for n in display]
        colors = [
            get_map_indicator_color(n.get("housing_units", 0), indicator="housing")
            for n in display
        ]
        border_colors = ["#002b5c" if n["code"] == selected_code else "#ffffff" for n in display]
        border_widths = [2.5 if n["code"] == selected_code else 1.0 for n in display]
        plot_height = max(310, len(sorted_items) * 26 + 24)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=y_names,
        x=x_vals,
        orientation='h',
        text=labels,
        textposition='outside',
        textfont=dict(size=9.5, color="#1e293b", family="Inter, sans-serif"),
        cliponaxis=False,
        marker=dict(
            color=colors,
            line=dict(color=border_colors, width=border_widths)
        ),
        customdata=customdata,
        hovertemplate="<b>%{y}</b><br>Housing Units: %{x:,}<extra></extra>"
    ))

    max_x = max(x_vals) if x_vals else 1
    fig.update_layout(
        title=dict(
            text=f"<b>{chart_title}</b>",
            font=dict(size=12, color="#002d62", family="Outfit, sans-serif"),
            x=0.02
        ),
        margin=dict(l=10, r=65, t=32, b=15),
        xaxis=dict(showgrid=False, showticklabels=False, range=[0, max_x * 1.35]),
        yaxis=dict(autorange=True, showgrid=False, tickfont=dict(size=9.5, family="Inter, sans-serif")),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=plot_height,
        clickmode="event+select"
    )

    return html.Div([
        dcc.Graph(
            id={"type": "housing-bar-chart", "id": "main"},
            figure=fig,
            config={"displayModeBar": False, "responsive": True, "scrollZoom": False},
            style={"height": f"{plot_height}px", "width": "100%"}
        )
    ], className="ref-chart-scroll-box", style={"maxHeight": "310px", "overflowY": "auto", "overflowX": "hidden"})

@functools.lru_cache(maxsize=64)
def render_housing_types_donut(selected_code="PH000000000"):
    """
    Render Type of Housing Unit donut chart matching reference exactly.
    """
    curr = get_entity_by_code(selected_code)
    if curr["level"] == "Country":
        labels = ["Single House", "Duplex", "Apartment/Accessoria", "Others"]
        values = [72.1, 6.9, 9.8, 11.2]
        legend_labels = ["Single House (72.1%)", "Duplex (6.9%)", "Apartment (9.8%)", "Others (11.2%)"]
        center_num = "31.8M"
    else:
        h_types = curr.get("housing_types", {})
        labels = list(h_types.keys())
        values = list(h_types.values())
        tot_units = sum(values) if values else 1
        legend_labels = [f"{l} ({v/tot_units*100:.1f}%)" for l, v in zip(labels, values)]
        center_num = format_compact(curr.get("housing_units", 1))

    colors = ["#0284c7", "#06b6d4", "#f43f5e", "#d97706"]

    fig = go.Figure(data=[go.Pie(
        labels=legend_labels,
        values=values,
        hole=0.64,
        domain=dict(x=[0.05, 0.95]), 
        marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
        textinfo='none',
        hovertemplate="<b>%{label}</b><extra></extra>",
        sort=False
    )])

    center_text = f"<b>{center_num}</b><br><span style='font-size:10px; color:#64748b;'>Housing Units</span>"

    fig.update_layout(
        title=dict(
            text="<b>Type of Housing Unit</b>",
            font=dict(size=12, color="#002d62", family="Outfit, sans-serif"),
            x=0.02
        ),
        annotations=[dict(text=center_text, x=0.5, y=0.5, font_size=11, showarrow=False)],
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.08,
            xanchor="center",
            x=0.5,
            font=dict(size=9.5, family="Inter, sans-serif")
        ),
        margin=dict(l=5, r=5, t=30, b=10),
        height=250,
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
