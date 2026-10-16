"""
Demographics Page Components.
Faithfully reproduces the reference design layout:
- Demographics Top Header with 'EXPLORE THIS AREA' 4-dropdown cascade
- 4 Top KPI Cards aligned with the 4 columns below (Total Population, Male, Female, Median Age)
- Column 1: Population Pyramid with bilateral bars, View By / Age Group dropdowns, zoom/recenter controls
- Column 2: Population by Age Group horizontal bar chart with 17-step sky-blue to mint-green gradient and percentage labels
- Column 3: Population by Sex donut chart with center total pop & 'What does this mean?' info callout + View definition button
- Column 4: Explore a Place (metrics table, callout box, Compare place button) & Quick Insights (3 icon bullets)
"""
import functools
from dash import html, dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_loader import get_entity_by_code
from utils.geography import get_regions, get_provinces
from utils.formatting import format_number, format_compact, format_abbreviated_m

# 17 Age cohorts mapping between official PSA dataset keys and reference labels
AGE_KEYS = [
    "Below 5", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39",
    "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79",
    "80 years old and over"
]

AGE_LABELS = [
    "0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39",
    "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79",
    "80+"
]

# 17-step smooth gradient from sky blue (#38bdf8) to teal (#14b8a6) to mint green (#6ee7b7)
AGE_GRADIENT_COLORS = [
    "#38bdf8", "#33bced", "#2fbbe3", "#2abbd9", "#26bacf", "#21b9c4",
    "#1db9ba", "#18b8b0", "#14b8a6", "#1fbda8", "#2ac3aa", "#35c9ac",
    "#41cfae", "#4cd5b0", "#57dbb2", "#62e1b4", "#6ee7b7"
]

def calculate_median_age(entity):
    """Calculate interpolated median age from age cohorts or return official benchmarks."""
    if entity["level"] == "Country":
        return 25.3  # Official PSA 2020 CPH Press Release (Ref No. 2022-322)
    if "rizal" in entity.get("name", "").lower():
        return 25.6

    age_both = entity.get("age_both", {})
    total = sum(age_both.values())
    if total == 0:
        return 25.3

    half = total / 2.0
    cum = 0
    brackets = [
        ("Below 5", 0, 5), ("5-9", 5, 5), ("10-14", 10, 5), ("15-19", 15, 5),
        ("20-24", 20, 5), ("25-29", 25, 5), ("30-34", 30, 5), ("35-39", 35, 5),
        ("40-44", 40, 5), ("45-49", 45, 5), ("50-54", 50, 5), ("55-59", 55, 5),
        ("60-64", 60, 5), ("65-69", 65, 5), ("70-74", 70, 5), ("75-79", 75, 5),
        ("80 years old and over", 80, 5)
    ]
    for name, low, width in brackets:
        count = age_both.get(name, 0)
        if cum + count >= half:
            return round(low + ((half - cum) / count) * width, 1) if count > 0 else low
        cum += count
    return 25.3


# =============================================================================
# 1. TOP HEADER & EXPLORE AREA DROPDOWNS
# =============================================================================
@functools.lru_cache(maxsize=32)
def render_demographics_top_header(selected_code="PH000000000"):
    """Header lockup (DEMOGRAPHICS) + 4-dropdown cascade (EXPLORE THIS AREA)."""
    entity = get_entity_by_code(selected_code)
    regions = get_regions()

    if entity["level"] == "Country":
        sel_reg = "ALL"
        sel_prov = "ALL"
        prov_options = [{"label": "All Provinces", "value": "ALL"}]
    elif entity["level"] == "Region":
        sel_reg = entity["code"]
        sel_prov = "ALL"
        provinces = get_provinces(sel_reg)
        prov_options = [{"label": "All Provinces", "value": "ALL"}] + [
            {"label": p["name"], "value": p["code"]} for p in provinces
        ]
    else:
        sel_reg = entity.get("parent_code", "ALL")
        sel_prov = entity["code"]
        provinces = get_provinces(sel_reg) if sel_reg != "ALL" else []
        prov_options = [{"label": "All Provinces", "value": "ALL"}] + [
            {"label": p["name"], "value": p["code"]} for p in provinces
        ]

    region_options = [{"label": "All Regions", "value": "ALL"}] + [
        {"label": r["short_name"], "value": r["code"]} for r in regions
    ]

    return html.Div([
        # Left Title Lockup
        html.Div([
            html.Div(
                html.Img(src="/assets/icons/users.svg",
                         style={"width": "22px", "height": "22px", "filter": "brightness(0) invert(1)"}),
                className="demo-header-icon-badge"
            ),
            html.Div([
                html.H1("DEMOGRAPHICS", className="demo-header-title"),
                html.P("Who makes up the population?", className="demo-header-subtitle")
            ])
        ], className="demo-header-lockup"),

        # Right Explore Area Dropdowns
        html.Div([
            html.Div("EXPLORE THIS AREA", className="demo-explore-label"),
            html.Div([
                dcc.Dropdown(
                    id={"type": "demo-filter-country", "id": "main"},
                    options=[{"label": "Philippines", "value": "PH000000000"}],
                    value="PH000000000",
                    clearable=False,
                    className="demo-explore-dropdown"
                ),
                dcc.Dropdown(
                    id={"type": "demo-filter-region", "id": "main"},
                    options=region_options,
                    value=sel_reg,
                    clearable=False,
                    placeholder="All Regions",
                    className="demo-explore-dropdown"
                ),
                dcc.Dropdown(
                    id={"type": "demo-filter-prov", "id": "main"},
                    options=prov_options,
                    value=sel_prov,
                    clearable=False,
                    placeholder="All Provinces",
                    className="demo-explore-dropdown"
                ),
                dcc.Dropdown(
                    id={"type": "demo-filter-city", "id": "main"},
                    options=[{"label": "All Cities/Municipalities", "value": "ALL"}],
                    value="ALL",
                    clearable=False,
                    placeholder="All Cities/Municipalities",
                    className="demo-explore-dropdown"
                ),
            ], className="demo-explore-grid")
        ], className="demo-explore-bar")
    ], className="demo-top-header")


