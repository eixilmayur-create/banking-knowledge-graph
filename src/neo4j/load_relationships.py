from pathlib import Path
import os

import pandas as pd

from dotenv import load_dotenv
from neo4j import GraphDatabase, Query


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


def load_relationships(
    dataframe: pd.DataFrame,
    query: Query,
) -> None:

    total = len(dataframe)

    with driver.session(  # type: ignore[reportUnknownMemberType]
        database=database
    ) as session:

        for start in range(
            0,
            total,
            BATCH_SIZE
        ):

            batch = dataframe.iloc[
                start:start + BATCH_SIZE
            ]

            rows = batch.where(
                pd.notnull(batch),
                None
            ).to_dict(
                orient="records"
            )

            session.run(
                query,
                rows=rows
            )

            print(
                f"Loaded {min(start + BATCH_SIZE, total)} / {total}"
            )


# ============================================================
# CUSTOMER -> ACCOUNT
# ============================================================

df = pd.read_csv(
    DATA_DIR /
    "rel_customer_account.csv"
)

query = Query("""
UNWIND $rows AS row

MATCH (c:Customer {
    customerId: row.customerId
})

MATCH (a:BankAccount {
    accountId: row.accountId
})

MERGE
(c)-[:HOLDS_ACCOUNT]->(a)
""")

print(
    "\nLoading CUSTOMER -> ACCOUNT"
)

load_relationships(
    df,
    query
)


# ============================================================
# CUSTOMER -> LOAN
# ============================================================

df = pd.read_csv(
    DATA_DIR /
    "rel_customer_loan.csv"
)

query = Query("""
UNWIND $rows AS row

MATCH (c:Customer {
    customerId: row.customerId
})

MATCH (l:Loan {
    loanId: row.loanId
})

MERGE
(c)-[:BORROWER_OF]->(l)
""")

print(
    "\nLoading CUSTOMER -> LOAN"
)

load_relationships(
    df,
    query
)


# ============================================================
# ACCOUNT -> CARD
# ============================================================

df = pd.read_csv(
    DATA_DIR /
    "rel_account_card.csv"
)

query = Query("""
UNWIND $rows AS row

MATCH (a:BankAccount {
    accountId: row.accountId
})

MATCH (c:Card {
    cardId: row.cardId
})

MERGE
(a)-[:HAS_CARD]->(c)
""")

print(
    "\nLoading ACCOUNT -> CARD"
)

load_relationships(
    df,
    query
)


# ============================================================
# ACCOUNT -> TRANSACTION
# ============================================================

df = pd.read_csv(
    DATA_DIR /
    "rel_account_transaction.csv"
)

query = Query("""
UNWIND $rows AS row

MATCH (a:BankAccount {
    accountId: row.accountId
})

MATCH (t:Transaction {
    transactionId: row.transactionId
})

MERGE
(a)-[:HAS_TRANSACTION]->(t)
""")

print(
    "\nLoading ACCOUNT -> TRANSACTION"
)

load_relationships(
    df,
    query
)


# ============================================================
# ACCOUNT -> BRANCH
# ============================================================

df = pd.read_csv(
    DATA_DIR /
    "rel_account_branch.csv"
)

query = Query("""
UNWIND $rows AS row

MATCH (a:BankAccount {
    accountId: row.accountId
})

MATCH (b:Branch {
    branchId: row.branchId
})

MERGE
(a)-[:MAINTAINED_AT]->(b)
""")

print(
    "\nLoading ACCOUNT -> BRANCH"
)

load_relationships(
    df,
    query
)


driver.close()

print(
    "\nAll relationships loaded successfully."
)
