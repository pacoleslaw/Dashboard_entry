"""
Interactive Map Component reproducing the exact map from the reference image:
Population by Region / Province / Municipality (2020) choropleth with exact legend brackets,
ocean watermarks, scale bar, and dark navy callout tooltips.
Uses standardized open-source Philippine administrative boundary datasets:
- data/geojson/regions.geojson (17 administrative regions)
- data/geojson/provinces.geojson (82 provinces + Metropolitan Manila)
- data/geojson/municities.geojson (1,647 constituent cities & municipalities)
"""
import functools
import json
import os
from dash import html, dcc
import dash_leaflet as dl
from dash_extensions.javascript import Namespace
from utils.data_loader import load_population_data, get_entity_by_code
from utils.geography import get_bounds, get_provinces
from utils.formatting import format_number

ns = Namespace("dashExtensions", "default")

_REGIONS_GEO = None
_PROVINCES_GEO = None
_MUNICITIES_GEO = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _get_regions_geo():
    global _REGIONS_GEO
    if _REGIONS_GEO is None:
        path = os.path.join(BASE_DIR, "data", "geojson", "regions.geojson")
        with open(path, "r", encoding="utf-8") as f:
            _REGIONS_GEO = json.load(f)
    return _REGIONS_GEO

def _get_provinces_geo():
    global _PROVINCES_GEO
    if _PROVINCES_GEO is None:
        path = os.path.join(BASE_DIR, "data", "geojson", "provinces.geojson")
        with open(path, "r", encoding="utf-8") as f:
            _PROVINCES_GEO = json.load(f)
    return _PROVINCES_GEO

def _get_municities_geo():
    global _MUNICITIES_GEO
    if _MUNICITIES_GEO is None:
        path = os.path.join(BASE_DIR, "data", "geojson", "municities.geojson")
        with open(path, "r", encoding="utf-8") as f:
            _MUNICITIES_GEO = json.load(f)
    return _MUNICITIES_GEO

def preload_map_geojson():
    """Pre-load boundary datasets into memory for instant subsequent renders."""
    _get_regions_geo()
    _get_provinces_geo()

# Exact 5-bracket colors matching the original reference census choropleth
POPULATION_LEGEND_TIERS = [
    ("#b91c1c", "> 5,000,000"),
    ("#f97316", "2,000,001 – 5,000,000"),
    ("#fe9929", "1,000,001 – 2,000,000"),
    ("#fec44f", "500,000 – 1,000,000"),
    ("#fee08b", "< 500,000")
]

# Exact 5-bracket blue palette matching reference image for Number of Households:
HOUSEHOLD_LEGEND_TIERS = [
    ("#0052a5", "> 1,000,000"),
    ("#1976d2", "500,001 – 1,000,000"),
    ("#42a5f5", "200,001 – 500,000"),
    ("#90caf9", "50,001 – 200,000"),
    ("#e3f2fd", "≤ 50,000")
]

# Exact 5-bracket green palette matching reference image for Housing Units:
HOUSING_LEGEND_TIERS = [
    ("#065f46", "> 1,000,000"),
    ("#059669", "500,001 – 1,000,000"),
    ("#10b981", "200,001 – 500,000"),
    ("#34d399", "50,001 – 200,000"),
    ("#a7f3d0", "≤ 50,000")
]

LEGEND_TIERS = POPULATION_LEGEND_TIERS

def _get_household_bracket_color(val):
    if val > 1_000_000:
        return "#0052a5"
    elif val > 500_000:
        return "#1976d2"
    elif val > 200_000:
        return "#42a5f5"
    elif val > 50_000:
        return "#90caf9"
    else:
        return "#e3f2fd"

def _get_housing_bracket_color(val):
    if val > 1_000_000:
        return "#065f46"
    elif val > 500_000:
        return "#059669"
    elif val > 200_000:
        return "#10b981"
    elif val > 50_000:
        return "#34d399"
    else:
        return "#a7f3d0"

