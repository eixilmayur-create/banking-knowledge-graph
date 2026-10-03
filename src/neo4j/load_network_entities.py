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
                f"Loaded {min(start + BATCH_SIZE, total)} / {total}"
            )


# ============================================================
# CONSTRAINTS
# ============================================================

with driver.session(  # type: ignore[reportUnknownMemberType]
    database=database
) as session:

    session.run(
        Query("""
        CREATE CONSTRAINT address_id_unique
        IF NOT EXISTS
        FOR (a:Address)
        REQUIRE a.addressId IS UNIQUE
        """)
    )

    session.run(
        Query("""
        CREATE CONSTRAINT beneficiary_id_unique
        IF NOT EXISTS
        FOR (b:Beneficiary)
        REQUIRE b.beneficiaryId IS UNIQUE
        """)
    )


# ============================================================
# ADDRESSES
# ============================================================

addresses = pd.read_csv(
    DATA_DIR / "addresses.csv"
)

run_batches(
    addresses,
    Query("""
    UNWIND $rows AS row

    MERGE (a:Address {
        addressId: row.addressId
    })

    SET
        a.city = row.city,
        a.postalCode = row.postalCode
    """)
)


# ============================================================
# BENEFICIARIES
# ============================================================

beneficiaries = pd.read_csv(
    DATA_DIR / "beneficiaries.csv"
)

run_batches(
    beneficiaries,
    Query("""
    UNWIND $rows AS row

    MERGE (b:Beneficiary {
        beneficiaryId: row.beneficiaryId
    })

    SET
        b.beneficiaryType =
            row.beneficiaryType
    """)
)


# ============================================================
# CUSTOMER -> ADDRESS
# ============================================================

customer_address = pd.read_csv(
    DATA_DIR /
    "rel_customer_address.csv"
)

run_batches(
    customer_address,
    Query("""
    UNWIND $rows AS row

    MATCH (c:Customer {
        customerId: row.customerId
    })

    MATCH (a:Address {
        addressId: row.addressId
    })

    MERGE
    (c)-[:HAS_ADDRESS]->(a)
    """)
)


# ============================================================
# CUSTOMER -> BENEFICIARY
# ============================================================

customer_beneficiary = pd.read_csv(
    DATA_DIR /
    "rel_customer_beneficiary.csv"
)

run_batches(
    customer_beneficiary,
    Query("""
    UNWIND $rows AS row

    MATCH (c:Customer {
        customerId: row.customerId
    })

    MATCH (b:Beneficiary {
        beneficiaryId: row.beneficiaryId
    })

    MERGE
    (c)-[:HAS_BENEFICIARY]->(b)
    """)
)


driver.close()

print(
    "\nNetwork entities loaded successfully."
)
