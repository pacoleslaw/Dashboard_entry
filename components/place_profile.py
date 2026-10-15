"""
Place Profile and 'Follow the Number' Component.
Renders detailed profile of selected geographic entity with plain-language explanation
and interactive breadcrumb hierarchy navigation.
"""
from dash import html, dcc
from utils.data_loader import get_entity_by_code
from utils.geography import (
    get_regions,
    get_provinces,
    get_city_municipalities,
    resolve_geo_hierarchy,
    HUC_TO_PROVINCE
)
from utils.formatting import format_number, format_percentage, format_compact, format_sex_ratio
from utils.narratives import get_plain_language_explanation

def render_follow_the_number(selected_code="PH000000000"):
    """
    Renders cascading dropdown selector replacing breadcrumbs:
    [GEOGRAPHIC FILTER] [Region Dropdown] [Province Dropdown] [City/Mun Dropdown] [↺ Reset]
    """
    sel_reg, sel_prov, sel_city = resolve_geo_hierarchy(selected_code)

    # 1. Region options
    regions = get_regions()
    region_options = [{"label": "All Regions", "value": "ALL"}] + [
        {"label": r["short_name"], "value": r["code"]} for r in regions
    ]

    # 2. Province options
    if sel_reg and sel_reg != "ALL":
        if sel_reg == "PH130000000":
            prov_options = [{"label": "Metropolitan Manila (NCR)", "value": "ALL"}]
            prov_disabled = True
            prov_placeholder = "Metropolitan Manila"
        else:
            provinces = get_provinces(sel_reg)
            prov_list = [p for p in provinces if p["name"] not in HUC_TO_PROVINCE]
            prov_options = [{"label": "All Provinces", "value": "ALL"}] + [
                {"label": p["name"], "value": p["code"]} for p in prov_list
            ]
            prov_disabled = False
            prov_placeholder = "All Provinces"
    else:
        prov_options = [{"label": "All Provinces", "value": "ALL"}]
        prov_disabled = True
        prov_placeholder = "Select Region first"

    # 3. City / Municipality options
    if sel_reg == "PH130000000":
        ncr_lgus = get_provinces("PH130000000")
        city_options = [{"label": "All Cities / Municipalities", "value": "ALL"}] + [
            {"label": lgu["name"], "value": lgu["code"]} for lgu in ncr_lgus
        ]
        city_disabled = False
        city_placeholder = "All Cities / Municipalities"
    elif sel_prov and sel_prov != "ALL":
        munis = get_city_municipalities(sel_prov)
        city_options = [{"label": "All Cities / Municipalities", "value": "ALL"}] + [
            {"label": m["name"], "value": m["code"]} for m in munis
        ]
        city_disabled = False
        city_placeholder = "All Cities / Municipalities"
    elif sel_reg and sel_reg != "ALL":
        provinces = get_provinces(sel_reg)
        hucs = [p for p in provinces if p["name"] in HUC_TO_PROVINCE]
        if hucs:
            city_options = [{"label": "All Cities / Municipalities", "value": "ALL"}] + [
                {"label": h["name"] + " (HUC)", "value": h["code"]} for h in hucs
            ]
        else:
            city_options = [{"label": "All Cities / Municipalities", "value": "ALL"}]
        city_disabled = False
        city_placeholder = "All Cities / Municipalities"
    else:
        city_options = [{"label": "All Cities / Municipalities", "value": "ALL"}]
        city_disabled = True
        city_placeholder = "Select Province first"

    has_selection = (sel_reg != "ALL" or sel_prov != "ALL" or sel_city != "ALL")

    return html.Div([
        # Label & Icon
        html.Div([
            html.Img(src="/assets/icons/map.svg", alt="Hierarchy", style={"width": "16px", "height": "16px", "verticalAlign": "middle"}),
            html.Span("GEOGRAPHIC HIERARCHY:")
        ], className="follow-number-label"),

        # 3 Cascading Dropdowns
        html.Div([
            # Region Dropdown
            html.Div([
                html.Span("Region", className="geo-dropdown-field-label"),
                dcc.Dropdown(
                    id={"type": "pop-filter-region", "id": "main"},
                    options=region_options,
                    value=sel_reg,
                    clearable=False,
                    placeholder="All Regions",
                    className="geo-dropdown-select"
                )
            ], className="geo-dropdown-field"),

            # Province Dropdown
            html.Div([
                html.Span("Province", className="geo-dropdown-field-label"),
                dcc.Dropdown(
                    id={"type": "pop-filter-prov", "id": "main"},
                    options=prov_options,
                    value=sel_prov,
                    clearable=False,
                    disabled=prov_disabled,
                    placeholder=prov_placeholder,
                    className="geo-dropdown-select"
                )
            ], className="geo-dropdown-field"),

            # City / Municipality Dropdown
            html.Div([
                html.Span("City/Mun", className="geo-dropdown-field-label"),
                dcc.Dropdown(
                    id={"type": "pop-filter-city", "id": "main"},
                    options=city_options,
                    value=sel_city,
                    clearable=False,
                    disabled=city_disabled,
                    placeholder=city_placeholder,
                    className="geo-dropdown-select"
                )
            ], className="geo-dropdown-field"),
        ], className="geo-dropdowns-group"),

        # Reset button
        (
            html.Button(
                [html.Span("↺", style={"marginRight": "5px", "fontWeight": "bold"}), "Reset to Philippines"],
                id={"type": "crumb-btn", "code": "PH000000000"},
                className="geo-reset-btn",
                title="Reset to whole country"
            ) if has_selection else html.Span()
        )
    ], className="follow-number-bar")


def render_place_profile(selected_code="PH000000000"):
    """Render About This Place and What Does This Mean card."""
    entity = get_entity_by_code(selected_code)
    name = entity["name"]
    level = entity["level"]
    pop = entity["total_pop"]
    hh_pop = entity.get("household_pop", 0) or pop
    male = entity.get("hh_male_pop", entity.get("male_pop", 0))
    female = entity.get("hh_female_pop", entity.get("female_pop", 0))
    male_share = entity.get("hh_male_share", entity.get("male_share", 50.6))
    female_share = entity.get("hh_female_share", entity.get("female_share", 49.4))
    sex_ratio = entity.get("hh_sex_ratio", entity.get("sex_ratio", 102.6))
    nat_share = entity["nat_share"]
    parent_share = entity.get("parent_share", 100.0)
    dep_ratio = entity["dependency_ratio"]
    explanation = get_plain_language_explanation(selected_code)

    table_rows = [
        ("Household Population", format_number(hh_pop)),
        ("Official Total Population", format_number(pop)),
        ("Male Population", f"{format_number(male)} ({male_share:.1f}%)"),
        ("Female Population", f"{format_number(female)} ({female_share:.1f}%)"),
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
    ], className="ref-panel places-profile-panel")
