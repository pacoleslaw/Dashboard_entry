import os
import pandas as pd

data_dir = "data"
csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

print(f"Found {len(csv_files)} CSV files in data/:\n")

for fname in csv_files:
    fpath = os.path.join(data_dir, fname)
    print("=" * 90)
    print(f"FILE: {fname}")
    print("=" * 90)
    try:
        # Read first few lines
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(8)]
        print("First 8 raw lines:")
        for idx, l in enumerate(lines):
            print(f"  [{idx}]: {l.strip()}")
            
        df = pd.read_csv(fpath, header=None, encoding="utf-8", errors="replace", low_memory=False)
        print(f"\nShape: {df.shape}")
        print("First 5 rows:")
        print(df.iloc[:5, :min(df.shape[1], 8)])
    except Exception as e:
        print(f"Error reading {fname}: {e}")
