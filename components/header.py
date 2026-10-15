"""
Header Component reproducing the exact visual layout from the reference image.
"""
from dash import html

def render_header():
    return html.Header([
        html.Div([
            # Left Group: Official PSA Logo Lockup, Divider, Main Titles
            html.Div([
                # Official PSA Seal (Circular Emblem)
                html.Img(
                    src="/assets/psa_seal_clean.png",
                    alt="Philippine Statistics Authority Seal",
                    className="psa-seal-img"
                ),

                # Real HTML Typography (NOT an image!)
                html.Div([
                    html.Div([
                        html.Span("PHILIPPINE", className="psa-text-line1"),
                        html.Span("STATISTICS AUTHORITY", className="psa-text-line2")
                    ], className="psa-text-primary"),
                    html.Div(className="psa-text-divider"),
                    html.Div("Solid • Responsive • World-class", className="psa-text-tagline")
                ], className="psa-official-text-lockup"),

                html.Div(className="ref-header-divider"),

                html.Div([
                    html.H1("Population and Housing Statistics", className="ref-main-title"),
                    html.Div("A Closer Look at the Filipino People", className="ref-subtitle"),
                    html.Div(
                        "Explore key statistics on population, households and housing at the regional, provincial, HUC/ICC, and city/municipal level.",
                        className="ref-desc"
                    )
                ], className="ref-title-group")
            ], className="ref-header-left"),

            # Right Group: "Better Data. Brighter Future." banner illustration
            html.Div([
                html.Img(
                    src="/assets/header_right_illus_clean@2x.png",
                    alt="Better Data. Brighter Future.",
                    className="ref-right-illustration",
                    style={
                        "height": "50px",          # Compact right banner illustration height
                        "width": "auto",
                        "objectFit": "cover",
                        "objectPosition": "right center"
                    }
                )
            ], className="ref-header-right")
        ], className="ref-header-card")
    ])
