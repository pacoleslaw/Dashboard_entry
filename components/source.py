"""
Data Source, Provenance, and Methodology Component.
Documents the official PSA datasets, internal reference codes,
definitions, and technical census notes.
"""
from dash import html
from utils.data_loader import get_dataset_metadata

def render_data_provenance():
    meta = get_dataset_metadata()

    return html.Div([
        # Data Provenance Box
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/info.svg", alt="Source", style={"width": "18px", "height": "18px", "marginRight": "8px"}),
                html.Span("DATA PROVENANCE & CENSUS METADATA", className="panel-title")
            ], className="panel-header"),

            html.Div([
                html.Div([
                    html.Span("DATASET", className="kpi-label"),
                    html.P(meta["title"], style={"fontWeight": "700", "color": "var(--psa-navy)", "fontSize": "0.95rem"}),
                    html.Span("REFERENCE YEAR: ", style={"fontWeight": "600", "fontSize": "0.78rem"}),
                    html.Span(str(meta["reference_year"]), style={"color": "var(--psa-blue)", "fontWeight": "700", "fontSize": "0.78rem"}),
                    html.Br(),
                    html.Span("CENSUS DATE: ", style={"fontWeight": "600", "fontSize": "0.78rem"}),
                    html.Span(meta["census_date"], style={"fontSize": "0.78rem", "color": "var(--text-muted)"}),
                ], style={"flex": "1 1 200px", "minWidth": "200px", "wordBreak": "break-word"}),

                html.Div([
                    html.Span("DATA FILES USED", className="kpi-label"),
                    html.Ul([
                        html.Li("data/2020_CPH_POP_DATA.xlsx (Total Population & Hierarchy)"),
                        html.Li("data/2020_CPH_POP_by_SEX.xlsx (Sex Breakdown)"),
                        html.Li("data/2020_CPH_POP_by_AGE_and_SEX.xlsx (Age & Sex Pyramid)")
                    ], style={"listStyle": "square", "paddingLeft": "18px", "fontSize": "0.78rem", "color": "#334155", "lineHeight": "1.6"}),
                ], style={"flex": "1.2 1 220px", "minWidth": "200px", "wordBreak": "break-word"}),

                html.Div([
                    html.Span("OFFICIAL PSA REPOSITORIES", className="kpi-label"),
                    html.P([
                        html.Strong("Internal Reference Code: "), html.Code(meta["internal_code"], style={"background": "#f1f5f9", "padding": "2px 6px", "borderRadius": "4px"}), html.Br(),
                        html.Strong("Latest Update: "), meta["latest_update"], html.Br(),
                        html.A("PSA Population & Housing Statistics Portal ↗", href=meta["source_url"], target="_blank", rel="noopener noreferrer", style={"color": "var(--psa-blue)", "fontWeight": "600"}), html.Br(),
                        html.A("PSA OpenSTAT Archive (Catalog #231) ↗", href=meta["openstat_url"], target="_blank", rel="noopener noreferrer", style={"color": "var(--psa-blue)", "fontWeight": "600"}), html.Br(),
                        html.A("PSA Age & Sex Distribution Press Release (Ref No. 2022-322) ↗", href="https://psa.gov.ph/system/files/phcd/2022-12/1_Press%2520Release%2520on_Age%2520Sex_RML_18July22_rev_mpe_RRDH_CRD-signed.pdf", target="_blank", rel="noopener noreferrer", style={"color": "var(--psa-blue)", "fontWeight": "600"})
                    ], style={"fontSize": "0.78rem", "lineHeight": "1.6", "wordBreak": "break-word"})
                ], style={"flex": "1.2 1 220px", "minWidth": "200px", "wordBreak": "break-word"}),
            ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "20px"}),

            # Technical Notes
            html.Div([
                html.Div([
                    html.Span("Official PSA Census Notes & Caveats", style={"fontWeight": "700", "fontSize": "0.85rem", "color": "var(--psa-navy)"})
                ], style={"marginBottom": "8px"}),
                html.Ul([
                    html.Li(note) for note in meta["notes"]
                ], style={"fontSize": "0.78rem", "color": "#475569", "paddingLeft": "18px", "lineHeight": "1.5"})
            ], style={"background": "#f8fafc", "border": "1px solid var(--border-color)", "borderRadius": "var(--radius-sm)", "padding": "12px 16px", "marginBottom": "20px"}),

            # Definitions Table
            html.Div([
                html.Div([
                    html.Span("Statistical Indicator Definitions", style={"fontWeight": "700", "fontSize": "0.85rem", "color": "var(--psa-navy)"})
                ], style={"marginBottom": "8px"}),
                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Indicator", style={"width": "25%"}),
                        html.Th("Unit", style={"width": "20%"}),
                        html.Th("Official PSA Definition", style={"width": "55%"})
                    ])),
                    html.Tbody([
                        html.Tr([
                            html.Td(html.Strong(k)),
                            html.Td("Persons" if "Population" in k or "Sex" == k else ("Males per 100 Females" if "Sex Ratio" in k else "Dependents per 100 Working")),
                            html.Td(v)
                        ], style={"backgroundColor": "#f8fafc" if i % 2 == 0 else "#ffffff"})
                        for i, (k, v) in enumerate(meta["definitions"].items())
                    ])
                ], style={"width": "100%", "borderCollapse": "collapse", "fontSize": "0.8rem", "border": "1px solid var(--border-color)"})
            ])
        ], className="panel-card")
    ])