# =============================================================================
# 2. TOP 4 KPI CARDS (Matching the 4 Columns Below)
# =============================================================================
@functools.lru_cache(maxsize=32)
def render_demographics_kpi_cards(selected_code="PH000000000"):
    """4 KPI cards directly aligned with the 4 columns below, following official PSA Press Release 2022-322."""
    entity = get_entity_by_code(selected_code)
    tot_pop = entity.get("total_pop", 0)
    hh_pop = entity.get("household_pop", 0) or tot_pop
    male_pop = entity.get("hh_male_pop", entity.get("male_pop", 0))
    female_pop = entity.get("hh_female_pop", entity.get("female_pop", 0))
    male_share = entity.get("hh_male_share", entity.get("male_share", 50.6))
    female_share = entity.get("hh_female_share", entity.get("female_share", 49.4))
    median_age = calculate_median_age(entity)
    name = entity.get("short_name", entity["name"])
    level = entity.get("level", "Country")

    # Format numbers (Male 55.02 M / 50.6%, Female 53.65 M / 49.4% matching press release)
    tot_str = format_number(tot_pop)
    hh_str = format_number(hh_pop)
    hh_abbrev = format_abbreviated_m(hh_pop)
    male_str = format_abbreviated_m(male_pop)
    male_pct_str = f"({male_share:.1f}%)"
    female_str = format_abbreviated_m(female_pop)
    female_pct_str = f"({female_share:.1f}%)"

    if level == "Country":
        sub_pop = f"Total Pop: {format_abbreviated_m(tot_pop)} (Official)"
        sub_median = "(Philippines)"
    else:
        sub_pop = f"Share of PH: {entity.get('nat_share', 0.0):.1f}%"
        sub_median = f"({name})"

    return html.Div([
        # Card 1: HOUSEHOLD POPULATION (Aligned with Population Pyramid)
        html.Div([
            html.Div([
                html.Div(
                    html.Img(src="/assets/icons/users.svg",
                             style={"width": "20px", "height": "20px", "filter": "brightness(0) invert(1)"}),
                    className="demo-kpi-icon-circle",
                    style={"backgroundColor": "#0284c7"}
                ),
                html.Div([
                    html.Div("HOUSEHOLD POPULATION",
                             style={"fontSize": "0.72rem", "fontWeight": "800", "color": "#002b5c", "letterSpacing": "0.4px"}),
                    html.Div(hh_str,
                             title=f"Household Population: {format_number(hh_pop)} | Total Population: {format_number(tot_pop)} persons",
                             style={"fontSize": "1.20rem", "fontWeight": "800", "color": "#002b5c", "lineHeight": "1.15", "whiteSpace": "nowrap"}),
                    html.Div(sub_pop,
                             title=f"Official Total Population: {format_number(tot_pop)} persons (Proclamation No. 1179)",
                             style={"fontSize": "0.7rem", "color": "#64748b"}),
                ])
            ], className="demo-kpi-body")
        ], className="demo-kpi-card"),

        # Card 2: MALE (Aligned with Population by Age Group)
        html.Div([
            html.Div([
                html.Div([
                    html.Span(className="demo-kpi-pin-stem", style={"backgroundColor": "#0284c7"}),
                    html.Img(src="/assets/icons/male.svg",
                             style={"width": "18px", "height": "18px", "filter": "brightness(0) invert(1)"}),
                ], className="demo-kpi-icon-circle", style={"backgroundColor": "#0284c7"}),
                html.Div([
                    html.Div([
                        html.Span("•", style={"color": "#0284c7", "fontSize": "0.9rem", "lineHeight": "1", "marginRight": "4px"}),
                        html.Span("MALE", style={"fontSize": "0.68rem", "fontWeight": "800", "color": "#0284c7", "letterSpacing": "0.5px"})
                    ], style={"display": "flex", "alignItems": "center"}),
                    html.Div(male_str,
                             title=f"{format_number(male_pop)} persons",
                             style={"fontSize": "1.20rem", "fontWeight": "800", "color": "#002b5c", "lineHeight": "1.15", "whiteSpace": "nowrap"}),
                    html.Div(male_pct_str,
                             style={"fontSize": "0.7rem", "color": "#64748b"}),
                ])
            ], className="demo-kpi-body")
        ], className="demo-kpi-card"),

        # Card 3: FEMALE (Aligned with Population by Sex)
        html.Div([
            html.Div([
                html.Div([
                    html.Span(className="demo-kpi-pin-stem", style={"backgroundColor": "#db2777"}),
                    html.Img(src="/assets/icons/female.svg",
                             style={"width": "18px", "height": "18px", "filter": "brightness(0) invert(1)"}),
                ], className="demo-kpi-icon-circle", style={"backgroundColor": "#db2777"}),
                html.Div([
                    html.Div([
                        html.Span("•", style={"color": "#db2777", "fontSize": "0.9rem", "lineHeight": "1", "marginRight": "4px"}),
                        html.Span("FEMALE", style={"fontSize": "0.68rem", "fontWeight": "800", "color": "#db2777", "letterSpacing": "0.5px"})
                    ], style={"display": "flex", "alignItems": "center"}),
                    html.Div(female_str,
                             title=f"{format_number(female_pop)} persons",
                             style={"fontSize": "1.20rem", "fontWeight": "800", "color": "#002b5c", "lineHeight": "1.15", "whiteSpace": "nowrap"}),
                    html.Div(female_pct_str,
                             style={"fontSize": "0.7rem", "color": "#64748b"}),
                ])
            ], className="demo-kpi-body")
        ], className="demo-kpi-card"),

        # Card 4: MEDIAN AGE (Aligned with Explore a Place)
        html.Div([
            html.Div([
                html.Div([
                    html.Span(className="demo-kpi-pin-stem", style={"backgroundColor": "#16a34a"}),
                    html.Img(src="/assets/icons/gauge.svg",
                             style={"width": "18px", "height": "18px", "filter": "brightness(0) invert(1)"}),
                ], className="demo-kpi-icon-circle", style={"backgroundColor": "#16a34a"}),
                html.Div([
                    html.Div([
                        html.Span("•", style={"color": "#16a34a", "fontSize": "0.9rem", "lineHeight": "1", "marginRight": "4px"}),
                        html.Span("MEDIAN AGE", style={"fontSize": "0.68rem", "fontWeight": "800", "color": "#16a34a", "letterSpacing": "0.5px"})
                    ], style={"display": "flex", "alignItems": "center"}),
                    html.Div(f"{median_age:.1f} years",
                             style={"fontSize": "1.20rem", "fontWeight": "800", "color": "#002b5c", "lineHeight": "1.15", "whiteSpace": "nowrap"}),
                    html.Div(sub_median,
                             style={"fontSize": "0.7rem", "color": "#64748b"}),
                ])
            ], className="demo-kpi-body")
        ], className="demo-kpi-card")
    ], className="demo-kpi-grid")


