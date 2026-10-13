# Philippines in Focus: People, Places, and Progress
> *“Explore the Philippines through official statistics.”*

An interactive web dashboard built with Python, Plotly Dash, and Dash Leaflet, transforming official 2020 Census of Population and Housing (2020 CPH) statistics from the Philippine Statistics Authority (PSA) into an intuitive, geographic public information portal.

---

## 1. Project Purpose
The purpose of **Philippines in Focus** is to make official census figures accessible to everyday citizens, researchers, planners, and competition judges without requiring formal statistical training. It directly answers:
1. **Who lives in the Philippines?** (Age distribution, sex breakdown, dependency ratios, population pyramid)
2. **Where do people live?** (Choropleth mapping, regional and provincial rankings, population shares)
3. **How do Filipinos live?** (Household sizes, household population, and housing structures)
4. **What does the population of a selected place look like?** (Place Profiles with plain-language explanations)
5. **How does one place compare with another?** (Side-by-side descriptive comparisons of any two regions or provinces)
6. **How are population and housing characteristics distributed across the country?** (Bi-directional interactive map and linked charts)

---

## 2. Integrated Official PSA Datasets

All datasets in [`data/`](file:///d:/Programming/Dashboard_entry/data) represent official 2020 CPH releases from the Philippine Statistics Authority:

### **A. Primary Excel Workbooks**
1. **`2020_CPH_POP_DATA.xlsx`**:
   - Total population counts, geographic dot hierarchy (`0` = Philippines, `2` = Region, `4` = Province/HUC), and official census notes.
2. **`2020_CPH_POP_by_SEX.xlsx`**:
   - Both Sexes, Male, and Female population across all 135 geographic jurisdictions.
3. **`2020_CPH_POP_by_AGE_and_SEX.xlsx`**:
   - 17 standard age groups (`Below 5` to `80 years and over`) for Both Sexes, Male, and Female cohorts.

### **B. Household & Housing Datasets (CSV)**
4. **`Total Population, Household Population, and Number of Households...csv`**:
   - Total Population (`109,035,343` official / `108,667,043` household pop), and Total Households (`26,393,906`).
   - Computes **Average Household Size** (`4.1` persons nationwide).
5. **`Occupied Housing Units... by Type of Building...csv`**:
   - Total Occupied Housing Units (`25,191,610`) and building structure breakdown:
     - Single House (`22,059,348` / 87.6%)
     - Duplex (`746,765` / 3.0%)
     - Apartment / Accessoria / Condo (`1,797,585` / 7.1%)
     - Others (`587,912` / 2.3%)
6. **`Occupied Housing Units by Floor Area, Number of Occupants...csv`**:
   - Household size distribution: `1 person`, `2 persons`, `3 persons`, `4 persons`, `5+ persons`.
7. **`Occupied Housing Units by Type of Building, Number of Floors...csv`**:
   - Building height characteristics (One floor, Two floors, Three floors, 4+ floors).

---

## 3. Dashboard Themes & Features

- **Executive Header & Branding**:
  - Official PSA Emblem, agency titles, motto (*Solid • Responsive • World-class*), and tagline.
- **Top 4 KPI Cards** (Matching the Official PSA Reference Layout):
  - **Total Population**: `109,035,343` (official count as declared by Proclamation No. 1179)
  - **Total Households**: `26,393,906` (private households)
  - **Average Household Size**: `4.1 persons`
  - **Total Housing Units**: `25,191,610` (occupied housing units)
- **Interactive Multi-Indicator Map (Dash Leaflet)**:
  - Toggle between: *Total Population*, *Total Households*, *Average Household Size*, *Occupied Housing Units*, *Male Population*, *Female Population*, *Sex Ratio*, *Age Dependency Ratio*, and *National Share (%)*.
  - Bi-directional linking: click map to filter charts; click bar chart to fly/zoom map.
- **Visualizations Matching Reference Layout**:
  - **Population by Region / Province** (horizontal bar chart with clickable bars)
  - **Top 5 Areas by Population** (ranked table)
  - **Household Size Distribution** (donut chart with center total)
  - **Type of Housing Units** (donut chart with center total)
  - **Age-Sex Population Pyramid** (Male on left, Female on right across 17 cohorts)
- **Dedicated Statistical Themes (Sidebar)**:
  - **Population**: Executive overview, choropleth map, regional bars, top 5, and household & housing donuts.
  - **Households**: Deep-dive into household population, average size by region, and occupant breakdowns.
  - **Housing**: Occupied housing units and building structure distribution.
  - **Demographics**: Population pyramid and age dependency metrics.
  - **Places & Exploration**: Geographic drill-down and detailed Place Profile.
  - **Compare Places**: Side-by-side descriptive comparison of any two regions or provinces.
  - **Data & Definitions**: Metadata, internal code `1A6DPAG0`, methodology, and live PSA source links.

---

## 4. How to Run

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Run Programmatic Inspection
python inspect_data.py

# 3. Launch the Dashboard
python app.py
```

Access the dashboard at: **`http://127.0.0.1:8050/`**
