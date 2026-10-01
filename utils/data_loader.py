"""
Data Loader Module for PSA 2020 Census of Population and Housing.
Loads, parses, cleans, and caches data from:
- 2020_CPH_POP_DATA.xlsx
- 2020_CPH_POP_by_SEX.xlsx
- 2020_CPH_POP_by_AGE_and_SEX.xlsx
- Total Population, Household Population, and Number of Households...csv
- Occupied Housing Units, Number of Households... by Type of Building...csv
- Occupied Housing Units by Floor Area, Number of Occupants...csv
"""
import os
import re
import logging
import pandas as pd
from utils.data_validation import validate_files_exist, validate_extracted_entities

logger = logging.getLogger("DataLoader")

# Module-level cache to guarantee files are read only once
_CACHE = {
    "entities": None,
    "entities_by_code": None,
    "metadata": None,
    "regions_list": None,
    "provinces_by_region": None
}

# Standard PSGC Region Codes and Display Names
REGION_MAPPING = {
    "NATIONAL CAPITAL REGION (NCR)": {
        "pcode": "PH130000000",
        "short": "NCR",
        "name": "National Capital Region (NCR)"
    },
    "CORDILLERA ADMINISTRATIVE REGION (CAR)": {
        "pcode": "PH140000000",
        "short": "CAR",
        "name": "Cordillera Administrative Region (CAR)"
    },
    "REGION I (ILOCOS REGION)": {
        "pcode": "PH010000000",
        "short": "Region I",
        "name": "Ilocos Region (Region I)"
    },
    "REGION II (CAGAYAN VALLEY)": {
        "pcode": "PH020000000",
        "short": "Region II",
        "name": "Cagayan Valley (Region II)"
    },
    "REGION III (CENTRAL LUZON)": {
        "pcode": "PH030000000",
        "short": "Region III",
        "name": "Central Luzon (Region III)"
    },
    "REGION IV-A (CALABARZON)": {
        "pcode": "PH040000000",
        "short": "Region IV-A",
        "name": "CALABARZON (Region IV-A)"
    },
    "MIMAROPA REGION": {
        "pcode": "PH170000000",
        "short": "MIMAROPA",
        "name": "MIMAROPA Region"
    },
    "REGION V (BICOL REGION)": {
        "pcode": "PH050000000",
        "short": "Region V",
        "name": "Bicol Region (Region V)"
    },
    "REGION VI (WESTERN VISAYAS)": {
        "pcode": "PH060000000",
        "short": "Region VI",
        "name": "Western Visayas (Region VI)"
    },
    "REGION VII (CENTRAL VISAYAS)": {
        "pcode": "PH070000000",
        "short": "Region VII",
        "name": "Central Visayas (Region VII)"
    },
    "REGION VIII (EASTERN VISAYAS)": {
        "pcode": "PH080000000",
        "short": "Region VIII",
        "name": "Eastern Visayas (Region VIII)"
    },
    "REGION IX (ZAMBOANGA PENINSULA)": {
        "pcode": "PH090000000",
        "short": "Region IX",
        "name": "Zamboanga Peninsula (Region IX)"
    },
    "REGION X (NORTHERN MINDANAO)": {
        "pcode": "PH100000000",
        "short": "Region X",
        "name": "Northern Mindanao (Region X)"
    },
    "REGION XI (DAVAO REGION)": {
        "pcode": "PH110000000",
        "short": "Region XI",
        "name": "Davao Region (Region XI)"
    },
    "REGION XII (SOCCSKSARGEN)": {
        "pcode": "PH120000000",
        "short": "Region XII",
        "name": "SOCCSKSARGEN (Region XII)"
    },
    "REGION XIII (CARAGA)": {
        "pcode": "PH160000000",
        "short": "Region XIII",
        "name": "Caraga (Region XIII)"
    },
    "BANGSAMORO AUTONOMOUS REGION IN MUSLIM MINDANAO (BARMM)": {
        "pcode": "PH150000000",
        "short": "BARMM",
        "name": "BARMM"
    }
}

