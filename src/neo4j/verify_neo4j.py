from pathlib import Path
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase, Query


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


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


queries: dict[str, Query] = {

    "Customers":
        Query("""
        MATCH (n:Customer)
        RETURN count(n) AS count
        """),

    "Accounts":
        Query("""
        MATCH (n:BankAccount)
        RETURN count(n) AS count
        """),

    "Cards":
        Query("""
        MATCH (n:Card)
        RETURN count(n) AS count
        """),

    "Loans":
        Query("""
        MATCH (n:Loan)
        RETURN count(n) AS count
        """),

    "Transactions":
        Query("""
        MATCH (n:Transaction)
        RETURN count(n) AS count
        """),

    "HOLDS_ACCOUNT":
        Query("""
        MATCH ()-[r:HOLDS_ACCOUNT]->()
        RETURN count(r) AS count
        """),

    "BORROWER_OF":
        Query("""
        MATCH ()-[r:BORROWER_OF]->()
        RETURN count(r) AS count
        """),

    "HAS_CARD":
        Query("""
        MATCH ()-[r:HAS_CARD]->()
        RETURN count(r) AS count
        """),

    "HAS_TRANSACTION":
        Query("""
        MATCH ()-[r:HAS_TRANSACTION]->()
        RETURN count(r) AS count
        """)
}


with driver.session(  # type: ignore[reportUnknownMemberType]
    database=database
) as session:

    print(
        "=" * 60
    )

    print(
        "NEO4J RECONCILIATION"
    )

    print(
        "=" * 60
    )

    for name, query in queries.items():

        record = session.run(
            query
        ).single()

        if record is None:
            raise RuntimeError(f"Query returned no result for {name}.")

        print(
            f"{name}: {record['count']}"
        )


driver.close()