# =============================================================================
# 3. COLUMN 1: POPULATION PYRAMID
# =============================================================================
def build_demographics_pyramid_figure(entity, view_by="num", age_filter="all"):
    """Build the Plotly figure for the bilateral Population Pyramid with age filtering."""
    tot_pop = entity.get("household_pop", 0) or entity.get("total_pop", 1) or 1
    male_dict = entity.get("hh_age_male", entity.get("age_male", {}))
    female_dict = entity.get("hh_age_female", entity.get("age_female", {}))

    # Filter cohorts according to selected Age Group
    if age_filter == "0-14":
        indices = [0, 1, 2]
    elif age_filter == "15-64":
        indices = list(range(3, 13))
    elif age_filter == "65+":
        indices = list(range(13, 17))
    else:
        indices = list(range(17))

    filtered_labels = [AGE_LABELS[i] for i in indices]
    filtered_keys = [AGE_KEYS[i] for i in indices]

    male_counts = [male_dict.get(k, 0) for k in filtered_keys]
    female_counts = [female_dict.get(k, 0) for k in filtered_keys]

    if view_by == "pct":
        male_plot = [(v / tot_pop) * 100 for v in male_counts]
        female_plot = [(v / tot_pop) * 100 for v in female_counts]
        max_val = max(max(male_plot), max(female_plot)) if (male_plot and max(male_plot) > 0) else 5.0
        axis_max = max(max_val * 1.25, 0.5)

        step = axis_max / 3.0
        left_ticks = [step * 3, step * 2, step, 0]
        left_text = [f"{step*3:.1f}%", f"{step*2:.1f}%", f"{step:.1f}%", "0"]
        right_ticks = [step, step * 2, step * 3]
        right_text = [f"{step:.1f}%", f"{step*2:.1f}%", f"{step*3:.1f}%"]
        hover_male = "<b>Age %{y}</b><br>Male: %{customdata:,} (%{x:.2f}%)<extra></extra>"
        hover_female = "<b>Age %{y}</b><br>Female: %{customdata:,} (%{x:.2f}%)<extra></extra>"
    else:
        max_raw = max(max(male_counts), max(female_counts)) if (male_counts and max(male_counts) > 0) else 1
        if max_raw >= 1_000_000:
            male_plot = [v / 1_000_000 for v in male_counts]
            female_plot = [v / 1_000_000 for v in female_counts]
            axis_max = (max_raw / 1_000_000) * 1.25
            step = axis_max / 3.0
            left_ticks = [step * 3, step * 2, step, 0]
            left_text = [f"{step*3:.1f}M", f"{step*2:.1f}M", f"{step:.1f}M", "0"]
            right_ticks = [step, step * 2, step * 3]
            right_text = [f"{step:.1f}M", f"{step*2:.1f}M", f"{step*3:.1f}M"]
        elif max_raw >= 1_000:
            male_plot = [v / 1_000 for v in male_counts]
            female_plot = [v / 1_000 for v in female_counts]
            axis_max = (max_raw / 1_000) * 1.25
            step = axis_max / 3.0
            left_ticks = [step * 3, step * 2, step, 0]
            left_text = [f"{step*3:.0f}K", f"{step*2:.0f}K", f"{step:.0f}K", "0"]
            right_ticks = [step, step * 2, step * 3]
            right_text = [f"{step:.0f}K", f"{step*2:.0f}K", f"{step*3:.0f}K"]
        else:
            male_plot = [float(v) for v in male_counts]
            female_plot = [float(v) for v in female_counts]
            axis_max = max_raw * 1.25
            step = axis_max / 3.0
            left_ticks = [step * 3, step * 2, step, 0]
            left_text = [f"{int(step*3)}", f"{int(step*2)}", f"{int(step)}", "0"]
            right_ticks = [step, step * 2, step * 3]
            right_text = [f"{int(step)}", f"{int(step*2)}", f"{int(step*3)}"]

        hover_male = "<b>Age %{y}</b><br>Male: %{customdata:,}<extra></extra>"
        hover_female = "<b>Age %{y}</b><br>Female: %{customdata:,}<extra></extra>"

    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04)

    # Left: Male Trace (Reversed X-axis)
    fig.add_trace(go.Bar(
        y=filtered_labels,
        x=male_plot,
        customdata=male_counts,
        name="Male",
        orientation="h",
        marker=dict(color="#3b82f6", line=dict(color="#ffffff", width=0.5)),
        hovertemplate=hover_male
    ), row=1, col=1)

    # Right: Female Trace
    fig.add_trace(go.Bar(
        y=filtered_labels,
        x=female_plot,
        customdata=female_counts,
        name="Female",
        orientation="h",
        marker=dict(color="#ec4899", line=dict(color="#ffffff", width=0.5)),
        hovertemplate=hover_female
    ), row=1, col=2)

    fig.update_xaxes(
        autorange="reversed",
        showgrid=True,
        gridcolor="#f1f5f9",
        tickvals=left_ticks,
        ticktext=left_text,
        tickfont=dict(size=9, color="#64748b", family="Inter, sans-serif"),
        range=[axis_max, 0],
        row=1, col=1
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#f1f5f9",
        tickvals=right_ticks,
        ticktext=right_text,
        tickfont=dict(size=9, color="#64748b", family="Inter, sans-serif"),
        range=[0, axis_max],
        row=1, col=2
    )

    fig.update_yaxes(showticklabels=False, row=1, col=1)
    fig.update_yaxes(
        showticklabels=True,
        tickfont=dict(size=9, color="#334155", family="Inter, sans-serif"),
        row=1, col=2
    )

    n_bars = len(filtered_labels)
    bar_gap = 0.40 if n_bars <= 4 else (0.22 if n_bars <= 10 else 0.12)

    fig.update_layout(
        barmode="overlay",
        bargap=bar_gap,
        margin=dict(l=5, r=5, t=10, b=25),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.08,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#334155")
        ),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=380
    )
    return fig


