from pathlib import Path
from typing import Any
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports"

REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


customers = pd.read_csv(
    PROCESSED_DIR / "customers_clean.csv"
)

accounts = pd.read_csv(
    PROCESSED_DIR / "accounts_clean.csv"
)

cards = pd.read_csv(
    PROCESSED_DIR / "cards_clean.csv"
)

loans = pd.read_csv(
    PROCESSED_DIR / "loans_clean.csv"
)

transactions = pd.read_csv(
    PROCESSED_DIR / "transactions_clean.csv"
)


issues: list[dict[str, Any]] = []


# ============================================================
# CUSTOMER CHECKS
# ============================================================

for _, row in customers.iterrows():

    if pd.isna(row["crm_customer_id"]):

        issues.append({
            "entity": "Customer",
            "entity_id": None,
            "rule": "CUSTOMER_ID_REQUIRED",
            "severity": "ERROR"
        })

    if (
        pd.isna(row["email"])
        and pd.isna(row["phone"])
    ):

        issues.append({
            "entity": "Customer",
            "entity_id": row["crm_customer_id"],
            "rule": "CONTACT_INFORMATION_MISSING",
            "severity": "WARNING"
        })


# ============================================================
# ACCOUNT CHECKS
# ============================================================

valid_customers = set(
    customers["crm_customer_id"]
)

for _, row in accounts.iterrows():

    if row["customer_ref"] not in valid_customers:

        issues.append({
            "entity": "BankAccount",
            "entity_id": row["account_id"],
            "rule": "CUSTOMER_REFERENCE_NOT_FOUND",
            "severity": "ERROR"
        })

    if row["balance_inr"] < 0:

        issues.append({
            "entity": "BankAccount",
            "entity_id": row["account_id"],
            "rule": "NEGATIVE_BALANCE",
            "severity": "WARNING"
        })


# ============================================================
# CARD CHECKS
# ============================================================

valid_accounts = set(
    accounts["account_id"]
)

for _, row in cards.iterrows():

    if row["linked_account_id"] not in valid_accounts:

        issues.append({
            "entity": "Card",
            "entity_id": row["card_id"],
            "rule": "ACCOUNT_REFERENCE_NOT_FOUND",
            "severity": "ERROR"
        })


# ============================================================
# LOAN CHECKS
# ============================================================

for _, row in loans.iterrows():

    if row["borrower_customer_ref"] not in valid_customers:

        issues.append({
            "entity": "Loan",
            "entity_id": row["loan_id"],
            "rule": "BORROWER_REFERENCE_NOT_FOUND",
            "severity": "ERROR"
        })

    if row["principal_inr"] <= 0:

        issues.append({
            "entity": "Loan",
            "entity_id": row["loan_id"],
            "rule": "INVALID_PRINCIPAL",
            "severity": "ERROR"
        })


# ============================================================
# TRANSACTION CHECKS
# ============================================================

for _, row in transactions.iterrows():

    if row["account_id"] not in valid_accounts:

        issues.append({
            "entity": "Transaction",
            "entity_id": row["transaction_id"],
            "rule": "ACCOUNT_REFERENCE_NOT_FOUND",
            "severity": "ERROR"
        })

    if row["amount_inr"] <= 0:

        issues.append({
            "entity": "Transaction",
            "entity_id": row["transaction_id"],
            "rule": "INVALID_TRANSACTION_AMOUNT",
            "severity": "ERROR"
        })


# ============================================================
# CREATE REPORT
# ============================================================

issues_df = pd.DataFrame(
    issues
)

output_file = (
    REPORT_DIR /
    "pre_resolution_quality_issues.csv"
)

issues_df.to_csv(
    output_file,
    index=False
)


print("\n" + "=" * 60)
print("PRE-RESOLUTION QUALITY CHECK COMPLETE")
print("=" * 60)

print(
    f"Total issues found: {len(issues_df)}"
)

if not issues_df.empty:

    print("\nIssue summary:")

    print(
        issues_df.groupby(
            ["rule", "severity"]
        ).size()
    )

print(
    f"\nReport saved to:\n{output_file}"
)