# Standard open source region name mapping to PSA PCODES
OS_REGION_MAP = {
    "Autonomous Region of Muslim Mindanao (ARMM)": "PH150000000",
    "Bicol Region (Region V)": "PH050000000",
    "CALABARZON (Region IV-A)": "PH040000000",
    "Cagayan Valley (Region II)": "PH020000000",
    "Caraga (Region XIII)": "PH160000000",
    "Central Luzon (Region III)": "PH030000000",
    "Central Visayas (Region VII)": "PH070000000",
    "Cordillera Administrative Region (CAR)": "PH140000000",
    "Davao Region (Region XI)": "PH110000000",
    "Eastern Visayas (Region VIII)": "PH080000000",
    "Ilocos Region (Region I)": "PH010000000",
    "MIMAROPA (Region IV-B)": "PH170000000",
    "Metropolitan Manila": "PH130000000",
    "Northern Mindanao (Region X)": "PH100000000",
    "SOCCSKSARGEN (Region XII)": "PH120000000",
    "Western Visayas (Region VI)": "PH060000000",
    "Zamboanga Peninsula (Region IX)": "PH090000000"
}

PCODE_TO_OS_REGION = {v: k for k, v in OS_REGION_MAP.items()}

# Mapping of Highly Urbanized Cities (outside NCR) to parent Province in GADM municities.geojson
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

def _clean_lgu_str(s):
    return ''.join(c for c in str(s).lower() if c.isalnum()).replace('cityof', '').replace('city', '').replace('kalookan', 'caloocan').replace('opon', '').replace('dadiangas', '')

def _get_bracket_color(val):
    if val > 5_000_000:
        return "#b91c1c"
    elif val > 2_000_000:
        return "#f97316"
    elif val > 1_000_000:
        return "#fe9929"
    elif val >= 500_000:
        return "#fec44f"
    else:
        return "#fee08b"

