from pathlib import Path
import pandas as pd


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ---------------------------------------------------------
# SOURCE FILES
# ---------------------------------------------------------

SOURCE_FILES = {
    "customers": "crm_customers.csv",
    "accounts": "core_accounts.csv",
    "cards": "card_accounts.csv",
    "loans": "loan_accounts.csv",
    "transactions": "transactions.csv",
}


# ---------------------------------------------------------
# LOAD AND PROFILE SOURCES
# ---------------------------------------------------------

total_rows = 0

for source_name, filename in SOURCE_FILES.items():

    file_path = RAW_DATA_DIR / filename

    print("\n" + "=" * 60)
    print(f"SOURCE: {source_name.upper()}")
    print("=" * 60)

    df = pd.read_csv(file_path)

    rows, columns = df.shape

    total_rows += rows

    print(f"File: {filename}")
    print(f"Rows: {rows}")
    print(f"Columns: {columns}")

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Rows:")
    print(df.duplicated().sum())


print("\n" + "=" * 60)
print("TOTAL RECORDS ACROSS ALL SOURCES")
print("=" * 60)

print(total_rows)
