from pathlib import Path
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

ER_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "entity_resolution"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "neo4j"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

customers = pd.read_csv(
    ER_DIR / "golden_customers.csv"
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


# ============================================================
# CUSTOMER LOOKUP
# ============================================================

customer_lookup = dict(
    zip(
        customers["crm_customer_id"],
        customers["golden_customer_id"]
    )
)


# ============================================================
# CUSTOMER NODES
# ============================================================

customer_nodes = customers[
    [
        "golden_customer_id",
        "full_name",
        "date_of_birth",
        "email",
        "phone",
        "pan_number",
        "city",
        "state",
        "kyc_status",
        "risk_segment"
    ]
].copy()

customer_nodes.rename(
    columns={
        "golden_customer_id": "customerId",
        "full_name": "name",
        "date_of_birth": "dateOfBirth",
        "pan_number": "panNumber",
        "kyc_status": "kycStatus",
        "risk_segment": "riskSegment"
    },
    inplace=True
)

customer_nodes.to_csv(
    OUTPUT_DIR / "customers.csv",
    index=False
)


# ============================================================
# ACCOUNT NODES
# ============================================================

account_nodes = accounts[
    [
        "account_id",
        "account_type",
        "account_status",
        "balance_inr",
        "currency",
        "open_date"
    ]
].copy()

account_nodes.rename(
    columns={
        "account_id": "accountId",
        "account_type": "accountType",
        "account_status": "accountStatus",
        "balance_inr": "balance",
        "open_date": "openDate"
    },
    inplace=True
)

account_nodes.to_csv(
    OUTPUT_DIR / "accounts.csv",
    index=False
)


# ============================================================
# CARD NODES
# ============================================================

card_nodes = cards[
    [
        "card_id",
        "card_type",
        "network",
        "card_status",
        "credit_limit_inr",
        "issue_date"
    ]
].copy()

card_nodes.rename(
    columns={
        "card_id": "cardId",
        "card_type": "cardType",
        "card_status": "cardStatus",
        "credit_limit_inr": "creditLimit",
        "issue_date": "issueDate"
    },
    inplace=True
)

card_nodes.to_csv(
    OUTPUT_DIR / "cards.csv",
    index=False
)


# ============================================================
# LOAN NODES
# ============================================================

loan_nodes = loans[
    [
        "loan_id",
        "loan_type",
        "principal_inr",
        "interest_rate",
        "tenure_months",
        "loan_status",
        "sanction_date"
    ]
].copy()

loan_nodes.rename(
    columns={
        "loan_id": "loanId",
        "loan_type": "loanType",
        "principal_inr": "principal",
        "interest_rate": "interestRate",
        "tenure_months": "tenureMonths",
        "loan_status": "loanStatus",
        "sanction_date": "sanctionDate"
    },
    inplace=True
)

loan_nodes.to_csv(
    OUTPUT_DIR / "loans.csv",
    index=False
)


# ============================================================
# TRANSACTION NODES
# ============================================================

transaction_nodes = transactions[
    [
        "transaction_id",
        "transaction_ts",
        "transaction_type",
        "direction",
        "amount_inr",
        "merchant_category",
        "channel"
    ]
].copy()

transaction_nodes.rename(
    columns={
        "transaction_id": "transactionId",
        "transaction_ts": "transactionTimestamp",
        "transaction_type": "transactionType",
        "amount_inr": "amount",
        "merchant_category": "merchantCategory"
    },
    inplace=True
)

transaction_nodes.to_csv(
    OUTPUT_DIR / "transactions.csv",
    index=False
)


# ============================================================
# BRANCH NODES
# ============================================================

branch_nodes = pd.DataFrame({
    "branchId":
        sorted(
            accounts["branch_id"]
            .dropna()
            .unique()
        )
})

branch_nodes.to_csv(
    OUTPUT_DIR / "branches.csv",
    index=False
)


# ============================================================
# CUSTOMER -> ACCOUNT
# ============================================================

customer_account = accounts[
    [
        "customer_ref",
        "account_id"
    ]
].copy()

customer_account["customerId"] = (
    customer_account[
        "customer_ref"
    ].map(customer_lookup)
)

customer_account.rename(
    columns={
        "account_id":
            "accountId"
    },
    inplace=True
)

customer_account[
    [
        "customerId",
        "accountId"
    ]
].dropna().to_csv(
    OUTPUT_DIR /
    "rel_customer_account.csv",
    index=False
)


# ============================================================
# CUSTOMER -> LOAN
# ============================================================

customer_loan = loans[
    [
        "borrower_customer_ref",
        "loan_id"
    ]
].copy()

customer_loan["customerId"] = (
    customer_loan[
        "borrower_customer_ref"
    ].map(customer_lookup)
)

customer_loan.rename(
    columns={
        "loan_id":
            "loanId"
    },
    inplace=True
)

customer_loan[
    [
        "customerId",
        "loanId"
    ]
].dropna().to_csv(
    OUTPUT_DIR /
    "rel_customer_loan.csv",
    index=False
)


# ============================================================
# ACCOUNT -> CARD
# ============================================================

account_card = cards[
    [
        "linked_account_id",
        "card_id"
    ]
].copy()

account_card.rename(
    columns={
        "linked_account_id":
            "accountId",

        "card_id":
            "cardId"
    },
    inplace=True
)

account_card.to_csv(
    OUTPUT_DIR /
    "rel_account_card.csv",
    index=False
)


# ============================================================
# ACCOUNT -> TRANSACTION
# ============================================================

account_transaction = transactions[
    [
        "account_id",
        "transaction_id"
    ]
].copy()

account_transaction.rename(
    columns={
        "account_id":
            "accountId",

        "transaction_id":
            "transactionId"
    },
    inplace=True
)

account_transaction.to_csv(
    OUTPUT_DIR /
    "rel_account_transaction.csv",
    index=False
)


# ============================================================
# ACCOUNT -> BRANCH
# ============================================================

account_branch = accounts[
    [
        "account_id",
        "branch_id"
    ]
].copy()

account_branch.rename(
    columns={
        "account_id":
            "accountId",

        "branch_id":
            "branchId"
    },
    inplace=True
)

account_branch.to_csv(
    OUTPUT_DIR /
    "rel_account_branch.csv",
    index=False
)


print("=" * 65)
print("NEO4J DATA PREPARATION COMPLETE")
print("=" * 65)

print(
    f"Output directory:\n{OUTPUT_DIR}"
)
