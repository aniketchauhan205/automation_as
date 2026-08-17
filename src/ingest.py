import pandas as pd
from pathlib import Path


DATA_DIR = Path("../data")

files = [
    DATA_DIR / "source1_naukri_applicants.csv",
    DATA_DIR / "source2_gig_workers.csv",
    DATA_DIR / "source3_cbnexus_contacts.csv"
]


for file in files:
    print(f"\nReading: {file}")

    df = pd.read_csv(file)

    print("Rows:", len(df))
    print("Columns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())