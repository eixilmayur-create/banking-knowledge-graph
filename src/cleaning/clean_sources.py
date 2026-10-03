from pathlib import Path
from typing import Any, cast
import pandas as pd
import re


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(value: Any) -> str | None:
    """
    Standardize general text values.
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    # Replace repeated spaces
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_name(value: Any) -> str | None:
    """
    Normalize customer names.
    Example:
    MAYUR   KAMBLE -> Mayur Kamble
    """

    value = normalize_text(value)

    if value is None:
        return None

    return value.title()


def normalize_email(value: Any) -> str | None:
    """
    Email values should be lowercase.
    """

    value = normalize_text(value)

    if value is None:
        return None

    return value.lower()


def normalize_phone(value: Any) -> str | None:
    """
    Keep only digits in phone numbers.
    """

    if pd.isna(value):
        return None

    value = re.sub(
        r"\D",
        "",
        str(value)
    )

    if not value:
        return None

    return value


def normalize_code(value: Any) -> str | None:
    """
    Standardize IDs / codes.
    """

    value = normalize_text(value)

    if value is None:
        return None

    return value.upper()


def normalize_category(value: Any) -> str | None:
    """
    Standardize categorical fields.
    """

    value = normalize_text(value)

    if value is None:
        return None

    return value.upper().replace(" ", "_")


def normalize_date(series: Any) -> pd.Series:
    """
    Convert dates into consistent YYYY-MM-DD format.
    """

    parsed = cast(pd.Series, pd.to_datetime(series, errors="coerce"))
    return parsed.dt.strftime("%Y-%m-%d")


def normalize_datetime(series: Any) -> pd.Series:
    """
    Convert timestamps into ISO-like datetime format.
    """

    parsed = cast(pd.Series, pd.to_datetime(series, errors="coerce"))
    return parsed.dt.strftime("%Y-%m-%dT%H:%M:%S")


# ============================================================
# LOAD SOURCES
# ============================================================

customers = pd.read_csv(
    RAW_DIR / "crm_customers.csv"
)

accounts = pd.read_csv(
    RAW_DIR / "core_accounts.csv"
)

cards = pd.read_csv(
    RAW_DIR / "card_accounts.csv"
)

loans = pd.read_csv(
    RAW_DIR / "loan_accounts.csv"
)

transactions = pd.read_csv(
    RAW_DIR / "transactions.csv"
)


# ============================================================
# 1. CLEAN CUSTOMERS
# ============================================================

customers["crm_customer_id"] = (
    customers["crm_customer_id"]
    .apply(normalize_code)
)

customers["full_name"] = (
    customers["full_name"]
    .apply(normalize_name)
)

customers["email"] = (
    customers["email"]
    .apply(normalize_email)
)

customers["phone"] = (
    customers["phone"]
    .apply(normalize_phone)
)

customers["pan_number"] = (
    customers["pan_number"]
    .apply(normalize_code)
)

customers["city"] = (
    customers["city"]
    .apply(normalize_text)
    .str.title()
)

customers["state"] = (
    customers["state"]
    .apply(normalize_text)
    .str.title()
)

customers["kyc_status"] = (
    customers["kyc_status"]
    .apply(normalize_category)
)

customers["risk_segment"] = (
    customers["risk_segment"]
    .apply(normalize_category)
)

customers["source_system"] = (
    customers["source_system"]
    .apply(normalize_category)
)

customers["date_of_birth"] = normalize_date(
    customers["date_of_birth"]
)


# ============================================================
# 2. CLEAN ACCOUNTS
# ============================================================

accounts["account_id"] = (
    accounts["account_id"]
    .apply(normalize_code)
)

accounts["customer_ref"] = (
    accounts["customer_ref"]
    .apply(normalize_code)
)

accounts["branch_id"] = (
    accounts["branch_id"]
    .apply(normalize_code)
)

accounts["account_type"] = (
    accounts["account_type"]
    .apply(normalize_category)
)

accounts["account_status"] = (
    accounts["account_status"]
    .apply(normalize_category)
)

accounts["currency"] = (
    accounts["currency"]
    .apply(normalize_code)
)

accounts["nominee_flag"] = (
    accounts["nominee_flag"]
    .apply(normalize_code)
)

accounts["source_system"] = (
    accounts["source_system"]
    .apply(normalize_category)
)

accounts["open_date"] = normalize_date(
    accounts["open_date"]
)

accounts["balance_inr"] = pd.to_numeric(
    accounts["balance_inr"],
    errors="coerce"
).round(2)


# ============================================================
# 3. CLEAN CARDS
# ============================================================

cards["card_id"] = (
    cards["card_id"]
    .apply(normalize_code)
)

cards["linked_account_id"] = (
    cards["linked_account_id"]
    .apply(normalize_code)
)

cards["card_type"] = (
    cards["card_type"]
    .apply(normalize_category)
)

cards["network"] = (
    cards["network"]
    .apply(normalize_category)
)

cards["card_status"] = (
    cards["card_status"]
    .apply(normalize_category)
)

cards["source_system"] = (
    cards["source_system"]
    .apply(normalize_category)
)

cards["issue_date"] = normalize_date(
    cards["issue_date"]
)

cards["credit_limit_inr"] = pd.to_numeric(
    cards["credit_limit_inr"],
    errors="coerce"
).round(2)

cards["last4"] = (
    cards["last4"]
    .astype(str)
    .str.zfill(4)
)


# ============================================================
# 4. CLEAN LOANS
# ============================================================

loans["loan_id"] = (
    loans["loan_id"]
    .apply(normalize_code)
)

loans["borrower_customer_ref"] = (
    loans["borrower_customer_ref"]
    .apply(normalize_code)
)

loans["loan_type"] = (
    loans["loan_type"]
    .apply(normalize_category)
)

loans["loan_status"] = (
    loans["loan_status"]
    .apply(normalize_category)
)

loans["source_system"] = (
    loans["source_system"]
    .apply(normalize_category)
)

loans["sanction_date"] = normalize_date(
    loans["sanction_date"]
)

loans["principal_inr"] = pd.to_numeric(
    loans["principal_inr"],
    errors="coerce"
).round(2)

loans["interest_rate"] = pd.to_numeric(
    loans["interest_rate"],
    errors="coerce"
).round(2)

loans["tenure_months"] = pd.to_numeric(
    loans["tenure_months"],
    errors="coerce"
)


# ============================================================
# 5. CLEAN TRANSACTIONS
# ============================================================

transactions["transaction_id"] = (
    transactions["transaction_id"]
    .apply(normalize_code)
)

transactions["account_id"] = (
    transactions["account_id"]
    .apply(normalize_code)
)

transactions["transaction_type"] = (
    transactions["transaction_type"]
    .apply(normalize_category)
)

transactions["direction"] = (
    transactions["direction"]
    .apply(normalize_category)
)

transactions["merchant_category"] = (
    transactions["merchant_category"]
    .apply(normalize_category)
)

transactions["channel"] = (
    transactions["channel"]
    .apply(normalize_category)
)

transactions["source_system"] = (
    transactions["source_system"]
    .apply(normalize_category)
)

transactions["transaction_ts"] = normalize_datetime(
    transactions["transaction_ts"]
)

transactions["amount_inr"] = pd.to_numeric(
    transactions["amount_inr"],
    errors="coerce"
).round(2)


# ============================================================
# REMOVE EXACT DUPLICATE ROWS
# ============================================================

datasets = {
    "customers": customers,
    "accounts": accounts,
    "cards": cards,
    "loans": loans,
    "transactions": transactions,
}

for name, df in datasets.items():

    before = len(df)

    df.drop_duplicates(
        inplace=True
    )

    after = len(df)

    print(
        f"{name}: removed "
        f"{before - after} exact duplicates"
    )


# ============================================================
# SAVE CLEAN FILES
# ============================================================

customers.to_csv(
    PROCESSED_DIR / "customers_clean.csv",
    index=False
)

accounts.to_csv(
    PROCESSED_DIR / "accounts_clean.csv",
    index=False
)

cards.to_csv(
    PROCESSED_DIR / "cards_clean.csv",
    index=False
)

loans.to_csv(
    PROCESSED_DIR / "loans_clean.csv",
    index=False
)

transactions.to_csv(
    PROCESSED_DIR / "transactions_clean.csv",
    index=False
)


# ============================================================
# CREATE CLEANING REPORT
# ============================================================

report_rows: list[dict[str, Any]] = []

for name, df in datasets.items():

    report_rows.append(
        {
            "dataset": name,
            "row_count": len(df),
            "column_count": len(df.columns),
            "total_null_values": int(
                df.isnull().sum().sum()
            ),
            "duplicate_rows": int(
                df.duplicated().sum()
            )
        }
    )

report_df = pd.DataFrame(
    report_rows
)

report_df.to_csv(
    REPORT_DIR / "cleaning_summary.csv",
    index=False
)


print("\n" + "=" * 60)
print("DATA CLEANING COMPLETE")
print("=" * 60)

print(
    f"Processed files saved to:\n"
    f"{PROCESSED_DIR}"
)

print(
    f"\nCleaning report:\n"
    f"{REPORT_DIR / 'cleaning_summary.csv'}"
)