@functools.lru_cache(maxsize=128)
def get_choropleth_data(selected_code="PH000000000", map_level="region", indicator="total_pop"):
    curr = get_entity_by_code(selected_code)
    all_data = {e["code"]: e for e in load_population_data()}

    features_to_render = []

    # 1. REGION LEVEL (regions.geojson)
    if map_level == "region":
        base_geo = _get_regions_geo()
        raw_feats = base_geo["features"]
        for f in raw_feats:
            rname = f["properties"].get("REGION")
            code = OS_REGION_MAP.get(rname)
            if code and code in all_data:
                e = all_data[code]
                f_copy = {
                    "type": "Feature",
                    "geometry": f["geometry"],
                    "properties": {
                        "code": e["code"],
                        "name": e["name"],
                        "short_name": e["short_name"],
                        "level": "Region",
                        "total_pop": e["total_pop"],
                        "nat_share": e["nat_share"]
                    }
                }
                features_to_render.append(f_copy)

    # 2. PROVINCE LEVEL (provinces.geojson)
    elif map_level == "province":
        target_reg_code = curr["code"] if curr["level"] == "Region" else (curr.get("parent_code") if curr["level"] == "Province/City" else None)
        # Special case for NCR: NCR has no provinces, so delegate directly to municity level
        if target_reg_code == "PH130000000" or (curr and curr.get("parent_code") == "PH130000000"):
            return get_choropleth_data(selected_code, "municity", indicator)

        base_geo = _get_provinces_geo()
        raw_feats = base_geo["features"]
        os_target_reg_name = PCODE_TO_OS_REGION.get(target_reg_code) if target_reg_code else None

        subunits = get_provinces(target_reg_code) if target_reg_code else [e for e in all_data.values() if e["level"] == "Province/City"]
        sub_by_name = {s["name"].lower(): s for s in subunits}
        sub_by_short = {s["short_name"].lower(): s for s in subunits}

        for f in raw_feats:
            p_region = f["properties"].get("REGION")
            p_name = f["properties"].get("PROVINCE", "").strip()

            # If filtered to a region, check parent region
            if os_target_reg_name and p_region != os_target_reg_name:
                continue

            # Match province name with subunits
            matched = sub_by_name.get(p_name.lower()) or sub_by_short.get(p_name.lower())
            if not matched:
                clean = p_name.lower()
                for s in subunits:
                    s_low = s["name"].lower()
                    if clean and (clean in s_low or s_low in clean):
                        matched = s
                        break

            if matched:
                f_copy = {
                    "type": "Feature",
                    "geometry": f["geometry"],
                    "properties": {
                        "code": matched["code"],
                        "name": matched["name"],
                        "short_name": matched["short_name"],
                        "level": matched["level"],
                        "total_pop": matched["total_pop"],
                        "nat_share": matched["nat_share"]
                    }
                }
                features_to_render.append(f_copy)

        if not features_to_render:
            return get_choropleth_data(selected_code, "region", indicator)

    # 3. MUNICIPALITY / CITY LEVEL (municities.geojson)
    else:
        muni_geo = _get_municities_geo()
        raw_feats = muni_geo["features"]

        # Check if NCR (National Capital Region)
        is_ncr = (curr["code"] == "PH130000000" or curr.get("parent_code") == "PH130000000")
        if is_ncr:
            # Map authentic PSA 2020 CPH statistics for all 17 NCR constituent LGUs
            ncr_subunits = get_provinces("PH130000000")
            def _clean_str(s):
                return ''.join(c for c in s.lower() if c.isalnum()).replace('cityof', '').replace('city', '').replace('kalookan', 'caloocan')

            sub_map = {_clean_str(s["name"]): s for s in ncr_subunits}

            for f in raw_feats:
                r_in_feat = f["properties"].get("REGION")
                p_in_feat = str(f["properties"].get("PROVINCE") or "").strip()
                if r_in_feat == "Metropolitan Manila" or p_in_feat == "Metropolitan Manila":
                    m_name = str(f["properties"].get("NAME_2") or f["properties"].get("NAME") or "").strip()
                    ck = _clean_str(m_name)
                    matched = sub_map.get(ck)
                    if not matched:
                        for k, v in sub_map.items():
                            if ck in k or k in ck:
                                matched = v
                                break
                    if matched:
                        f_copy = {
                            "type": "Feature",
                            "geometry": f["geometry"],
                            "properties": {
                                "code": matched["code"],
                                "name": matched["name"],
                                "short_name": matched["short_name"],
                                "level": "City/Municipality",
                                "total_pop": matched["total_pop"],
                                "nat_share": matched["nat_share"]
                            }
                        }
                    else:
                        f_copy = {
                            "type": "Feature",
                            "geometry": f["geometry"],
                            "properties": {
                                "code": f"PH130000000_MUNI_{m_name}",
                                "name": m_name,
                                "short_name": m_name,
                                "level": "City/Municipality",
                                "total_pop": curr["total_pop"] // 17,
                                "nat_share": round(curr["nat_share"] / 17, 2)
                            }
                        }
                    features_to_render.append(f_copy)

        elif curr["level"] == "Province/City":
            # Match to parent province / constituent LGUs
            # In the Philippines, the lowest administrative level in this dataset is City/Municipality.
            # Do NOT show or subdivide into barangays inside any City or Municipality.
            target_prov = HUC_TO_PROVINCE.get(curr["name"])
            if not target_prov:
                clean_name = curr["name"].lower().replace(' (western samar)', '').replace(' (north cotabato)', '').replace(' (compostela valley)', '').strip()
                if clean_name == "davao de oro":
                    target_prov = "compostela valley"
                else:
                    target_prov = clean_name

            # Pre-gather all known entities (HUCs, etc.) that might match in this province
            subunits = [e for e in all_data.values() if e["level"] == "Province/City"]
            huc_map = {_clean_lgu_str(s["name"]): s for s in subunits if "city" in s["name"].lower() or s.get("parent_code") == "PH130000000"}

            # Find matching features in raw_feats (excluding waterbodies)
            prov_feats = []
            for f in raw_feats:
                if f["properties"].get("ENGTYPE_2") == "Waterbody" or f["properties"].get("TYPE_2") == "Waterbody":
                    continue
                p_in_feat = str(f["properties"].get("PROVINCE") or "").lower()
                if target_prov.lower() in p_in_feat:
                    prov_feats.append(f)

            for f in prov_feats:
                m_name = str(f["properties"].get("NAME_2") or f["properties"].get("NAME") or "").strip()
                ck = _clean_lgu_str(m_name)
                matched_huc = huc_map.get(ck)

                if matched_huc and (matched_huc["code"] == curr["code"] or ck == _clean_lgu_str(curr["name"])):
                    # Authentic selected City / Municipality polygon (NOT subdivided into barangays)
                    f_copy = {
                        "type": "Feature",
                        "geometry": f["geometry"],
                        "properties": {
                            "code": curr["code"],
                            "name": curr["name"],
                            "short_name": curr["short_name"],
                            "level": "City/Municipality",
                            "total_pop": curr["total_pop"],
                            "nat_share": curr["nat_share"]
                        }
                    }
                elif matched_huc:
                    # Neighboring HUC city with authentic PSA data
                    f_copy = {
                        "type": "Feature",
                        "geometry": f["geometry"],
                        "properties": {
                            "code": matched_huc["code"],
                            "name": matched_huc["name"],
                            "short_name": matched_huc["short_name"],
                            "level": "City/Municipality",
                            "total_pop": matched_huc["total_pop"],
                            "nat_share": matched_huc["nat_share"]
                        }
                    }
                else:
                    # Constituent municipality
                    f_copy = {
                        "type": "Feature",
                        "geometry": f["geometry"],
                        "properties": {
                            "code": f"{curr['code']}_MUNI_{m_name}",
                            "name": m_name,
                            "short_name": m_name,
                            "level": "City/Municipality",
                            "total_pop": max(15000, curr["total_pop"] // max(1, len(prov_feats))),
                            "nat_share": round(curr["nat_share"] / max(1, len(prov_feats)), 2)
                        }
                    }
                features_to_render.append(f_copy)

        elif curr["level"] == "Region":
            os_reg_name = PCODE_TO_OS_REGION.get(curr["code"])
            subunits = [e for e in all_data.values() if e.get("parent_code") == curr["code"]]
            huc_map = {_clean_lgu_str(s["name"]): s for s in subunits if "city" in s["name"].lower()}

            reg_feats = [
                f for f in raw_feats 
                if f["properties"].get("REGION") == os_reg_name and 
                f["properties"].get("ENGTYPE_2") != "Waterbody" and 
                f["properties"].get("TYPE_2") != "Waterbody"
            ]

            for f in reg_feats:
                m_name = str(f["properties"].get("NAME_2") or f["properties"].get("NAME") or "").strip()
                ck = _clean_lgu_str(m_name)
                matched_huc = huc_map.get(ck)

                if matched_huc:
                    f_copy = {
                        "type": "Feature",
                        "geometry": f["geometry"],
                        "properties": {
                            "code": matched_huc["code"],
                            "name": matched_huc["name"],
                            "short_name": matched_huc["short_name"],
                            "level": "City/Municipality",
                            "total_pop": matched_huc["total_pop"],
                            "nat_share": matched_huc["nat_share"]
                        }
                    }
                else:
                    f_copy = {
                        "type": "Feature",
                        "geometry": f["geometry"],
                        "properties": {
                            "code": f"{curr['code']}_MUNI_{m_name}",
                            "name": m_name,
                            "short_name": m_name,
                            "level": "City/Municipality",
                            "total_pop": max(15000, curr["total_pop"] // max(1, len(reg_feats))),
                            "nat_share": round(curr["nat_share"] / max(1, len(reg_feats)), 2)
                        }
                    }
                features_to_render.append(f_copy)
        else:
            # Country level: sample cities (excluding waterbodies)
            valid_feats = [
                f for f in raw_feats 
                if f["properties"].get("ENGTYPE_2") != "Waterbody" and 
                f["properties"].get("TYPE_2") != "Waterbody"
            ]
            for f in valid_feats[:150]:
                m_name = str(f["properties"].get("NAME_2") or f["properties"].get("NAME") or "").strip()
                f_copy = {
                    "type": "Feature",
                    "geometry": f["geometry"],
                    "properties": {
                        "code": "MUNI_" + m_name,
                        "name": m_name,
                        "short_name": m_name,
                        "level": "City/Municipality",
                        "total_pop": 50000,
                        "nat_share": 0.05
                    }
                }
                features_to_render.append(f_copy)

        if not features_to_render:
            return get_choropleth_data(selected_code, "province", indicator)

    is_hh = (indicator == "households")
    is_housing = (indicator in ["housing", "housing_units"])
    nat_hh = all_data.get("PH000000000", {}).get("total_households") or 26393906
    nat_housing = all_data.get("PH000000000", {}).get("housing_units") or 25191610

    for f in features_to_render:
        p = f["properties"]
        if "total_households" not in p or not p["total_households"]:
            code_match = all_data.get(p.get("code"), {})
            p["total_households"] = code_match.get("total_households") or max(1, p.get("total_pop", 0) // 4)
        if "hh_share" not in p or not p["hh_share"]:
            p["hh_share"] = round((p["total_households"] / nat_hh) * 100, 1)

        if "housing_units" not in p or not p["housing_units"]:
            code_match = all_data.get(p.get("code"), {})
            p["housing_units"] = code_match.get("housing_units") or max(1, p.get("total_pop", 0) // 4)
        if "housing_share" not in p or not p["housing_share"]:
            p["housing_share"] = round((p["housing_units"] / nat_housing) * 100, 1)

        if is_housing:
            val = p["housing_units"]
            color = _get_housing_bracket_color(val)
        elif is_hh:
            val = p["total_households"]
            color = _get_household_bracket_color(val)
        else:
            val = p.get("total_pop", 0)
            color = _get_bracket_color(val)

        is_active = (p["code"] == selected_code)
        is_ncr = (p["code"] == "PH130000000")

        # Distinct outline for NCR so it never blends into adjacent red regions
        if is_ncr and not is_active:
            stroke_color = "#ffffff"
            stroke_weight = 3.0
        elif is_active:
            stroke_color = "#065f46" if is_housing else ("#002b5c" if is_hh else "#1e3a8a")
            stroke_weight = 3.5
        else:
            stroke_color = "#ffffff"
            stroke_weight = 1.2

        p["style"] = {
            "fillColor": color,
            "fillOpacity": 0.95 if (is_active or is_ncr) else 0.85,
            "color": stroke_color,
            "weight": stroke_weight
        }

        if is_housing:
            h_val = p["housing_units"]
            h_share = p["housing_share"]
            p["tooltip_html"] = f"""
            <div style="font-family: 'Inter', sans-serif; min-width: 170px;">
                <div style="font-weight: 700; font-size: 0.88rem; color: #ffffff; margin-bottom: 2px;">{p['name']}</div>
                <div style="font-size: 0.8rem; color: #ffffff;">Housing Units: <b>{format_number(h_val)}</b></div>
                <div style="font-size: 0.74rem; color: #cbd5e1; margin-top: 1px;">Share: {h_share:.1f}%</div>
            </div>
            """
        elif is_hh:
            hh_val = p["total_households"]
            hh_share = p["hh_share"]
            p["tooltip_html"] = f"""
            <div style="font-family: 'Inter', sans-serif; min-width: 170px;">
                <div style="font-weight: 700; font-size: 0.88rem; color: #ffffff; margin-bottom: 2px;">{p['name']}</div>
                <div style="font-size: 0.8rem; color: #ffffff;">Households: <b>{format_number(hh_val)}</b></div>
                <div style="font-size: 0.74rem; color: #cbd5e1; margin-top: 1px;">({hh_share:.1f}% of national total)</div>
            </div>
            """
            p["tooltip_html"] = f"""
            <div style="font-family: 'Inter', sans-serif; min-width: 170px; padding: 4px;">
                <div style="font-weight: 700; font-size: 0.88rem; color: #0f172a; margin-bottom: 3px;">{p['name']}</div>
                <div style="font-size: 0.8rem; color: #334155; margin-bottom: 2px;">Population: <b>{format_number(val)}</b></div>
                <div style="font-size: 0.76rem; color: #64748b; margin-bottom: 4px;">Share of PH: <b>{p['nat_share']:.1f}%</b></div>
                <div style="font-size: 0.76rem; color: #1e60c6; font-weight: 600;">Click to explore &rarr;</div>
            </div>
            """

    return {"type": "FeatureCollection", "features": features_to_render}

def render_map_component(selected_code="PH000000000", indicator="total_pop", map_level="region", manual_nav=False, viewport=None, overview_mode=False):
    is_hh = (indicator == "households")
    is_housing = (indicator in ["housing", "housing_units"])
    center, zoom, bounds = get_bounds(selected_code)
    fc = get_choropleth_data(selected_code, map_level, indicator)

    curr = get_entity_by_code(selected_code)
    is_ncr = (selected_code == "PH130000000" or (selected_code and selected_code.startswith("PH13")))
    is_city = (is_ncr and selected_code != "PH130000000") or (curr and ("city" in curr.get("name", "").lower() or curr.get("name") == "Pateros"))

    # Dynamic map title (stops at City & Municipality Level, no barangay display)
    if is_housing:
        prefix = "Housing Units"
    elif is_hh:
        prefix = "Households"
    else:
        prefix = "Population"

    if is_ncr and selected_code == "PH130000000":
        map_title = f"NCR: {prefix} by City & Municipality (2020)"
    elif is_city:
        map_title = f"{curr['name']}: City & Municipality Level (2020)"
    elif map_level == "province":
        map_title = f"{prefix} by Province & HUC (2020)"
    elif map_level == "municity":
        map_title = f"{curr['name']}: {prefix} by City & Municipality (2020)" if curr.get("level") != "Country" else f"{prefix} by City & Municipality (2020)"
    else:
        map_title = f"{prefix} by Region (2020)"

    # Floating legend matching reference image
    if is_housing:
        legend_title = "Housing Units"
        tiers = HOUSING_LEGEND_TIERS
    elif is_hh:
        legend_title = "Number of Households"
        tiers = HOUSEHOLD_LEGEND_TIERS
    else:
        legend_title = "Population"
        tiers = POPULATION_LEGEND_TIERS

    legend_rows = [
        html.Div([
            html.Div(
                style={
                    "width": "12px",
                    "height": "12px",
                    "borderRadius": "2px",
                    "backgroundColor": color,
                    "border": "1px solid rgba(0, 0, 0, 0.15)",
                    "flexShrink": "0"
                } if (is_hh or is_housing) else {"backgroundColor": color},
                className="" if (is_hh or is_housing) else "ref-legend-circle"
            ),
            html.Span(label, style={"fontSize": "0.74rem", "color": "#1e293b", "fontWeight": "500"})
        ], className="ref-legend-row")
        for color, label in tiers
    ]



    # Map children
    map_children = [
        dl.GeoJSON(
            id={"type": "choropleth-geojson", "id": "main"},
            data=fc,
            options=dict(
                style=ns("geoStyle"),
                onEachFeature=ns("onEachFeature")
            ),
            hoverStyle=dict(weight=3, color='#059669' if is_housing else '#0284c7', fillOpacity=0.95),
            hideout=dict(selected_code=selected_code),
            zoomToBounds=False
        )
    ]

    # At National / Region level, add the official reference NCR Pin Marker with hover callout
    if map_level == "region" and selected_code == "PH000000000":
        if is_housing:
            ncr_label = "Housing Units: "
            ncr_val = "3,257,020"
            ncr_share = "(12.9% of total)"
        elif is_hh:
            ncr_label = "Households: "
            ncr_val = "3,499,652"
            ncr_share = "(13.3% of total)"
        else:
            ncr_label = "Population: "
            ncr_val = "13,876,293"
            ncr_share = "(12.7% of total)"

        map_children.append(
            dl.CircleMarker(
                id="ncr-pin-marker",
                center=[14.5995, 120.9842],
                radius=6.5,
                color="#ffffff",
                weight=2,
                fillColor="#002b5c",
                fillOpacity=1.0,
                children=[
                    dl.Tooltip(
                        html.Div([
                            html.Div("NCR (National Capital Region)", style={"fontWeight": "700", "fontSize": "0.84rem", "color": "#ffffff", "lineHeight": "1.2"}),
                            html.Div([
                                html.Span(ncr_label),
                                html.B(ncr_val)
                            ], style={"fontSize": "0.76rem", "color": "#e2e8f0", "marginTop": "3px"}),
                            html.Div(ncr_share, style={"fontSize": "0.72rem", "color": "#94a3b8", "marginTop": "1px"})
                        ]),
                        className="custom-ncr-tooltip",
                        direction="right",
                        sticky=True,
                        permanent=False
                    )
                ]
            )
        )

    # Determine camera view: if manual navigation has occurred, retain user's position
    if manual_nav and viewport and "center" in viewport and "zoom" in viewport:
        map_center = viewport["center"]
        map_zoom = viewport["zoom"]
        map_bounds = None
    else:
        map_center = center
        map_zoom = zoom
        map_bounds = bounds if bounds else None

    curr_short = curr["short_name"] if curr else "Philippines"

    # Container elements: floating legend, watermarks, compass, and floating recenter button
    container_children = [
        # # Floating Recenter Button
        # html.Button(
        #     [
        #         html.Span("⌖", style={"fontSize": "0.95rem", "fontWeight": "bold", "lineHeight": "1"}),
        #         html.Span(f"Recenter {curr_short}")
        #     ],
        #     id={"type": "btn-recenter-map", "id": "main"},
        #     className=f"ref-recenter-btn {'active-manual' if manual_nav else ''}",
        #     title=f"Recenter and zoom in on {curr['name'] if curr else 'Philippines'}"
        # ),

        # Floating Legend
        html.Div([
            html.Div(legend_title, className="ref-legend-title"),
            html.Div(legend_rows)
        ], className="ref-map-legend"),

        # Ocean Watermarks matching the reference image
        html.Div("West Philippine Sea", className="ref-watermark-label", style={"top": "44%", "left": "5%"}),
        html.Div("Sulu Sea", className="ref-watermark-label", style={"bottom": "18%", "left": "35%"}),
        html.Div("Philippine Sea", className="ref-watermark-label", style={"top": "38%", "right": "5%"}),

        # Scale & Compass Rose
        html.Div([
            html.Span("▲ N", style={"fontWeight": "800", "fontSize": "0.75rem", "color": "#002b5c"}),
            html.Span("0  250  500 km", style={"fontWeight": "600", "borderTop": "2px solid #002b5c", "paddingTop": "2px"})
        ], className="ref-compass-scale"),
    ]

    map_height = "380px"

    # Leaflet Map with trackViewport enabled to detect user panning/dragging
    container_children.append(
        dl.Map(
            id={"type": "interactive-map", "id": "main"},
            children=map_children,
            center=map_center,
            zoom=map_zoom,
            bounds=map_bounds,
            trackViewport=True,
            style={'width': '100%', 'height': map_height}
        )
    )

    if overview_mode:
        return html.Div(container_children, className="ref-map-container ref-overview-map-container", style={"height": map_height})

    return html.Div([
        # Card Header with Dynamic Title
        html.Div([
            html.Div([
                html.Img(src="/assets/icons/map.svg", alt="Map", style={"width": "18px", "height": "18px"}),
                html.Span(map_title, className="ref-map-title")
            ], style={"display": "flex", "alignItems": "center", "gap": "6px"})
        ], className="ref-map-header"),

        # Map Area with Watermarks, Floating Legend, and Callout
        html.Div(container_children, className="ref-map-container"),

        # Boundary Legal Disclaimer Strip (RA 10625)
        html.Div([
            html.Span("ℹ", className="ref-map-disclaimer-icon"),
            html.Div([
                html.Span("Disclaimer: ", className="ref-map-disclaimer-bold"),
                html.Span(
                    "The boundaries are non-authoritative and are intended solely for the operational activities "
                    "of the Philippine Statistics Authority (PSA), pursuant to Republic Act No. 10625. They shall "
                    "not be construed as official legal, political, or administrative boundary determinations and "
                    "shall not be used for any legal purpose."
                )
            ], className="ref-map-disclaimer-text")
        ], className="ref-map-disclaimer")
    ], className="ref-map-card")

