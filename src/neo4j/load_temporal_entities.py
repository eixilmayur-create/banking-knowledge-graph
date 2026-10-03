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

    with driver.session(  # type: ignore[reportUnknownMemberType]
        database=database
    ) as session:

        for start in range(
            0,
            len(dataframe),
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


# ============================================================
# CONSTRAINT
# ============================================================

with driver.session(  # type: ignore[reportUnknownMemberType]
    database=database
) as session:

    session.run(
        Query("""
        CREATE CONSTRAINT organization_id_unique
        IF NOT EXISTS
        FOR (o:Organization)
        REQUIRE o.organizationId IS UNIQUE
        """)
    )


# ============================================================
# ORGANIZATIONS
# ============================================================

organizations = pd.read_csv(
    DATA_DIR
    / "organizations.csv"
)


run_batches(
    organizations,
    Query("""
    UNWIND $rows AS row

    MERGE (o:Organization {
        organizationId:
            row.organizationId
    })

    SET
        o.name =
            row.organizationName
    """)
)


# ============================================================
# TEMPORAL RELATIONSHIPS
# ============================================================

relationships = pd.read_csv(
    DATA_DIR
    / "rel_customer_organization.csv"
)


run_batches(
    relationships,
    Query("""
    UNWIND $rows AS row

    MATCH (c:Customer {
        customerId:
            row.customerId
    })

    MATCH (o:Organization {
        organizationId:
            row.organizationId
    })

    MERGE
    (c)-[r:ASSOCIATED_WITH {
        role: row.role,
        validFrom: date(row.validFrom)
    }]->(o)

    SET
        r.validTo =
            date(row.validTo),

        r.sourceSystem =
            row.sourceSystem,

        r.confidence =
            toFloat(row.confidence)
    """)
)


driver.close()

print(
    "Temporal entities loaded successfully."
)