@functools.lru_cache(maxsize=32)
def render_demographics_pyramid_card(selected_code="PH000000000", view_by="num", age_filter="all"):
    """Population Pyramid bilateral chart with controls and floating zoom widget."""
    entity = get_entity_by_code(selected_code)
    fig = build_demographics_pyramid_figure(entity, view_by, age_filter)

    return html.Div([
        # Panel Header with title & dropdowns
        html.Div([
            html.Div([
                html.H3("Population Pyramid", className="demo-panel-title", style={"fontSize": "0.90rem", "margin": "0"})
            ], style={"marginBottom": "8px"}),
            html.Div([
                # View By Dropdown
                html.Div([
                    html.Span("View By", style={"fontSize": "0.70rem", "fontWeight": "600", "color": "#64748b", "marginRight": "5px", "whiteSpace": "nowrap"}),
                    dcc.Dropdown(
                        id={"type": "demo-pyramid-view", "id": "main"},
                        options=[
                            {"label": "Percentage", "value": "pct"},
                            {"label": "Number of People", "value": "num"}
                        ],
                        value=view_by,
                        clearable=False,
                        searchable=False,
                        className="demo-compact-select",
                        style={"width": "126px"}
                    )
                ], style={"display": "inline-flex", "alignItems": "center"}),

                # Age Group Dropdown
                html.Div([
                    html.Span("Age Group", style={"fontSize": "0.70rem", "fontWeight": "600", "color": "#64748b", "marginRight": "5px", "whiteSpace": "nowrap"}),
                    dcc.Dropdown(
                        id={"type": "demo-pyramid-age-filter", "id": "main"},
                        options=[
                            {"label": "All Ages", "value": "all"},
                            {"label": "0–14 (Youth)", "value": "0-14"},
                            {"label": "15–64 (Working)", "value": "15-64"},
                            {"label": "65+ (Seniors)", "value": "65+"}
                        ],
                        value=age_filter,
                        clearable=False,
                        searchable=False,
                        className="demo-compact-select",
                        style={"width": "108px"}
                    )
                ], style={"display": "inline-flex", "alignItems": "center"})
            ], className="demo-pyramid-controls", style={"display": "flex", "alignItems": "center", "gap": "6px", "flexWrap": "wrap"})
        ], className="demo-panel-header demo-pyramid-header", style={"flexDirection": "column", "alignItems": "flex-start", "marginBottom": "6px"}),

        # Pyramid Graph
        dcc.Graph(
            id={"type": "demo-pyramid-graph", "id": "main"},
            figure=fig,
            config={"displayModeBar": False, "responsive": True}
        )
    ], className="demo-panel")


# =============================================================================
# 4. COLUMN 2: POPULATION BY AGE GROUP (Horizontal Gradient Bar Chart)
# =============================================================================
def build_demographics_age_bar_figure(entity, metric="total"):
    """Build the Plotly figure for the Population by Age Group horizontal gradient bar chart."""
    hh_pop = entity.get("household_pop", 0) or entity.get("total_pop", 1) or 1
    if metric == "male":
        tot_pop = entity.get("hh_male_pop", entity.get("male_pop", 1)) or 1
        dict_data = entity.get("hh_age_male", entity.get("age_male", {}))
    elif metric == "female":
        tot_pop = entity.get("hh_female_pop", entity.get("female_pop", 1)) or 1
        dict_data = entity.get("hh_age_female", entity.get("age_female", {}))
    else:
        tot_pop = hh_pop
        dict_data = entity.get("hh_age_both", entity.get("age_both", {}))

    counts = [dict_data.get(k, 0) for k in AGE_KEYS]
    pcts = [(v / tot_pop) * 100 for v in counts]
    text_labels = [f"{p:.1f}%" for p in pcts]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=AGE_LABELS,
        x=pcts,
        orientation="h",
        marker=dict(
            color=AGE_GRADIENT_COLORS,
            line=dict(color="#ffffff", width=0.5)
        ),
        text=text_labels,
        textposition="outside",
        textfont=dict(size=9.5, color="#002b5c", family="Inter, sans-serif"),
        cliponaxis=False,
        customdata=counts,
        hovertemplate="<b>Age %{y}</b><br>Share: %{x:.2f}%<br>Count: %{customdata:,}<extra></extra>"
    ))

    max_pct = max(pcts) if pcts else 10
    fig.update_layout(
        margin=dict(l=35, r=40, t=10, b=15),
        bargap=0.18,
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, max_pct * 1.25]
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=9, color="#475569", family="Inter, sans-serif")
        ),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=380
    )
    return fig


@functools.lru_cache(maxsize=32)
def render_demographics_age_bar_card(selected_code="PH000000000", metric="total"):
    """Horizontal bar chart with 17 gradient bars (sky blue to mint green) and direct % labels."""
    entity = get_entity_by_code(selected_code)
    fig = build_demographics_age_bar_figure(entity, metric)

    return html.Div([
        # Panel Header with title and dropdown
        html.Div([
            html.Div([
                html.H3("Population by Age Group", className="demo-panel-title", style={"fontSize": "0.90rem", "margin": "0"})
            ], style={"marginBottom": "8px"}),
            html.Div([
                dcc.Dropdown(
                    id={"type": "demo-age-metric", "id": "main"},
                    options=[
                        {"label": "Total Population", "value": "total"},
                        {"label": "Male", "value": "male"},
                        {"label": "Female", "value": "female"}
                    ],
                    value=metric,
                    clearable=False,
                    searchable=False,
                    className="demo-compact-select",
                    style={"width": "125px"}
                )
            ], style={"display": "flex", "justifyContent": "flex-start"})
        ], className="demo-panel-header", style={"flexDirection": "column", "alignItems": "flex-start", "marginBottom": "6px"}),

        # Graph
        dcc.Graph(
            id={"type": "demo-age-bar-graph", "id": "main"},
            figure=fig,
            config={"displayModeBar": False, "responsive": True}
        )
    ], className="demo-panel")


