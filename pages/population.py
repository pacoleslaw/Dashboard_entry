"""
Population Page Module - combined with Overview.
Re-exports render_overview_page as render_population_page for backward compatibility.
"""
from pages.overview import render_overview_page


def render_population_page(selected_code="PH000000000", indicator="total_pop", map_level="region", manual_nav=False, viewport=None):
    return render_overview_page(selected_code, indicator, map_level, manual_nav, viewport)
