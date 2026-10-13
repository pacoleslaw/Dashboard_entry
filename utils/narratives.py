"""
Plain Language Narratives and Dynamic Insights Module.
Translates statistical indicators into clear, non-technical explanations
based strictly on official 2020 CPH figures.
"""
from utils.data_loader import get_entity_by_code
from utils.formatting import format_number, format_percentage, format_compact
from utils.calculations import get_ranking

DEFINITIONS = {
    "population": "Population refers to the actual number of individuals enumerated in a given area during the 2020 Census of Population and Housing.",
    "sex_distribution": "Population by sex breaks down the count into biological males and females.",
    "sex_ratio": "Sex ratio indicates how many males there are for every 100 females in the community.",
    "dependency_ratio": "Age dependency ratio measures the balance between young children (under 15) and seniors (65 and older) compared to the working-age population (15 to 64).",
    "population_share": "Share of the population is the proportion of a larger area's total residents living in this specific locality."
}

def get_indicator_definition(key):
    """Return plain-language definition of a demographic term."""
    return DEFINITIONS.get(key, "Official demographic indicator from the Philippine Statistics Authority.")

def get_plain_language_explanation(code):
    """
    Generate an accessible, plain-language summary for the Place Profile.
    Adheres strictly to official PSA data and Press Release Ref No. 2022-322.
    """
    entity = get_entity_by_code(code)
    name = entity["name"]
    level = entity["level"]
    tot_pop = entity.get("total_pop", 0)
    pop_str = format_number(tot_pop)
    hh_pop = entity.get("household_pop", 0) or tot_pop
    hh_str = format_number(hh_pop)
    m_pop = entity.get("hh_male_pop", entity.get("male_pop", 0))
    f_pop = entity.get("hh_female_pop", entity.get("female_pop", 0))
    m_pop_str = format_number(m_pop)
    f_pop_str = format_number(f_pop)
    m_share = entity.get("hh_male_share", entity.get("male_share", 50.6))
    f_share = entity.get("hh_female_share", entity.get("female_share", 49.4))
    sex_ratio = entity.get("hh_sex_ratio", entity.get("sex_ratio", 102.6))
    top_age = entity.get("top_age_group", "5-9")

    if level == "Country":
        return (
            f"As of the May 1, 2020 Census of Population and Housing, the Philippines was home to "
            f"{pop_str} residents, with a household population of {hh_str}. "
            f"Of this household population, {m_pop_str} ({m_share:.1f}%) were male and {f_pop_str} ({f_share:.1f}%) were female, "
            f"yielding an overall sex ratio of {sex_ratio:.1f} males per 100 females. "
            f"The largest single age cohort nationwide was the {top_age} group."
        )
    elif level == "Region":
        rank, total_reg = get_ranking(code, within="national")
        share = format_percentage(entity["nat_share"])
        return (
            f"{name} had an official population of {pop_str} ({hh_str} in private households) in the 2020 Census, accounting for "
            f"{share} of the national population. It ranks #{rank} in population size among the country's "
            f"{total_reg} administrative regions. The household population comprises {m_pop_str} males ({m_share:.1f}%) and "
            f"{f_pop_str} females ({f_share:.1f}%), yielding a sex ratio of {sex_ratio:.1f} males per 100 females."
        )
    else:
        # Province or City
        p_name = entity.get("parent_name", "its region")
        p_share = format_percentage(entity.get("parent_share", 0.0))
        nat_share = format_percentage(entity.get("nat_share", 0.0))
        rank_reg, count_reg = get_ranking(code, within="region")
        return (
            f"{name} had an official count of {pop_str} residents ({hh_str} in private households) in the 2020 Census of Population and Housing. "
            f"This represents {p_share} of {p_name}'s population and {nat_share} of the national total. "
            f"Within {p_name}, it ranks #{rank_reg} among {count_reg} local jurisdictions. "
            f"The household population comprises {m_pop_str} males ({m_share:.1f}%) and {f_pop_str} females ({f_share:.1f}%)."
        )

