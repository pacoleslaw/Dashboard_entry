"""
Geographic Hierarchy Module for Philippine Administrative Divisions.
Handles hierarchy navigation:
Philippines -> Region -> Province/City
"""
import json
import os
import difflib
from utils.data_loader import load_population_data, get_entity_by_code, get_cached_regions, get_cached_provinces

# Load precomputed bounds if available
BOUNDS_FILE = "data/geojson/geo_bounds.json"
_GEO_BOUNDS = {}
if os.path.exists(BOUNDS_FILE):
    try:
        with open(BOUNDS_FILE, "r", encoding="utf-8") as f:
            _GEO_BOUNDS = json.load(f)
    except Exception:
        pass

def get_all_entities():
    """Return all 135 geographic entities."""
    return load_population_data()

def get_country():
    """Return the national entity for the Philippines."""
    return get_entity_by_code("PH000000000")

def get_regions():
    """Return list of all 17 Philippine regions (cached O(1))."""
    return get_cached_regions()

def get_provinces(region_code=None):
    """
    Return list of provinces and cities (cached O(1)).
    If region_code is provided, returns children of that region.
    """
    return get_cached_provinces(region_code)

def get_city_municipalities(province_code=None):
    """
    Return city/municipalities if available.
    In the 2020 CPH Provincial/HUC dataset:
    - NCR has 17 LGUs (16 Cities + Pateros).
    - HUCs are reported directly at sub-regional level.
    """
    if province_code and province_code.startswith("PH130000000"):
        return get_provinces(province_code)
    return []

def get_parent_geography(code):
    """Return parent entity for a given geographic code."""
    entity = get_entity_by_code(code)
    if entity.get("parent_code"):
        return get_entity_by_code(entity["parent_code"])
    return None

def get_geographic_level(code):
    """Return 'Country', 'Region', or 'Province/City'."""
    entity = get_entity_by_code(code)
    return entity.get("level", "Country")

def get_geographic_code(name_or_code):
    """Resolve an entity code from a code, exact name, or partial name."""
    if not name_or_code:
        return "PH000000000"
    
    entities = load_population_data()
    # Check if exact code
    for e in entities:
        if e["code"] == name_or_code:
            return e["code"]

    # Check exact name
    clean_target = name_or_code.lower().strip()
    for e in entities:
        if e["name"].lower() == clean_target or e["short_name"].lower() == clean_target:
            return e["code"]

    # Partial / substring match
    for e in entities:
        if clean_target in e["name"].lower() or clean_target in e["short_name"].lower():
            return e["code"]

    # Fuzzy match
    names = [e["name"] for e in entities]
    close = difflib.get_close_matches(name_or_code, names, n=1, cutoff=0.6)
    if close:
        for e in entities:
            if e["name"] == close[0]:
                return e["code"]

    return "PH000000000"

def get_bounds(code):
    """
    Return [center_lat, center_lon, zoom, bounds] for a given geographic code.
    Defaults to full Philippines view if not found.
    Always returns tightly fitted item bounds and optimal zoom.
    """
    if not code or code == "PH000000000":
        return [12.8797, 121.7740], 6, [[4.5, 116.5], [21.5, 127.0]]

    # 1. Direct lookup in bounds table (contains all 17 regions, 82 provinces, and HUCs)
    if code in _GEO_BOUNDS:
        b = _GEO_BOUNDS[code]
        return b["center"], b.get("zoom", 8), b.get("bounds")

    # 2. Check if it's a municipality code (e.g. PH..._MUNI_CityName)
    if "_MUNI_" in code:
        muni_name = code.split("_MUNI_")[-1]
        muni_key = f"MUNI_{muni_name}"
        if muni_key in _GEO_BOUNDS:
            b = _GEO_BOUNDS[muni_key]
            return b["center"], b.get("zoom", 12), b.get("bounds")
        muni_key_low = f"MUNI_{muni_name.lower()}"
        if muni_key_low in _GEO_BOUNDS:
            b = _GEO_BOUNDS[muni_key_low]
            return b["center"], b.get("zoom", 12), b.get("bounds")

    # 3. Explicit check for NCR region
    if code == "PH130000000":
        return [14.5653, 121.0245], 11, [[14.3493, 120.9169], [14.7813, 121.1321]]

    # 4. If it's a sub-unit without its own entry, check its parent region bounds
    entity = get_entity_by_code(code)
    if entity.get("parent_code") and entity["parent_code"] in _GEO_BOUNDS:
        b = _GEO_BOUNDS[entity["parent_code"]]
        return b["center"], b.get("zoom", 8), b.get("bounds")

    # 5. Default Philippines bounds
    return [12.8797, 121.7740], 6, [[4.5, 116.5], [21.5, 127.0]]

