from pathlib import Path
import os

import pandas as pd

from dotenv import load_dotenv
from neo4j import GraphDatabase, Query


# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "neo4j"
)

def require_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required .env setting: {name}")
    return value


driver = GraphDatabase.driver(  # type: ignore[reportUnknownMemberType]
    require_setting("NEO4J_URI"),
    auth=(
        require_setting("NEO4J_USERNAME"),
        require_setting("NEO4J_PASSWORD")
    )
)

database = os.getenv(
    "NEO4J_DATABASE",
    "neo4j"
)

BATCH_SIZE = 500


# ============================================================
# HELPER
# ============================================================

def run_batches(
    dataframe: pd.DataFrame,
    query: Query,
    batch_size: int = BATCH_SIZE,
) -> None:

    total = len(dataframe)

    with driver.session(  # type: ignore[reportUnknownMemberType]
        database=database
    ) as session:

        for start in range(
            0,
            total,
            batch_size
        ):

            batch = dataframe.iloc[
                start:start + batch_size
            ]

            records = batch.where(
                pd.notnull(batch),
                None
            ).to_dict(
                orient="records"
            )

            session.run(
                query,
                rows=records
            )

            print(
                f"Loaded {min(start + batch_size, total)} / {total}"
            )


# ============================================================
# CUSTOMER
# ============================================================

customers = pd.read_csv(
    DATA_DIR / "customers.csv"
)

customer_query = Query("""
UNWIND $rows AS row

MERGE (c:Customer {
    customerId: row.customerId
})

SET
    c.name = row.name,
    c.dateOfBirth = row.dateOfBirth,
    c.email = row.email,
    c.phone = row.phone,
    c.panNumber = row.panNumber,
    c.city = row.city,
    c.state = row.state,
    c.kycStatus = row.kycStatus,
    c.riskSegment = row.riskSegment
""")

print("\nLoading Customers")

run_batches(
    customers,
    customer_query
)


# ============================================================
# ACCOUNTS
# ============================================================

accounts = pd.read_csv(
    DATA_DIR / "accounts.csv"
)

account_query = Query("""
UNWIND $rows AS row

MERGE (a:BankAccount {
    accountId: row.accountId
})

SET
    a.accountType = row.accountType,
    a.accountStatus = row.accountStatus,
    a.balance = toFloat(row.balance),
    a.currency = row.currency,
    a.openDate = row.openDate
""")

print("\nLoading Accounts")

run_batches(
    accounts,
    account_query
)


# ============================================================
# CARDS
# ============================================================

cards = pd.read_csv(
    DATA_DIR / "cards.csv"
)

card_query = Query("""
UNWIND $rows AS row

MERGE (c:Card {
    cardId: row.cardId
})

SET
    c.cardType = row.cardType,
    c.network = row.network,
    c.cardStatus = row.cardStatus,
    c.creditLimit = toFloat(row.creditLimit),
    c.issueDate = row.issueDate
""")

print("\nLoading Cards")

run_batches(
    cards,
    card_query
)


# ============================================================
# LOANS
# ============================================================

loans = pd.read_csv(
    DATA_DIR / "loans.csv"
)

loan_query = Query("""
UNWIND $rows AS row

MERGE (l:Loan {
    loanId: row.loanId
})

SET
    l.loanType = row.loanType,
    l.principal = toFloat(row.principal),
    l.interestRate = toFloat(row.interestRate),
    l.tenureMonths = toInteger(row.tenureMonths),
    l.loanStatus = row.loanStatus,
    l.sanctionDate = row.sanctionDate
""")

print("\nLoading Loans")

run_batches(
    loans,
    loan_query
)


# ============================================================
# TRANSACTIONS
# ============================================================

transactions = pd.read_csv(
    DATA_DIR / "transactions.csv"
)

transaction_query = Query("""
UNWIND $rows AS row

MERGE (t:Transaction {
    transactionId: row.transactionId
})

SET
    t.transactionTimestamp = row.transactionTimestamp,
    t.transactionType = row.transactionType,
    t.direction = row.direction,
    t.amount = toFloat(row.amount),
    t.merchantCategory = row.merchantCategory,
    t.channel = row.channel
""")

print("\nLoading Transactions")

run_batches(
    transactions,
    transaction_query
)


# ============================================================
# BRANCHES
# ============================================================

branches = pd.read_csv(
    DATA_DIR / "branches.csv"
)

branch_query = Query("""
UNWIND $rows AS row

MERGE (b:Branch {
    branchId: row.branchId
})
""")

print("\nLoading Branches")

run_batches(
    branches,
    branch_query
)


driver.close()

print(
    "\nAll Neo4j nodes loaded successfully."
)
