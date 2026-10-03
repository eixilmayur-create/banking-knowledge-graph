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
    / "enriched"
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


def run_batches(
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
                f"Processed "
                f"{min(start + BATCH_SIZE, total)} / {total}"
            )


# ============================================================
# CUSTOMER -> ACCOUNT
# ============================================================

df = pd.read_csv(
    DATA_DIR
    / "rel_customer_account_enriched.csv"
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
(c)-[r:HOLDS_ACCOUNT]->(a)

SET
    r.sourceSystem = row.sourceSystem,
    r.confidence = toFloat(row.confidence),
    r.validFrom = date(row.validFrom),
    r.ingestedAt = datetime(row.ingestedAt),
    r.recordVersion = toInteger(row.recordVersion)
""")

run_batches(
    df,
    query
)


# ============================================================
# CUSTOMER -> LOAN
# ============================================================

df = pd.read_csv(
    DATA_DIR
    / "rel_customer_loan_enriched.csv"
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
(c)-[r:BORROWER_OF]->(l)

SET
    r.sourceSystem = row.sourceSystem,
    r.confidence = toFloat(row.confidence),
    r.validFrom = date(row.validFrom),
    r.ingestedAt = datetime(row.ingestedAt),
    r.recordVersion = toInteger(row.recordVersion)
""")

run_batches(
    df,
    query
)


# ============================================================
# CUSTOMER -> ADDRESS
# ============================================================

df = pd.read_csv(
    DATA_DIR
    / "rel_customer_address_enriched.csv"
)

query = Query("""
UNWIND $rows AS row

MATCH (c:Customer {
    customerId: row.customerId
})

MATCH (a:Address {
    addressId: row.addressId
})

MERGE
(c)-[r:HAS_ADDRESS]->(a)

SET
    r.sourceSystem = row.sourceSystem,
    r.confidence = toFloat(row.confidence),
    r.validFrom = date(row.validFrom),
    r.ingestedAt = datetime(row.ingestedAt),
    r.recordVersion = toInteger(row.recordVersion)
""")

run_batches(
    df,
    query
)


# ============================================================
# CUSTOMER -> BENEFICIARY
# ============================================================

df = pd.read_csv(
    DATA_DIR
    / "rel_customer_beneficiary_enriched.csv"
)

query = Query("""
UNWIND $rows AS row

MATCH (c:Customer {
    customerId: row.customerId
})

MATCH (b:Beneficiary {
    beneficiaryId: row.beneficiaryId
})

MERGE
(c)-[r:HAS_BENEFICIARY]->(b)

SET
    r.sourceSystem = row.sourceSystem,
    r.confidence = toFloat(row.confidence),
    r.validFrom = date(row.validFrom),
    r.ingestedAt = datetime(row.ingestedAt),
    r.recordVersion = toInteger(row.recordVersion)
""")

run_batches(
    df,
    query
)


driver.close()

print(
    "\nEnriched relationships loaded successfully."
)