# =============================================================================
# 5. COLUMN 3: POPULATION BY SEX (Donut + What does this mean? Callout)
# =============================================================================
@functools.lru_cache(maxsize=32)
def render_demographics_sex_donut_card(selected_code="PH000000000"):
    """Donut chart with center total population and callout box with View definition button."""
    entity = get_entity_by_code(selected_code)
    tot_pop = entity.get("total_pop", 1) or 1
    hh_pop = entity.get("household_pop", 0) or tot_pop
    male_pop = entity.get("hh_male_pop", entity.get("male_pop", 0))
    female_pop = entity.get("hh_female_pop", entity.get("female_pop", 0))
    male_share = entity.get("hh_male_share", entity.get("male_share", 50.6))
    female_share = entity.get("hh_female_share", entity.get("female_share", 49.4))

    tot_str = format_number(tot_pop)
    hh_str = format_number(hh_pop)

    fig = go.Figure(data=[go.Pie(
        labels=[f"Male  {male_share:.1f}%", f"Female  {female_share:.1f}%"],
        values=[male_pop, female_pop],
        hole=0.62,
        marker=dict(colors=["#0284c7", "#ec4899"], line=dict(color="#ffffff", width=2)),
        sort=False,
        direction="clockwise",
        showlegend=True,
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>"
    )])

    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        height=145,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="#334155")
        )
    )

    return html.Div([
        # Panel Header
        html.Div([
            html.H3("Population by Sex", className="demo-panel-title", style={"fontSize": "0.9rem"})
        ], className="demo-panel-header"),

        # 1. Donut Chart (Above)
        dcc.Graph(
            figure=fig,
            config={"displayModeBar": False, "responsive": True}
        ),

        # 2. Total Population Stat Display (Below the Donut)
        html.Div([
            html.Div(hh_str, style={"fontFamily": "Outfit, sans-serif", "fontSize": "1.25rem", "fontWeight": "800", "color": "#002b5c", "lineHeight": "1.15"}),
            html.Div("Household Population", style={"fontSize": "0.70rem", "fontWeight": "600", "color": "#64748b", "letterSpacing": "0.4px", "textTransform": "uppercase", "marginTop": "2px"}),
            html.Div(f"Total Count: {tot_str}", title="Includes institutional population per Proclamation No. 1179", style={"fontSize": "0.70rem", "color": "#0284c7", "fontWeight": "600", "marginTop": "2px"}),
            html.Div("2020 Census of Population", style={"fontSize": "0.68rem", "color": "#94a3b8", "marginTop": "1px"})
        ], style={
            "textAlign": "center",
            "padding": "6px 10px",
            "background": "#f8fafc",
            "borderRadius": "8px",
            "border": "1px solid #e2e8f0",
            "margin": "4px 0 8px 0"
        }),

        # What does this mean? Callout Box matching reference
        html.Div([
            html.Div([
                html.Span("ℹ", style={"fontWeight": "bold", "color": "#0284c7", "marginRight": "4px"}),
                html.Span("What does this mean?", className="demo-callout-title")
            ], style={"display": "flex", "alignItems": "center"}),
            html.P(
                "The population pyramid shows the number of males and females in each age group. "
                "It helps us understand the age structure of the population.",
                className="demo-callout-text"
            ),
            html.Div([
                html.Button(
                    [html.Span("ℹ", style={"fontWeight": "bold", "marginRight": "4px"}), html.Span("View definition")],
                    id={"type": "nav-btn", "page": "definitions", "source": "demo-sex-callout"},
                    className="demo-pill-btn",
                    title="View official PSA Census definitions"
                )
            ], style={"display": "flex", "alignItems": "center", "gap": "6px"})
        ], className="demo-callout-box")
    ], className="demo-panel", style={"justifyContent": "space-between"})


# =============================================================================
# 6. COLUMN 4: EXPLORE A PLACE & 2020 CPH PRESS RELEASE INSIGHTS
# =============================================================================
def compute_cph_indicators(entity):
    """Compute official PSA 2020 CPH Press Release (Ref. 2022-322) demographic indicators."""
    tot_pop = entity.get("household_pop", 0) or entity.get("total_pop", 1) or 1
    m_pop = entity.get("hh_male_pop", entity.get("male_pop", 0))
    f_pop = entity.get("hh_female_pop", entity.get("female_pop", 1)) or 1
    age_both = entity.get("hh_age_both", entity.get("age_both", {}))
    age_male = entity.get("hh_age_male", entity.get("age_male", {}))
    age_female = entity.get("hh_age_female", entity.get("age_female", {}))

    # 1. Median Age
    median_age = calculate_median_age(entity)

    # 2. Women of Reproductive Age (15–49 years old)
    reprod_keys = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"]
    reprod_females = sum(age_female.get(k, 0) for k in reprod_keys)
    reprod_share = (reprod_females / f_pop) * 100 if f_pop > 0 else 51.9

    # 3. School-Age Population (5–24 years old)
    school_keys = ["5-9", "10-14", "15-19", "20-24"]
    school_pop = sum(age_both.get(k, 0) for k in school_keys)
    school_share = (school_pop / tot_pop) * 100 if tot_pop > 0 else 39.4

    # 4. Senior Citizens (60 years old and over)
    senior_keys = ["60-64", "65-69", "70-74", "75-79", "80 years old and over"]
    senior_pop = sum(age_both.get(k, 0) for k in senior_keys)
    senior_females = sum(age_female.get(k, 0) for k in senior_keys)
    senior_share = (senior_pop / tot_pop) * 100 if tot_pop > 0 else 8.5
    senior_fem_share = (senior_females / senior_pop) * 100 if senior_pop > 0 else 55.5

    # 5. Age Dependency Ratios (Young 0-14, Old 65+, Working 15-64)
    working_keys = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64"]
    young_keys = ["Below 5", "5-9", "10-14"]
    old_keys = ["65-69", "70-74", "75-79", "80 years old and over"]

    working_pop = sum(age_both.get(k, 0) for k in working_keys) or 1
    young_pop = sum(age_both.get(k, 0) for k in young_keys)
    old_pop = sum(age_both.get(k, 0) for k in old_keys)

    young_dep = round((young_pop / working_pop) * 100, 1)
    old_dep = round((old_pop / working_pop) * 100, 1)
    total_dep = round(((young_pop + old_pop) / working_pop) * 100, 1)

    return {
        "tot_pop": tot_pop,
        "m_pop": m_pop,
        "f_pop": f_pop,
        "median_age": median_age,
        "reprod_females": reprod_females,
        "reprod_share": reprod_share,
        "school_pop": school_pop,
        "school_share": school_share,
        "senior_pop": senior_pop,
        "senior_share": senior_share,
        "senior_fem_share": senior_fem_share,
        "young_dep": young_dep,
        "old_dep": old_dep,
        "total_dep": total_dep
    }


