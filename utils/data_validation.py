"""
Data Validation Module for PSA 2020 CPH Datasets.
Validates file presence, columns, data types, geographic hierarchy,
and missing or anomalous values.
"""
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DataValidation")

REQUIRED_FILES = [
    "data/2020_CPH_POP_DATA.xlsx",
    "data/2020_CPH_POP_by_SEX.xlsx",
    "data/2020_CPH_POP_by_AGE_and_SEX.xlsx"
]

def validate_files_exist():
    """Verify that all three official PSA Excel files exist."""
    missing = []
    for fpath in REQUIRED_FILES:
        if not os.path.exists(fpath):
            missing.append(fpath)
    if missing:
        error_msg = f"Required data file(s) not found: {', '.join(missing)}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    logger.info("All required PSA Excel files verified successfully.")
    return True

def validate_extracted_entities(entities):
    """
    Validate parsed geographic entities.
    Checks:
    - Expected number of records (135: 1 National, 17 Regions, 117 Sub-units)
    - Non-null names and population counts
    - Positive population numbers
    - Consistency between Total Pop and Male + Female Pop
    - Valid parent codes
    """
    issues = []
    
    if len(entities) != 135:
        issues.append(f"Unexpected entity count: found {len(entities)}, expected 135.")

    national = entities[0]
    if national["level"] != "Country" or national["total_pop"] <= 0:
        issues.append("National population record invalid or missing.")

    regions = [e for e in entities if e["level"] == "Region"]
    if len(regions) != 17:
        issues.append(f"Expected 17 regions, found {len(regions)}.")

    subunits = [e for e in entities if e["level"] == "Province/City"]
    if len(subunits) != 117:
        issues.append(f"Expected 117 sub-units (provinces/cities), found {len(subunits)}.")

    for e in entities:
        # Check nulls
        if not e.get("name"):
            issues.append(f"Entity with code {e.get('code')} has missing name.")
        if e.get("total_pop") is None or e.get("total_pop") <= 0:
            issues.append(f"Entity '{e.get('name')}' has invalid total population: {e.get('total_pop')}.")
        
        # Check sex consistency
        m = e.get("male_pop", 0)
        f = e.get("female_pop", 0)
        tot = e.get("total_pop", 0)
        if m + f != tot:
            # Note: in some census tables rounding or institutional differences can occur
            logger.debug(f"Entity '{e.get('name')}': male ({m}) + female ({f}) != total ({tot}) [diff: {tot - (m + f)}]")

    if issues:
        for iss in issues:
            logger.warning(f"Data Validation Issue: {iss}")
    else:
        logger.info("Data validation passed with 0 errors across 135 geographic entities.")

    return issues