def clean_name(raw):
    """Clean geographic name by removing footnotes, markers, and leading dots."""
    s = str(raw).strip()
    dots = len(s) - len(s.lstrip('.'))
    clean = s.lstrip('.').strip()
    clean = re.sub(r'\s*\/\w+$', '', clean)  # e.g. /a
    clean = re.sub(r'\s*\*+$', '', clean)    # e.g. *, **, ***
    clean = clean.strip()
    return dots, clean

def _load_and_process():
    """Internal function to parse Excel and CSV sheets and build data model."""
    validate_files_exist()

    f_pop = "data/2020_CPH_POP_DATA.xlsx"
    f_sex = "data/2020_CPH_POP_by_SEX.xlsx"
    f_age = "data/2020_CPH_POP_by_AGE_and_SEX.xlsx"

    logger.info("Reading official PSA Excel files into memory...")
    df_pop = pd.read_excel(f_pop, header=None)
    df_sex = pd.read_excel(f_sex, header=None)
    df_age = pd.read_excel(f_age, header=None)

    # 17 standard age groups in columns 3 to 19 of row 3
    age_groups = [str(df_age.iloc[3, c]).strip() for c in range(3, 20)]

    # Check for supplementary CSV datasets
    f_hh = "data/Total Population, Household Population, and Number of Households by Region and Province-Highly Urbanized City- Philippines, 2020.csv"
    f_bldg = "data/Occupied Housing Units, Number of Households, Household Population, by Type of Building and Province-Highly Urbanized City- Philippines, 2020.csv"
    f_occ = "data/Occupied Housing Units by Floor Area, Number of Occupants in Each Housing Unit and Province-Highly Urbanized City- Philippines, 2020.csv"

    has_hh_data = os.path.exists(f_hh)
    has_bldg_data = os.path.exists(f_bldg)
    has_occ_data = os.path.exists(f_occ)

    if has_hh_data:
        df_hh = pd.read_csv(f_hh, skiprows=1)
    if has_bldg_data:
        df_bldg = pd.read_csv(f_bldg, skiprows=1)
    if has_occ_data:
        df_occ = pd.read_csv(f_occ, skiprows=1)

    entities = []
    current_region = None
    sub_count = 0

    for r in range(4, 139):
        entity_idx = r - 4  # 0 to 134
        raw_name = str(df_pop.iloc[r, 1]).strip()
        dots, c_name = clean_name(raw_name)

        total_pop = int(df_pop.iloc[r, 2])
        male_pop = int(df_sex.iloc[r, 3])
        female_pop = int(df_sex.iloc[r, 4])

        age_both = {age_groups[i]: int(df_age.iloc[r, 3 + i]) for i in range(len(age_groups))}
        age_male = {age_groups[i]: int(df_age.iloc[r, 21 + i]) for i in range(len(age_groups))}
        age_female = {age_groups[i]: int(df_age.iloc[r, 39 + i]) for i in range(len(age_groups))}

        if dots == 0:
            level = "Country"
            code = "PH000000000"
            display_name = "Philippines"
            short_name = "Philippines"
            parent_code = None
            parent_name = None
        elif dots == 2:
            level = "Region"
            sub_count = 0
            reg_info = REGION_MAPPING.get(c_name, {
                "pcode": f"PH_REG_{len(entities)}",
                "short": c_name,
                "name": c_name
            })
            code = reg_info["pcode"]
            display_name = reg_info["name"]
            short_name = reg_info["short"]
            parent_code = "PH000000000"
            parent_name = "Philippines"
            current_region = {
                "name": display_name,
                "short": short_name,
                "code": code
            }
        else:
            level = "Province/City"
            sub_count += 1
            code = f"{current_region['code']}_SUB_{sub_count:02d}"
            display_name = c_name
            short_name = c_name
            parent_code = current_region["code"]
            parent_name = current_region["name"]

        # Calculate demographic metrics
        young_pop = sum(age_both[g] for g in ['Below 5', '5-9', '10-14'])
        working_pop = sum(age_both[g] for g in ['15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64'])
        elderly_pop = sum(age_both[g] for g in ['65-69', '70-74', '75-79', '80 years old and over'])

        dep_ratio = round(((young_pop + elderly_pop) / working_pop) * 100, 1) if working_pop > 0 else 0.0
        sex_ratio = round((male_pop / female_pop) * 100, 1) if female_pop > 0 else 100.0
        top_age_group = max(age_both.items(), key=lambda x: x[1])[0]

        # Extract Household & Housing Data
        total_hh = 0
        hh_pop = 0
        avg_hh_size = 0.0
        housing_units = 0
        housing_types = {
            "Single House": 0,
            "Duplex": 0,
            "Apartment/Condo": 0,
            "Others": 0
        }
        household_sizes = {
            "1 person": 0,
            "2 persons": 0,
            "3 persons": 0,
            "4 persons": 0,
            "5+ persons": 0
        }

        if has_hh_data and entity_idx < len(df_hh):
            row_hh = df_hh.iloc[entity_idx]
            total_hh = int(row_hh["Number of Households"])
            hh_pop = int(row_hh["Household Population"])
            avg_hh_size = round(hh_pop / total_hh, 1) if total_hh > 0 else 0.0

        if has_bldg_data:
            # 10 types of building per entity
            bldg_sub = df_bldg.iloc[entity_idx::135]
            for _, b_row in bldg_sub.iterrows():
                b_type = str(b_row["Type of Building"]).strip()
                u_count = int(b_row["Occupied Housing Units"])
                if b_type == "All Types of Building":
                    housing_units = u_count
                elif b_type == "Single house":
                    housing_types["Single House"] = u_count
                elif b_type == "Duplex":
                    housing_types["Duplex"] = u_count
                elif b_type in ["Apartment/accessoria/rowhouse", "Condominium/condotel"]:
                    housing_types["Apartment/Condo"] += u_count
                else:
                    housing_types["Others"] += u_count

        if has_occ_data:
            # 11 occupant groups per entity
            occ_sub = df_occ.iloc[entity_idx::135]
            for _, o_row in occ_sub.iterrows():
                o_label = str(o_row["Number of Occupants"]).strip()
                o_val = int(o_row["Total"])
                if o_label == "One Occupant":
                    household_sizes["1 person"] = o_val
                elif o_label == "Two Occupants":
                    household_sizes["2 persons"] = o_val
                elif o_label == "Three Occupants":
                    household_sizes["3 persons"] = o_val
                elif o_label == "Four Occupants":
                    household_sizes["4 persons"] = o_val
                elif o_label in ["Five Occupants", "Six Occupants", "Seven Occupants", "Eight Occupants", "Nine Occupants", "Ten Occupants or More"]:
                    household_sizes["5+ persons"] += o_val

        entity = {
            "code": code,
            "raw_name": raw_name,
            "name": display_name,
            "short_name": short_name,
            "level": level,
            "parent_code": parent_code,
            "parent_name": parent_name,
            "total_pop": total_pop,
            "male_pop": male_pop,
            "female_pop": female_pop,
            "male_share": round((male_pop / total_pop) * 100, 1) if total_pop > 0 else 0.0,
            "female_share": round((female_pop / total_pop) * 100, 1) if total_pop > 0 else 0.0,
            "sex_ratio": sex_ratio,
            "young_pop": young_pop,
            "working_pop": working_pop,
            "elderly_pop": elderly_pop,
            "dependency_ratio": dep_ratio,
            "young_share": round((young_pop / total_pop) * 100, 1) if total_pop > 0 else 0.0,
            "working_share": round((working_pop / total_pop) * 100, 1) if total_pop > 0 else 0.0,
            "elderly_share": round((elderly_pop / total_pop) * 100, 1) if total_pop > 0 else 0.0,
            "top_age_group": top_age_group,
            "age_groups": age_groups,
            "age_both": age_both,
            "age_male": age_male,
            "age_female": age_female,
            # Integrated Household & Housing indicators
            "total_households": total_hh,
            "household_pop": hh_pop,
            "avg_household_size": avg_hh_size,
            "housing_units": housing_units,
            "housing_types": housing_types,
            "household_sizes": household_sizes
        }
        entities.append(entity)

    # Compute national share and regional parent share
    nat_pop = entities[0]["total_pop"]
    code_map = {e["code"]: e for e in entities}

    for e in entities:
        e["nat_share"] = round((e["total_pop"] / nat_pop) * 100, 2)
        if e["parent_code"] and e["parent_code"] in code_map:
            p_pop = code_map[e["parent_code"]]["total_pop"]
            e["parent_share"] = round((e["total_pop"] / p_pop) * 100, 2)
        else:
            e["parent_share"] = 100.0

    # Build metadata from file annotations
    metadata = {
        "title": "2020 Census of Population and Housing (2020 CPH)",
        "reference_year": 2020,
        "census_date": "May 1, 2020",
        "source": "Philippine Statistics Authority (PSA)",
        "source_url": "https://psa.gov.ph/statistics/population-and-housing",
        "openstat_url": "https://psada.psa.gov.ph/catalog/231",
        "internal_code": "1A6DPAG0",
        "unit": "Persons / Households / Housing Units",
        "latest_update": "April 15, 2024",
        "notes": [
            "Population counts for provinces exclude counts of Highly Urbanized Cities (HUCs).",
            "City of Isabela is geographically situated in Basilan province but reported under Region IX.",
            "Eight (8) Area Clusters per PSA Board Resolution No. 13 Series of 2021 (BARMM Special Geographic Area).",
            "Philippines national count excludes 2,098 Filipinos in Philippine Embassies, Consulates and Missions Abroad.",
            "Household and Housing tables incorporate 2020 CPH Occupied Housing Units, Number of Households, and Occupant Distribution."
        ],
        "definitions": {
            "Total Population": "Sum of household population and institutional living quarter residents counted on census reference date.",
            "Household Population": "Refers to all persons who are members of private households.",
            "Number of Households": "Social unit consisting of a person or group of persons who sleep in the same housing unit and share common arrangements for preparation and consumption of food.",
            "Average Household Size": "Average number of persons per household (Household Population divided by Number of Households).",
            "Occupied Housing Units": "A separate and independent place of abode intended for habitation, currently occupied by one or more households.",
            "Sex Ratio": "The number of males per 100 females in the population (e.g. 102.9 males per 100 females).",
            "Age Dependency Ratio": "The ratio of persons in dependent age brackets (under 15 and 65+) per 100 working-age persons (15-64)."
        }
    }

    validate_extracted_entities(entities)

    _CACHE["entities"] = entities
    _CACHE["entities_by_code"] = code_map
    _CACHE["metadata"] = metadata
    _CACHE["regions_list"] = [e for e in entities if e["level"] == "Region"]
    _CACHE["provinces_by_region"] = {}
    for r in _CACHE["regions_list"]:
        _CACHE["provinces_by_region"][r["code"]] = [e for e in entities if e["parent_code"] == r["code"]]

    logger.info("Data loader initialization complete. Cached 135 geographic entities with integrated Household and Housing indicators.")

def load_population_data():
    """Return all cached geographic entities."""
    if _CACHE["entities"] is None:
        _load_and_process()
    return _CACHE["entities"]

def get_entity_by_code(code):
    """Lookup entity by geographic code."""
    if _CACHE["entities_by_code"] is None:
        _load_and_process()
    return _CACHE["entities_by_code"].get(code, _CACHE["entities"][0])

def get_dataset_metadata():
    """Return official PSA metadata and provenance information."""
    if _CACHE["metadata"] is None:
        _load_and_process()
    return _CACHE["metadata"]

def load_population_by_sex():
    """Convenience accessor for population by sex."""
    entities = load_population_data()
    return [{
        "code": e["code"],
        "name": e["name"],
        "level": e["level"],
        "total": e["total_pop"],
        "male": e["male_pop"],
        "female": e["female_pop"],
        "sex_ratio": e["sex_ratio"]
    } for e in entities]

def load_population_by_age_sex():
    """Convenience accessor for population by age and sex."""
    entities = load_population_data()
    return [{
        "code": e["code"],
        "name": e["name"],
        "level": e["level"],
        "age_both": e["age_both"],
        "age_male": e["age_male"],
        "age_female": e["age_female"]
    } for e in entities]
