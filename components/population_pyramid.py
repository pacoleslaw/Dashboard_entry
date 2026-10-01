"""
Population Pyramid and Age Distribution Component.
Visualizes age-sex demographic structure using official PSA 2020 CPH data.
Male counts on left, Female counts on right, 17 standard age groups on vertical axis.
"""
from dash import html, dcc
import plotly.graph_objects as go
from utils.data_loader import get_entity_by_code
from utils.formatting import format_compact, format_number

def render_population_pyramid(selected_code="PH000000000"):
    entity = get_entity_by_code(selected_code)
    age_groups = entity["age_groups"]
    male_counts = [entity["age_male"].get(g, 0) for g in age_groups]
    female_counts = [entity["age_female"].get(g, 0) for g in age_groups]
    total_pop = entity["total_pop"]

    # Negative values for male bars (left side)
    male_neg = [-v for v in male_counts]

    # Calculate max limit for symmetric x-axis
    max_count = max(max(male_counts), max(female_counts)) if male_counts else 1000
    # Axis ticks at 4 intervals
    step = max_count / 3
    tick_vals = [-step * 3, -step * 2, -step, 0, step, step * 2, step * 3]
    tick_text = [format_compact(abs(v)) for v in tick_vals]

    fig = go.Figure()

    # Male trace
    fig.add_trace(go.Bar(
        y=age_groups,
        x=male_neg,
        name="Male",
        orientation='h',
        marker=dict(color="#0284c7", line=dict(color="#ffffff", width=0.5)),
        customdata=[(v, (v / total_pop) * 100 if total_pop > 0 else 0) for v in male_counts],
        hovertemplate="<b>Age: %{y}</b><br>Male: %{customdata[0]:,} (%{customdata[1]:.2f}%)<extra></extra>"
    ))

    # Female trace
    fig.add_trace(go.Bar(
        y=age_groups,
        x=female_counts,
        name="Female",
        orientation='h',
        marker=dict(color="#ec4899", line=dict(color="#ffffff", width=0.5)),
        customdata=[(v, (v / total_pop) * 100 if total_pop > 0 else 0) for v in female_counts],
        hovertemplate="<b>Age: %{y}</b><br>Female: %{customdata[0]:,} (%{customdata[1]:.2f}%)<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>Population Pyramid: {entity['name']}</b>",
            font=dict(size=14, color="#002d62", family="Outfit, sans-serif"),
            x=0.02
        ),
        barmode='overlay',
        bargap=0.1,
        margin=dict(l=60, r=20, t=45, b=40),
        xaxis=dict(
            tickmode='array',
            tickvals=tick_vals,
            ticktext=tick_text,
            title=dict(text="Population (Persons)", font=dict(size=11, family="Inter, sans-serif")),
            gridcolor="#f1f5f9",
            zerolinecolor="#cbd5e1",
            zerolinewidth=2
        ),
        yaxis=dict(
            autorange=True,
            title=None,
            tickfont=dict(size=10, family="Inter, sans-serif")
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        ),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=440
    )

    return html.Div([
        dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True})
    ], className="panel-card")

def render_age_distribution_chart(selected_code="PH000000000"):
    """Alternative Age Distribution bar chart showing Both Sexes by Age Cohort."""
    entity = get_entity_by_code(selected_code)
    age_groups = entity["age_groups"]
    both_counts = [entity["age_both"].get(g, 0) for g in age_groups]
    total_pop = entity["total_pop"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=age_groups,
        y=both_counts,
        marker=dict(
            color="#2563eb",
            line=dict(color="#ffffff", width=1)
        ),
        customdata=[(v / total_pop) * 100 if total_pop > 0 else 0 for v in both_counts],
        hovertemplate="<b>Age Group: %{x}</b><br>Population: %{y:,} (%{customdata:.2f}%)<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>Population by Age Group: {entity['name']}</b>",
            font=dict(size=14, color="#002d62", family="Outfit, sans-serif"),
            x=0.02
        ),
        margin=dict(l=40, r=20, t=45, b=60),
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=10, family="Inter, sans-serif"),
            showgrid=False
        ),
        yaxis=dict(
            title="Persons",
            gridcolor="#f1f5f9",
            tickformat=","
        ),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=380
    )

    return html.Div([
        dcc.Graph(figure=fig, config={"displayModeBar": False, "responsive": True})
    ], className="panel-card")