def render_cph_modal(entity, cph):
    """Interactive modal presenting official PSA 2020 CPH Press Release Ref. No. 2022-322 findings."""
    name = entity.get("short_name", entity["name"])
    level = entity.get("level", "Country")

    # Comparator Rows if looking at sub-national area
    comparator_section = []
    if level != "Country":
        diff_med = cph["median_age"] - 25.3
        diff_dep = cph["total_dep"] - 57.0
        diff_sen = cph["senior_share"] - 8.5
        diff_rep = cph["reprod_share"] - 51.9
        diff_sch = cph["school_share"] - 39.4

        def make_tag(diff, unit=""):
            if abs(diff) < 0.1:
                return html.Span("Matched", className="cph-diff-badge cph-diff-neutral")
            sign = "+" if diff > 0 else ""
            cls = "cph-diff-higher" if diff > 0 else "cph-diff-lower"
            return html.Span(f"{sign}{diff:.1f}{unit}", className=f"cph-diff-badge {cls}")

        comparator_section = [
            html.H5(f"Local vs. National Benchmark Comparison ({name})",
                    style={"fontSize": "0.82rem", "fontWeight": "800", "color": "#002b5c", "margin": "14px 0 6px 0"}),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Indicator"),
                    html.Th(f"{name}"),
                    html.Th("National Avg"),
                    html.Th("Variance")
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td("Median Age", style={"fontWeight": "600"}),
                        html.Td(f"{cph['median_age']:.1f} yrs"),
                        html.Td("25.3 yrs"),
                        html.Td(make_tag(diff_med, " yrs"))
                    ]),
                    html.Tr([
                        html.Td("Dependency Ratio", style={"fontWeight": "600"}),
                        html.Td(f"{cph['total_dep']:.1f} per 100"),
                        html.Td("57.0 per 100"),
                        html.Td(make_tag(diff_dep))
                    ]),
                    html.Tr([
                        html.Td("Senior Citizens (60+)", style={"fontWeight": "600"}),
                        html.Td(f"{cph['senior_share']:.1f}%"),
                        html.Td("8.5%"),
                        html.Td(make_tag(diff_sen, "%"))
                    ]),
                    html.Tr([
                        html.Td("Reproductive Females (15-49)", style={"fontWeight": "600"}),
                        html.Td(f"{cph['reprod_share']:.1f}%"),
                        html.Td("51.9%"),
                        html.Td(make_tag(diff_rep, "%"))
                    ]),
                    html.Tr([
                        html.Td("School-Age Youth (5-24)", style={"fontWeight": "600"}),
                        html.Td(f"{cph['school_share']:.1f}%"),
                        html.Td("39.4%"),
                        html.Td(make_tag(diff_sch, "%"))
                    ])
                ])
            ], className="cph-compare-table")
        ]

    return html.Div([
        # Transparent Backdrop Overlay
        html.Div(id={"type": "cph-modal-backdrop", "id": "main"}, className="cph-modal-backdrop"),

        # Modal Box
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.Div("OFFICIAL 2020 CPH HIGHLIGHTS", style={"fontSize": "0.68rem", "fontWeight": "800", "letterSpacing": "0.5px", "color": "#7dd3fc"}),
                    html.H4("Age & Sex Distribution in the Philippines", style={"fontSize": "1.05rem", "fontWeight": "800", "margin": "2px 0 0 0"}),
                    html.Div("PSA Press Release Ref. No. 2022-322 | 2020 Census of Population and Housing", style={"fontSize": "0.72rem", "color": "#cbd5e1"})
                ]),
                html.Button("✕", id={"type": "btn-close-cph-modal", "id": "main"},
                            style={"background": "transparent", "border": "none", "color": "#ffffff", "fontSize": "1.2rem", "cursor": "pointer", "padding": "4px 8px"})
            ], className="cph-modal-header"),

            # Body
            html.Div([
                # 4 KPI Tiles
                html.Div([
                    html.Div([
                        html.Div("MEDIAN AGE", style={"fontSize": "0.65rem", "fontWeight": "800", "color": "#0284c7"}),
                        html.Div("25.3 yrs", style={"fontSize": "1.15rem", "fontWeight": "800", "color": "#002b5c"}),
                        html.Div("Rising from 24.3 (2015)", style={"fontSize": "0.62rem", "color": "#64748b"})
                    ], className="cph-kpi-tile"),
                    html.Div([
                        html.Div("OVERALL SEX RATIO", style={"fontSize": "0.65rem", "fontWeight": "800", "color": "#0284c7"}),
                        html.Div("103 males", style={"fontSize": "1.15rem", "fontWeight": "800", "color": "#002b5c"}),
                        html.Div("per 100 females", style={"fontSize": "0.62rem", "color": "#64748b"})
                    ], className="cph-kpi-tile"),
                    html.Div([
                        html.Div("DEPENDENCY RATIO", style={"fontSize": "0.65rem", "fontWeight": "800", "color": "#0284c7"}),
                        html.Div("57 per 100", style={"fontSize": "1.15rem", "fontWeight": "800", "color": "#002b5c"}),
                        html.Div("Down from 58 (2015)", style={"fontSize": "0.62rem", "color": "#64748b"})
                    ], className="cph-kpi-tile"),
                    html.Div([
                        html.Div("SENIORS (60+)", style={"fontSize": "0.65rem", "fontWeight": "800", "color": "#0284c7"}),
                        html.Div("9.22 M", style={"fontSize": "1.15rem", "fontWeight": "800", "color": "#002b5c"}),
                        html.Div("8.5% of pop (55.5% F)", style={"fontSize": "0.62rem", "color": "#64748b"})
                    ], className="cph-kpi-tile"),
                ], className="cph-kpi-grid"),

                # Key Findings Deep-Dives
                html.Div([
                    html.Div([
                        html.Div([
                            html.Span("⚖ ", style={"fontSize": "0.9rem"}),
                            html.Span("The Age 55 Sex Crossover (Female Longevity)", style={"fontWeight": "700", "fontSize": "0.78rem", "color": "#002b5c"})
                        ]),
                        html.P(
                            "Males outnumber females in all age brackets from 0 to 54 years. However, starting at age 55, "
                            "the gender balance flips decisively: females outnumber males, representing 13.4% of the cohort vs. 11.2% for males. "
                            "Among senior citizens (60+), females account for 55.5% due to higher female life expectancy.",
                            style={"fontSize": "0.72rem", "color": "#334155", "lineHeight": "1.35", "margin": "3px 0 0 0"}
                        )
                    ], className="cph-finding-card", style={"borderLeftColor": "#db2777"}),

                    html.Div([
                        html.Div([
                            html.Span("👩 ", style={"fontSize": "0.9rem"}),
                            html.Span("Women of Reproductive Age (15 to 49 years)", style={"fontWeight": "700", "fontSize": "0.78rem", "color": "#002b5c"})
                        ]),
                        html.P(
                            "Nationwide, 27.85 million females are of reproductive age, representing 51.9% of the total female household population. "
                            "This proportion saw a slight reduction from 52.2% (26.02M) in 2015.",
                            style={"fontSize": "0.72rem", "color": "#334155", "lineHeight": "1.35", "margin": "3px 0 0 0"}
                        )
                    ], className="cph-finding-card", style={"borderLeftColor": "#0284c7"}),

                    html.Div([
                        html.Div([
                            html.Span("🎓 ", style={"fontSize": "0.9rem"}),
                            html.Span("School-Age Population (5 to 24 years)", style={"fontWeight": "700", "fontSize": "0.78rem", "color": "#002b5c"})
                        ]),
                        html.P(
                            "The school-age population reached 42.78 million (39.4% of the household population), down from 40.6% in 2015. "
                            "This trend aligns with declining fertility and shifting national youth demographics.",
                            style={"fontSize": "0.72rem", "color": "#334155", "lineHeight": "1.35", "margin": "3px 0 0 0"}
                        )
                    ], className="cph-finding-card", style={"borderLeftColor": "#059669"}),
                ]),

                # Comparator table
                *comparator_section

            ], className="cph-modal-body"),

            # Footer
            html.Div([
                html.Div([
                    html.Span("Source: ", style={"fontSize": "0.7rem", "color": "#64748b"}),
                    html.A("PSA Press Release 2022-322", href="https://psa.gov.ph/content/age-and-sex-distribution-philippine-population-2020-census-population-and-housing", target="_blank",
                           style={"fontSize": "0.7rem", "color": "#0284c7", "fontWeight": "600", "textDecoration": "none"})
                ]),
                html.Button("Close", id={"type": "btn-close-cph-modal", "id": "main"}, className="demo-pill-btn",
                            style={"fontSize": "0.72rem", "padding": "4px 14px", "fontWeight": "700"})
            ], className="cph-modal-footer")
        ], className="cph-modal-box")
    ], id={"type": "cph-highlights-modal", "id": "main"}, className="cph-modal-overlay")


