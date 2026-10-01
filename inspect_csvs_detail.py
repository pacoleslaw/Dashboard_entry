import os
import pandas as pd

data_dir = "data"

f1 = os.path.join(data_dir, "Total Population, Household Population, and Number of Households by Region and Province-Highly Urbanized City- Philippines, 2020.csv")
f2 = os.path.join(data_dir, "Occupied Housing Units, Number of Households, Household Population, by Type of Building and Province-Highly Urbanized City- Philippines, 2020.csv")
f3 = os.path.join(data_dir, "Occupied Housing Units by Type of Building, Number of Floors, and Province-Highly Urbanized City- Philippines, 2020.csv")
f4 = os.path.join(data_dir, "Occupied Housing Units by Floor Area, Number of Occupants in Each Housing Unit and Province-Highly Urbanized City- Philippines, 2020.csv")

print("=== FILE 1: Total, Household Pop, Households ===")
df1 = pd.read_csv(f1, skiprows=1)
print("Columns:", list(df1.columns))
print("Shape:", df1.shape)
print("Head 5:")
print(df1.head(5))

print("\n=== FILE 2: By Type of Building ===")
df2 = pd.read_csv(f2, skiprows=1)
print("Columns:", list(df2.columns))
print("Shape:", df2.shape)
print("Unique Types of Building:", df2["Type of Building"].dropna().unique())
print("Head 10:")
print(df2.head(10))

print("\n=== FILE 4: By Floor Area and Occupants ===")
df4 = pd.read_csv(f4, skiprows=1)
print("Columns:", list(df4.columns))
print("Shape:", df4.shape)
print("Unique Floor Areas (first 10):", df4.iloc[:, 0].dropna().unique()[:10])
print("Head 5:")
print(df4.head(5))
