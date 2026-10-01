"""
Data & Definitions Page Layout.
Provides official census definitions, technical notes, provenance metadata,
and links to the Philippine Statistics Authority.
"""
from dash import html
from components.source import render_data_provenance

def render_definitions_page():
    return html.Div([
        render_data_provenance()
    ])
