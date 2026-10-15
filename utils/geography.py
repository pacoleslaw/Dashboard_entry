"""
Geographic Hierarchy Module for Philippine Administrative Divisions.
Handles hierarchy navigation:
Philippines -> Region -> Province/City
"""
import json
import os
import difflib
from utils.data_loader import load_population_data, get_entity_by_code, get_cached_regions, get_cached_provinces

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNDS_FILE = os.path.join(BASE_DIR, "data", "geojson", "geo_bounds.json")
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

HUC_TO_PROVINCE = {
    "City of Baguio": "Benguet",
    "City of Angeles": "Pampanga",
    "City of Olongapo": "Zambales",
    "City of Lucena": "Quezon",
    "City of Puerto Princesa": "Palawan",
    "City of Bacolod": "Negros Occidental",
    "City of Iloilo": "Iloilo",
    "City of Cebu": "Cebu",
    "City of Lapu-Lapu (Opon)": "Cebu",
    "City of Mandaue": "Cebu",
    "City of Tacloban": "Leyte",
    "City of Isabela": "Basilan",
    "City of Zamboanga": "Zamboanga del Sur",
    "City of Cagayan de Oro": "Misamis Oriental",
    "City of Iligan": "Lanao del Norte",
    "City of Davao": "Davao del Sur",
    "City of General Santos (Dadiangas)": "South Cotabato",
    "City of Butuan": "Agusan del Norte"
}

_MUNICITIES_BY_PROVINCE = None

def _get_municities_by_prov_map():
    global _MUNICITIES_BY_PROVINCE
    if _MUNICITIES_BY_PROVINCE is None:
        _MUNICITIES_BY_PROVINCE = {}
        muni_path = os.path.join(BASE_DIR, "data", "geojson", "municities.geojson")
        if os.path.exists(muni_path):
            try:
                with open(muni_path, "r", encoding="utf-8") as f:
                    geo_data = json.load(f)
                for feat in geo_data.get("features", []):
                    props = feat.get("properties", {})
                    if props.get("ENGTYPE_2") == "Waterbody" or props.get("TYPE_2") == "Waterbody":
                        continue
                    p = str(props.get("PROVINCE") or "").strip().lower()
                    m = str(props.get("NAME_2") or "").strip()
                    if p and m:
                        _MUNICITIES_BY_PROVINCE.setdefault(p, set()).add(m)
            except Exception:
                pass
    return _MUNICITIES_BY_PROVINCE

def get_city_municipalities(province_code=None):
    """
    Return city/municipalities for a given province or HUC.
    For NCR (PH130000000), returns its 17 constituent LGUs.
    For provinces, matches from municities.geojson and any associated HUCs.
    """
    if not province_code or province_code == "PH000000000":
        return []

    # NCR
    if province_code == "PH130000000" or province_code.startswith("PH13"):
        return get_provinces("PH130000000")

    pe = get_entity_by_code(province_code)
    if pe.get("level") not in ("Province/City", "City/Municipality"):
        return []

    clean_p = pe["name"].lower().replace(" (western samar)", "").replace(" (north cotabato)", "").replace(" (compostela valley)", "").strip()
    if clean_p == "davao de oro":
        clean_p = "compostela valley"

    all_munis_map = _get_municities_by_prov_map()
    all_entities = load_population_data()

    results = []
    seen = set()
    # Match HUCs in this province
    for huc_name, target_prov in HUC_TO_PROVINCE.items():
        if target_prov.lower() == clean_p:
            huc_ent = next((e for e in all_entities if e["name"] == huc_name), None)
            if huc_ent:
                results.append({
                    "name": f"{huc_ent['name']} (HUC)",
                    "short_name": huc_ent["short_name"],
                    "code": huc_ent["code"],
                    "level": "City/Municipality",
                    "total_pop": huc_ent.get("total_pop", 0)
                })
                seen.add(huc_ent["name"].lower().replace("city of ", "").replace("city", "").strip())

    # Match constituent municipalities from GeoJSON
    raw_munis = all_munis_map.get(clean_p, set())
    for m in sorted(list(raw_munis)):
        clean_m = m.lower().replace("city", "").strip()
        if clean_m not in seen:
            results.append({
                "name": m,
                "short_name": m,
                "code": f"{province_code}_MUNI_{m}",
                "level": "City/Municipality"
            })
            seen.add(clean_m)

    return results

def resolve_geo_hierarchy(code):
    """
    Given any geographic code (country, region, province, HUC, municipality),
    resolves the active hierarchy tuple: (sel_reg, sel_prov, sel_city).
    """
    if not code or code == "PH000000000":
        return "ALL", "ALL", "ALL"

    if "_MUNI_" in code:
        prov_code = code.split("_MUNI_")[0]
        pe = get_entity_by_code(prov_code)
        reg_code = pe.get("parent_code", "ALL")
        return reg_code, prov_code, code

    entity = get_entity_by_code(code)
    lvl = entity.get("level", "Country")

    if lvl == "Country":
        return "ALL", "ALL", "ALL"

    if lvl == "Region":
        return entity["code"], "ALL", "ALL"

    # Province/City level
    parent_reg = entity.get("parent_code", "ALL")

    if parent_reg == "PH130000000" or entity["code"].startswith("PH13"):
        # NCR constituent LGU
        return "PH130000000", "ALL", entity["code"]

    if entity["name"] in HUC_TO_PROVINCE:
        parent_prov_name = HUC_TO_PROVINCE[entity["name"]]
        provinces = get_provinces(parent_reg)
        match_prov = next((p for p in provinces if parent_prov_name.lower() in p["name"].lower()), None)
        prov_code = match_prov["code"] if match_prov else "ALL"
        return parent_reg, prov_code, entity["code"]

    return parent_reg, entity["code"], "ALL"


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
        return [12.2, 122.0], 5, [[4.5, 116.5], [21.5, 127.0]]

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
    return [12.2, 122.0], 5, [[4.5, 116.5], [21.5, 127.0]]

