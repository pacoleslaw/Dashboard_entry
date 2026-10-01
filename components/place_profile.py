"""
Place Profile and 'Follow the Number' Component.
Renders detailed profile of selected geographic entity with plain-language explanation
and interactive breadcrumb hierarchy navigation.
"""
from dash import html
from utils.data_loader import get_entity_by_code
from utils.formatting import format_number, format_percentage, format_compact, format_sex_ratio
from utils.narratives import get_plain_language_explanation

def render_follow_the_number(selected_code="PH000000000"):
    """
    Renders clickable 'Follow the Number' breadcrumb hierarchy:
    PHILIPPINES (109.0M) -> REGION (XX.XM) -> PROVINCE/CITY (XX.XM)
    """
    curr = get_entity_by_code(selected_code)
    nat = get_entity_by_code("PH000000000")

    btn_base_style = {
        "display": "inline-flex",
        "alignItems": "center",
        "justifyContent": "center",
        "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "fontSize": "0.78rem",
        "fontWeight": "600",
        "color": "#1a3b94",
        "backgroundColor": "#f1f6fb",
        "border": "1px solid #cbdde9",
        "borderRadius": "6px",
        "padding": "4px 10px",
        "lineHeight": "1.25",
        "cursor": "pointer",
        "transition": "all 0.15s ease-in-out",
        "verticalAlign": "middle",
        "outline": "none"
    }

    btn_active_style = {
        **btn_base_style,
        "backgroundColor": "#eff6ff",
        "border": "1.5px solid #1a3b94",
        "fontWeight": "700",
        "color": "#1a3b94",
        "boxShadow": "0 1px 3px rgba(26, 59, 148, 0.15)"
    }

    arrow_style = {
        "color": "#8da4be",
        "fontSize": "0.85rem",
        "fontWeight": "700",
        "display": "inline-flex",
        "alignItems": "center",
        "userSelect": "none",
        "margin": "0 2px",
        "verticalAlign": "middle"
    }

    is_country_active = (curr["level"] == "Country")
    crumbs = [
        html.Button(
            f"Philippines ({format_compact(nat['total_pop'])})",
            id={"type": "crumb-btn", "code": "PH000000000"},
            className=f"follow-crumb-btn {'active' if is_country_active else ''}",
            style=btn_active_style if is_country_active else btn_base_style
        )
    ]

    if curr["level"] in ["Region", "Province/City"]:
        reg_code = curr["code"] if curr["level"] == "Region" else curr.get("parent_code")
        reg = get_entity_by_code(reg_code)
        is_reg_active = (curr["level"] == "Region")
        crumbs.append(html.Span("→", className="follow-arrow", style=arrow_style))
        crumbs.append(
            html.Button(
                f"{reg['short_name']} ({format_compact(reg['total_pop'])})",
                id={"type": "crumb-btn", "code": reg["code"]},
                className=f"follow-crumb-btn {'active' if is_reg_active else ''}",
                style=btn_active_style if is_reg_active else btn_base_style
            )
        )

    if curr["level"] == "Province/City":
        crumbs.append(html.Span("→", className="follow-arrow", style=arrow_style))
        crumbs.append(
            html.Button(
                f"{curr['short_name']} ({format_compact(curr['total_pop'])})",
                id={"type": "crumb-btn", "code": curr["code"]},
                className="follow-crumb-btn active",
                style=btn_active_style
            )
        )

    container_style = {
        "display": "flex",
        "alignItems": "center",
        "flexWrap": "wrap",
        "gap": "10px",
        "backgroundColor": "#ffffff",
        "border": "1px solid #dce8f2",
        "borderRadius": "8px",
        "padding": "7px 14px",
        "marginBottom": "14px",
        "boxShadow": "0 1px 3px rgba(0, 0, 0, 0.03)"
    }

    label_style = {
        "display": "inline-flex",
        "alignItems": "center",
        "gap": "8px",
        "fontFamily": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "fontWeight": "700",
        "fontSize": "0.78rem",
        "color": "#030130",
        "letterSpacing": "0.2px",
        "textTransform": "uppercase",
        "whiteSpace": "nowrap",
        "marginRight": "4px"
    }

    crumbs_container_style = {
        "display": "inline-flex",
        "alignItems": "center",
        "gap": "6px",
        "flexWrap": "wrap"
    }

    return html.Div([
        html.Div([
            html.Img(src="/assets/icons/map.svg", alt="Hierarchy", style={"width": "16px", "height": "16px", "verticalAlign": "middle"}),
            html.Span("FOLLOW THE NUMBER (Geographic Hierarchy):")
        ], className="follow-number-label", style=label_style),
        html.Div(crumbs, className="follow-crumbs-container", style=crumbs_container_style)
    ], className="follow-number-bar", style=container_style)

