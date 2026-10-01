"""
Formatting utilities for statistical indicators and plain labels.
"""

INDICATOR_METADATA = {
    "total_pop": {
        "label": "Total Population",
        "unit": "Persons",
        "description": "Total count of residents in the selected area (2020 CPH)."
    },
    "total_households": {
        "label": "Total Households",
        "unit": "Households",
        "description": "Total count of private households in the selected area."
    },
    "avg_household_size": {
        "label": "Average Household Size",
        "unit": "Persons per Household",
        "description": "Average number of persons per household (Household Population / Households)."
    },
    "housing_units": {
        "label": "Occupied Housing Units",
        "unit": "Housing Units",
        "description": "Total number of occupied housing units in the selected area."
    },
    "male_pop": {
        "label": "Male Population",
        "unit": "Persons",
        "description": "Count of male residents in the selected area."
    },
    "female_pop": {
        "label": "Female Population",
        "unit": "Persons",
        "description": "Count of female residents in the selected area."
    },
    "nat_share": {
        "label": "Share of National Population",
        "unit": "Percent (%)",
        "description": "Percentage of total Philippine population residing in this area."
    },
    "sex_ratio": {
        "label": "Sex Ratio",
        "unit": "Males per 100 Females",
        "description": "Number of males per 100 females in the population."
    },
    "dependency_ratio": {
        "label": "Age Dependency Ratio",
        "unit": "Dependents per 100 Working",
        "description": "Number of dependents (ages 0-14 and 65+) per 100 working-age people (ages 15-64)."
    }
}

def format_number(val):
    """Format integer with thousands separator, or 'No data available'."""
    if val is None or val == "":
        return "No data available"
    try:
        return f"{int(val):,}"
    except (ValueError, TypeError):
        return "No data available"

def format_compact(val):
    """Format large numbers compactly (e.g. 109.0M, 1.8M, 450K)."""
    if val is None or val == "":
        return "No data available"
    try:
        n = float(val)
        if abs(n) >= 1_000_000_000:
            return f"{n / 1_000_000_000:.1f}B"
        elif abs(n) >= 1_000_000:
            return f"{n / 1_000_000:.1f}M"
        elif abs(n) >= 1_000:
            return f"{n / 1_000:.1f}K"
        else:
            return f"{int(n)}"
    except (ValueError, TypeError):
        return "No data available"

def format_percentage(val, decimals=1):
    """Format float as percentage string."""
    if val is None or val == "":
        return "No data available"
    try:
        return f"{float(val):.{decimals}f}%"
    except (ValueError, TypeError):
        return "No data available"

def format_sex_ratio(val):
    """Format sex ratio with descriptive suffix."""
    if val is None or val == "":
        return "No data available"
    try:
        return f"{float(val):.1f} males per 100 females"
    except (ValueError, TypeError):
        return "No data available"

def get_indicator_label(key):
    """Return user-friendly label for indicator."""
    return INDICATOR_METADATA.get(key, {}).get("label", key.replace("_", " ").title())

def format_indicator_value(key, val):
    """Format an indicator value appropriately based on its unit."""
    if key in ["total_pop", "male_pop", "female_pop", "young_pop", "working_pop", "elderly_pop", "total_households", "housing_units"]:
        return format_number(val)
    elif key in ["nat_share", "parent_share", "male_share", "female_share", "young_share", "working_share", "elderly_share"]:
        return format_percentage(val)
    elif key == "sex_ratio":
        return format_sex_ratio(val)
    elif key == "avg_household_size":
        return f"{val:.1f} persons" if val is not None else "No data available"
    elif key == "dependency_ratio":
        return f"{val:.1f} per 100 working" if val is not None else "No data available"
    return str(val)
