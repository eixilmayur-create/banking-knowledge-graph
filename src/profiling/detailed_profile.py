from pathlib import Path
import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# SOURCE FILES
# ============================================================

SOURCE_FILES = {
    "CRM_CUSTOMER": "crm_customers.csv",
    "CORE_ACCOUNT": "core_accounts.csv",
    "CARD": "card_accounts.csv",
    "LOAN": "loan_accounts.csv",
    "TRANSACTION": "transactions.csv",
}


# ============================================================
# PROFILE STORAGE
# ============================================================

profile_rows: list[dict[str, object]] = []


# ============================================================
# PROFILE EACH SOURCE
# ============================================================

for source_name, filename in SOURCE_FILES.items():

    file_path = RAW_DATA_DIR / filename

    df = pd.read_csv(file_path)

    print("\n")
    print("=" * 70)
    print(f"SOURCE: {source_name}")
    print("=" * 70)

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nUnique Values:")
    print(df.nunique())

    print("\nDuplicate Rows:")
    print(df.duplicated().sum())

    print("\nSample Records:")
    print(df.head(3))

    # --------------------------------------------------------
    # COLUMN-LEVEL PROFILE
    # --------------------------------------------------------

    for column in df.columns:

        profile_rows.append(
            {
                "source_system": source_name,
                "file_name": filename,
                "column_name": column,
                "data_type": str(df[column].dtype),
                "total_rows": len(df),
                "null_count": int(df[column].isnull().sum()),
                "null_percent": round(
                    df[column].isnull().mean() * 100,
                    2,
                ),
                "unique_values": int(df[column].nunique()),
                "duplicate_values": int(
                    len(df) - df[column].nunique()
                ),
                "sample_value": (
                    str(df[column].dropna().iloc[0])
                    if not df[column].dropna().empty
                    else None
                ),
            }
        )


# ============================================================
# CREATE PROFILE REPORT
# ============================================================

profile_df = pd.DataFrame(profile_rows)

output_file = REPORT_DIR / "source_data_profile.csv"

profile_df.to_csv(
    output_file,
    index=False,
)


print("\n")
print("=" * 70)
print("PROFILE COMPLETE")
print("=" * 70)

print(f"Report saved to: {output_file}")
