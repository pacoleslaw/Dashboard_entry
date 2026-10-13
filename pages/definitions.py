"""
Data & Definitions Page Layout.
Provides official census definitions, technical notes, provenance metadata,
and links to the Philippine Statistics Authority.
"""
import functools
from dash import html
from components.source import render_data_provenance

@functools.lru_cache(maxsize=1)
def render_definitions_page():
    return html.Div([
        render_data_provenance()
    ])