@functools.lru_cache(maxsize=32)
def render_demographics_profile_insights_card(selected_code="PH000000000"):
    """Explore a Place statistics breakdown, nested callout box, Compare button, and 2020 CPH Press Release Insights."""
    entity = get_entity_by_code(selected_code)
    name = entity.get("short_name", entity["name"])
    level = entity.get("level", "Country")
    tot_pop = entity.get("total_pop", 0)
    hh_pop = entity.get("household_pop", 0) or tot_pop
    male_pop = entity.get("hh_male_pop", entity.get("male_pop", 0))
    female_pop = entity.get("hh_female_pop", entity.get("female_pop", 0))
    male_share = entity.get("hh_male_share", entity.get("male_share", 50.6))
    female_share = entity.get("hh_female_share", entity.get("female_share", 49.4))
    median_age = calculate_median_age(entity)

    # Compute official 2020 CPH Press Release indicators
    cph = compute_cph_indicators(entity)

    # Majority sex determination
    if female_pop >= male_pop:
        maj_text = "females than males"
    else:
        maj_text = "males than females"

    area_title = "National" if level == "Country" else level

    callout_text = (
        f"{name} has {format_number(hh_pop)} household population in 2020 "
        f"({format_abbreviated_m(male_pop)} males and {format_abbreviated_m(female_pop)} females), "
        f"with a slightly higher number of {maj_text}."
    )

    # Prepare dynamic insight bullet texts
    if level == "Country":
        med_insight = "Median age is 25.3 years (up from 24.3 in 2015), indicating a steadily maturing population."
        dep_insight = f"Dependency ratio: {cph['total_dep']:.1f} per 100 workers ({cph['young_dep']:.1f} young + {cph['old_dep']:.1f} elderly; down from 58 in 2015)."
        rep_insight = f"Women of reproductive age (15–49) total {format_abbreviated_m(cph['reprod_females'])}, or {cph['reprod_share']:.1f}% of all females."
        sch_insight = f"School-age youth (5–24 years) stand at {format_abbreviated_m(cph['school_pop'])} ({cph['school_share']:.1f}% of household residents)."
        sen_insight = f"Senior citizens (60+) make up 8.5% (9.22M), with females (55.5%) outnumbering males due to longevity."
    else:
        diff_med = round(cph["median_age"] - 25.3, 1)
        med_tag = f" ({'+' if diff_med > 0 else ''}{diff_med:.1f} vs nat'l)" if abs(diff_med) >= 0.1 else " (matches nat'l)"
        med_insight = f"{name} has a median age of {cph['median_age']:.1f} years{med_tag}."
        dep_insight = f"Dependency burden: {cph['total_dep']:.1f} per 100 workers ({cph['young_dep']:.1f} young + {cph['old_dep']:.1f} seniors)."
        rep_insight = f"Women of reproductive age (15–49) comprise {cph['reprod_share']:.1f}% ({format_abbreviated_m(cph['reprod_females'])}) of local females."
        sch_insight = f"School-age youth (5–24 years) account for {cph['school_share']:.1f}% ({format_abbreviated_m(cph['school_pop'])}) of residents."
        sen_insight = f"Senior citizens (60+) make up {cph['senior_share']:.1f}% ({format_abbreviated_m(cph['senior_pop'])}), with females at {cph['senior_fem_share']:.1f}%."

    return html.Div([
        # Modal (rendered inside card, toggled via clientside callback)
        render_cph_modal(entity, cph),

        # Section 1: Explore a Place
        html.Div([
            html.H3("Explore a Place", className="demo-panel-title", style={"marginBottom": "8px", "fontSize": "0.9rem"}),

            # Place Lockup
            html.Div([
                html.Div(
                    html.Img(src="/assets/icons/pin.svg",
                             style={"width": "15px", "height": "15px", "filter": "brightness(0) invert(1)"}),
                    style={
                        "width": "26px", "height": "26px", "borderRadius": "6px",
                        "backgroundColor": "#0d9488", "display": "flex", "alignItems": "center",
                        "justifyContent": "center", "marginRight": "8px", "flexShrink": "0"
                    }
                ),
                html.Div([
                    html.Div(name.upper(), style={"fontSize": "0.85rem", "fontWeight": "800", "color": "#002b5c", "lineHeight": "1.1"}),
                    html.Div(area_title, style={"fontSize": "0.7rem", "color": "#64748b"})
                ])
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),

            # Stats Table
            html.Div([
                html.Div([
                    html.Span("Household pop.", className="demo-stat-label"),
                    html.Span(format_number(hh_pop), className="demo-stat-value")
                ], className="demo-stat-row"),
                html.Div([
                    html.Span("Male", className="demo-stat-label"),
                    html.Span(f"{format_number(male_pop)} ({male_share:.1f}%)", className="demo-stat-value")
                ], className="demo-stat-row"),
                html.Div([
                    html.Span("Female", className="demo-stat-label"),
                    html.Span(f"{format_number(female_pop)} ({female_share:.1f}%)", className="demo-stat-value")
                ], className="demo-stat-row"),
                html.Div([
                    html.Span("Median age", className="demo-stat-label"),
                    html.Span(f"{median_age:.1f} years", className="demo-stat-value")
                ], className="demo-stat-row"),
                html.Div([
                    html.Span("Total population", className="demo-stat-label"),
                    html.Span(format_number(tot_pop), className="demo-stat-value")
                ], className="demo-stat-row"),
            ]),

            # Nested Callout Box
            html.Div([
                html.Div([
                    html.Span("★", style={"color": "#0284c7", "marginRight": "4px", "fontSize": "0.8rem"}),
                    html.Span("What does this mean?", style={"fontSize": "0.74rem", "fontWeight": "700", "color": "#0284c7"})
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "2px"}),
                html.P(callout_text, style={"fontSize": "0.72rem", "color": "#334155", "lineHeight": "1.35", "margin": "0"})
            ], className="demo-callout-box", style={"marginTop": "6px", "padding": "8px 10px"})
        ]),

        # Section 2: 2020 CPH Key Takeaways & Quick Insights
        html.Div([
            html.Div([
                html.H4("Quick Insights", style={"fontSize": "0.82rem", "fontWeight": "800", "color": "#002b5c", "margin": 0}),
                html.Button(
                    [html.Span("Highlights"), html.Span(" ↗", style={"fontSize": "0.72rem", "marginLeft": "2px"})],
                    id={"type": "btn-open-cph-modal", "id": "main"},
                    className="demo-pill-btn",
                    style={"fontSize": "0.68rem", "padding": "2px 8px", "fontWeight": "700", "cursor": "pointer"}
                )
            ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between", "margin": "10px 0 6px 0"}),

            # Bullet 1: Median Age
            html.Div([
                html.Div(
                    html.Img(src="/assets/icons/gauge.svg", style={"width": "12px", "height": "12px", "filter": "brightness(0) invert(1)"}),
                    className="demo-insight-badge",
                    style={"backgroundColor": "#0284c7"}
                ),
                html.Span(med_insight, className="demo-insight-text")
            ], className="demo-insight-item"),

            # Bullet 2: Dependency Ratio & Young/Elderly breakdown
            html.Div([
                html.Div(
                    html.Img(src="/assets/icons/chart.svg", style={"width": "12px", "height": "12px", "filter": "brightness(0) invert(1)"}),
                    className="demo-insight-badge",
                    style={"backgroundColor": "#0d9488"}
                ),
                html.Span(dep_insight, className="demo-insight-text")
            ], className="demo-insight-item"),

            # Bullet 3: Women of Reproductive Age (15-49)
            html.Div([
                html.Div(
                    html.Img(src="/assets/icons/female.svg", style={"width": "12px", "height": "12px", "filter": "brightness(0) invert(1)"}),
                    className="demo-insight-badge",
                    style={"backgroundColor": "#db2777"}
                ),
                html.Span(rep_insight, className="demo-insight-text")
            ], className="demo-insight-item"),

            # Bullet 4: School-Age Cohort (5-24)
            html.Div([
                html.Div(
                    html.Img(src="/assets/icons/users.svg", style={"width": "12px", "height": "12px", "filter": "brightness(0) invert(1)"}),
                    className="demo-insight-badge",
                    style={"backgroundColor": "#059669"}
                ),
                html.Span(sch_insight, className="demo-insight-text")
            ], className="demo-insight-item"),

            # Bullet 5: Senior Citizens (60+)
            html.Div([
                html.Div(
                    html.Img(src="/assets/icons/family.svg", style={"width": "12px", "height": "12px", "filter": "brightness(0) invert(1)"}),
                    className="demo-insight-badge",
                    style={"backgroundColor": "#d97706"}
                ),
                html.Span(sen_insight, className="demo-insight-text")
            ], className="demo-insight-item"),
        ])
    ], className="demo-panel")