def render_place_profile(selected_code="PH000000000"):
    """Render About This Place and What Does This Mean card."""
    entity = get_entity_by_code(selected_code)
    name = entity["name"]
    level = entity["level"]
    pop = entity["total_pop"]
    male = entity["male_pop"]
    female = entity["female_pop"]
    nat_share = entity["nat_share"]
    parent_share = entity.get("parent_share", 100.0)
    sex_ratio = entity["sex_ratio"]
    dep_ratio = entity["dependency_ratio"]
    explanation = get_plain_language_explanation(selected_code)

    table_rows = [
        ("Official Population", format_number(pop)),
        ("Male Population", f"{format_number(male)} ({entity['male_share']:.1f}%)"),
        ("Female Population", f"{format_number(female)} ({entity['female_share']:.1f}%)"),
        ("Sex Ratio", f"{sex_ratio:.1f} males per 100 females"),
        ("Age Dependency Ratio", f"{dep_ratio:.1f} per 100 working-age"),
        ("Share of National Population", f"{nat_share:.2f}%"),
    ]

    if level != "Country":
        table_rows.append(("Share of Parent Region", f"{parent_share:.2f}%"))

    return html.Div([
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/building.svg", alt="Place", style={"width": "18px", "height": "18px", "marginRight": "8px"}),
                html.Span(f"About This Place: {name}", className="panel-title")
            ], style={"display": "flex", "alignItems": "center"}),
            html.Span(level, className="kpi-badge kpi-badge-blue", style={"fontSize": "0.8rem", "padding": "4px 10px"})
        ], className="panel-header"),

        # Grid of stats + explanation
        html.Div([
            # Left: Stat table
            html.Div([
                html.Table([
                    html.Tbody([
                        html.Tr([
                            html.Td(label, style={"fontWeight": "600", "color": "var(--text-muted)", "padding": "6px 8px", "borderBottom": "1px solid var(--border-light)"}),
                            html.Td(val, style={"fontWeight": "700", "color": "var(--psa-navy)", "padding": "6px 8px", "borderBottom": "1px solid var(--border-light)", "textAlign": "right"})
                        ])
                        for label, val in table_rows
                    ])
                ], style={"width": "100%", "fontSize": "0.82rem"})
            ], style={"flex": "1", "minWidth": "280px"}),

            # Right: What does this mean?
            html.Div([
                html.Div([
                    html.Img(src="/assets/icons/lightbulb.svg", alt="Insights", style={"width": "16px", "height": "16px", "marginRight": "6px"}),
                    html.Span("WHAT DOES THIS MEAN?", style={"fontWeight": "700", "fontSize": "0.82rem", "color": "var(--psa-navy)"})
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px"}),
                html.P(explanation, style={"fontSize": "0.84rem", "lineHeight": "1.55", "color": "#1e293b", "background": "#f8fafc", "padding": "12px 14px", "borderRadius": "var(--radius-sm)", "border": "1px solid var(--border-color)"}),
                html.Div([
                    html.Span("Reference Year: ", style={"fontWeight": "600", "color": "var(--text-muted)", "fontSize": "0.75rem"}),
                    html.Span("2020 CPH • Official PSA Source", style={"fontSize": "0.75rem", "color": "var(--psa-blue)", "fontWeight": "600"})
                ], style={"marginTop": "8px"})
            ], style={"flex": "1.2", "minWidth": "280px"})
        ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"})
    ], className="panel-card")