def get_quick_insights(code):
    """
    Return a list of dynamic factual bullet points for the Quick Insights panel.
    Calculated strictly from actual data.
    """
    entity = get_entity_by_code(code)
    level = entity["level"]
    name = entity["name"]
    pop = entity["total_pop"]
    nat_share = entity["nat_share"]
    m_pct = entity["male_share"]
    f_pct = entity["female_share"]
    work_pct = entity["working_share"]
    young_pct = entity["young_share"]
    elderly_pct = entity["elderly_share"]
    dep_ratio = entity["dependency_ratio"]
    sex_ratio = entity["sex_ratio"]

    insights = []

    # Current view & size
    insights.append(
        f"Selected view: {name} ({level}) with {format_compact(pop)} residents ({format_number(pop)})."
    )

    # Share
    if level == "Country":
        insights.append("Represents 100% of the enumerated national population in the 2020 CPH.")
    elif level == "Region":
        rank, _ = get_ranking(code, within="national")
        insights.append(f"Accounts for {nat_share:.1f}% of the Philippine population (Rank #{rank} among 17 regions).")
    else:
        p_share = entity.get("parent_share", 0.0)
        p_name = entity.get("parent_name", "its region")
        insights.append(f"Accounts for {p_share:.1f}% of {p_name} and {nat_share:.2f}% of the Philippine total.")

    # Sex breakdown
    if m_pct > f_pct:
        insights.append(f"Sex balance: Males comprise {m_pct:.1f}% and females {f_pct:.1f}% ({sex_ratio:.1f} males per 100 females).")
    elif f_pct > m_pct:
        insights.append(f"Sex balance: Females comprise {f_pct:.1f}% and males {m_pct:.1f}% ({sex_ratio:.1f} males per 100 females).")
    else:
        insights.append(f"Sex balance: Exactly equal proportion of males and females (50.0% each).")

    # Age structure
    insights.append(
        f"Age profile: {work_pct:.1f}% of residents are in the working-age bracket (15–64), "
        f"while children under 15 make up {young_pct:.1f}% and seniors (65+) make up {elderly_pct:.1f}%."
    )

    # Dependency
    insights.append(
        f"Dependency burden: {dep_ratio:.1f} dependents for every 100 persons in the working-age population."
    )

    # 2020 CPH Press Release specific cohorts (Reproductive Age, School Age, Seniors 60+)
    f_pop = entity.get("hh_female_pop", entity.get("female_pop", 1)) or 1
    hh_pop = entity.get("household_pop", pop) or pop
    age_both = entity.get("hh_age_both", entity.get("age_both", {}))
    age_female = entity.get("hh_age_female", entity.get("age_female", {}))

    reprod_f = sum(age_female.get(k, 0) for k in ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"])
    reprod_share = (reprod_f / f_pop) * 100 if f_pop > 0 else 51.9

    school_pop = sum(age_both.get(k, 0) for k in ["5-9", "10-14", "15-19", "20-24"])
    school_share = (school_pop / hh_pop) * 100 if hh_pop > 0 else 39.4

    senior_pop = sum(age_both.get(k, 0) for k in ["60-64", "65-69", "70-74", "75-79", "80 years old and over"])
    senior_share = (senior_pop / hh_pop) * 100 if hh_pop > 0 else 8.5

    insights.append(
        f"Special demographic groups: {reprod_share:.1f}% ({format_compact(reprod_f)}) of females are of reproductive age (15–49); "
        f"school-age youth (5–24) comprise {school_share:.1f}% ({format_compact(school_pop)}); "
        f"and senior citizens (60+) make up {senior_share:.1f}% ({format_compact(senior_pop)}) of residents."
    )

    return insights

def get_did_you_know(code):
    """Return an interesting fact tailored to the selected area."""
    entity = get_entity_by_code(code)
    level = entity["level"]
    name = entity["name"]

    if level == "Country":
        return {
            "title": "Did you know?",
            "text": "The Philippines reached an official total population of 109,035,343 as of May 1, 2020, as declared by Proclamation No. 1179. The three largest regions (Region IV-A, NCR, and Region III) together house over 38% of the entire national population."
        }
    elif "NCR" in name or "National Capital" in name:
        return {
            "title": "Did you know?",
            "text": "The National Capital Region (NCR) contains 16 highly urbanized cities and 1 municipality (Pateros), housing nearly 13.5 million residents in less than 0.2% of the country's land area."
        }
    elif "CALABARZON" in name or "IV-A" in name:
        return {
            "title": "Did you know?",
            "text": "CALABARZON (Region IV-A) is the most populous administrative region in the Philippines, with 16.20 million residents, surpassing NCR in total population."
        }
    elif "CAR" in name or "Cordillera" in name:
        return {
            "title": "Did you know?",
            "text": "The Cordillera Administrative Region (CAR) is the country's only landlocked region and has a population of 1.80 million across 6 mountainous provinces and Baguio City."
        }
    elif "Cebu" in name:
        return {
            "title": "Did you know?",
            "text": "Cebu province and its highly urbanized cities (Cebu City, Lapu-Lapu, Mandaue) constitute the major demographic and economic hub of the Visayas island group."
        }
    elif "Davao" in name:
        return {
            "title": "Did you know?",
            "text": "Davao City is the most populous city outside of Luzon, with 1.78 million residents recorded in the 2020 Census."
        }
    elif "Manila" in name:
        return {
            "title": "Did you know?",
            "text": "The City of Manila recorded 1.85 million residents in 2020 and represents the historical capital city of the Republic of the Philippines."
        }
    elif "Quezon City" in name:
        return {
            "title": "Did you know?",
            "text": "Quezon City is the most populous city in the Philippines, with nearly 2.96 million residents in the 2020 Census."
        }
    else:
        top_cohort = entity.get("top_age_group", "20-24")
        return {
            "title": "Did you know?",
            "text": f"In {name}, the largest population cohort is the '{top_cohort}' age group, reflecting the youthful demographic pyramid characteristic of the Philippines."
        }
