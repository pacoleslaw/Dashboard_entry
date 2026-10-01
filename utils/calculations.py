"""
Calculation module for analytical metrics, rankings, comparisons, and shares.
"""
from utils.data_loader import load_population_data, get_entity_by_code
from utils.geography import get_regions, get_provinces

def get_top_regions(indicator="total_pop", top_n=5, ascending=False):
    """Return top N regions sorted by specified indicator."""
    regions = get_regions()
    sorted_reg = sorted(regions, key=lambda x: x.get(indicator, 0) or 0, reverse=not ascending)
    return sorted_reg[:top_n]

def get_top_provinces(region_code=None, indicator="total_pop", top_n=5, ascending=False):
    """Return top N provinces/cities sorted by specified indicator."""
    provinces = get_provinces(region_code)
    sorted_prov = sorted(provinces, key=lambda x: x.get(indicator, 0) or 0, reverse=not ascending)
    return sorted_prov[:top_n]

def get_ranking(code, within="national"):
    """
    Get ordinal rank of an entity.
    - If level == 'Region': rank among all 17 regions.
    - If level == 'Province/City':
        - within == 'region': rank within its parent region
        - within == 'national': rank among all 117 provinces/cities.
    """
    entity = get_entity_by_code(code)
    if entity["level"] == "Country":
        return 1, 1

    if entity["level"] == "Region":
        regions = get_regions()
        sorted_reg = sorted(regions, key=lambda x: x["total_pop"], reverse=True)
        for i, r in enumerate(sorted_reg, 1):
            if r["code"] == code:
                return i, len(sorted_reg)
        return 1, len(sorted_reg)

    # Sub-unit
    if within == "region" and entity.get("parent_code"):
        peers = get_provinces(entity["parent_code"])
    else:
        peers = get_provinces()

    sorted_peers = sorted(peers, key=lambda x: x["total_pop"], reverse=True)
    for i, p in enumerate(sorted_peers, 1):
        if p["code"] == code:
            return i, len(sorted_peers)

    return 1, len(sorted_peers)

def compare_two_entities(code_a, code_b):
    """
    Generate side-by-side comparison dict between two geographic entities.
    Does not rank as 'better' or 'worse'; strictly factual.
    """
    ea = get_entity_by_code(code_a)
    eb = get_entity_by_code(code_b)

    diff_pop = ea["total_pop"] - eb["total_pop"]
    diff_pct = round(((ea["total_pop"] - eb["total_pop"]) / eb["total_pop"]) * 100, 1) if eb["total_pop"] > 0 else 0

    return {
        "entity_a": ea,
        "entity_b": eb,
        "pop_difference": abs(diff_pop),
        "pop_diff_signed": diff_pop,
        "pop_diff_pct": diff_pct,
        "larger_entity": ea["name"] if diff_pop > 0 else (eb["name"] if diff_pop < 0 else "Equal"),
        "sex_ratio_diff": round(ea["sex_ratio"] - eb["sex_ratio"], 1),
        "dep_ratio_diff": round(ea["dependency_ratio"] - eb["dependency_ratio"], 1)
    }
