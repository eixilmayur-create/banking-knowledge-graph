import os
from typing import Any, LiteralString, cast

from dotenv import load_dotenv
from neo4j import GraphDatabase, Query


load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


NEO4J_URI = get_required_env("NEO4J_URI")
NEO4J_USERNAME = get_required_env("NEO4J_USERNAME")
NEO4J_PASSWORD = get_required_env("NEO4J_PASSWORD")


driver = cast(
    Any,
    GraphDatabase.driver(  # type: ignore[reportCallIssue]
        NEO4J_URI,
        auth=(
            NEO4J_USERNAME,
            NEO4J_PASSWORD,
        ),
    ),
)


database = os.getenv(
    "NEO4J_DATABASE",
    "neo4j",
)


checks = {

    "Customer":
        """
        MATCH (n:Customer)
        RETURN count(n) AS count
        """,

    "BankAccount":
        """
        MATCH (n:BankAccount)
        RETURN count(n) AS count
        """,

    "Card":
        """
        MATCH (n:Card)
        RETURN count(n) AS count
        """,

    "Loan":
        """
        MATCH (n:Loan)
        RETURN count(n) AS count
        """,

    "Transaction":
        """
        MATCH (n:Transaction)
        RETURN count(n) AS count
        """,

    "HOLDS_ACCOUNT":
        """
        MATCH ()-[r:HOLDS_ACCOUNT]->()
        RETURN count(r) AS count
        """,

    "BORROWER_OF":
        """
        MATCH ()-[r:BORROWER_OF]->()
        RETURN count(r) AS count
        """,

    "HAS_CARD":
        """
        MATCH ()-[r:HAS_CARD]->()
        RETURN count(r) AS count
        """,

    "HAS_TRANSACTION":
        """
        MATCH ()-[r:HAS_TRANSACTION]->()
        RETURN count(r) AS count
        """,
}


print(
    "=" * 65
)

print(
    "CLOUD GRAPH RECONCILIATION"
)

print(
    "=" * 65
)


with driver.session(
    database=database
) as session:

    for name, query in checks.items():

        record = session.run(
            Query(cast(LiteralString, query))
        ).single()

        count = record["count"] if record is not None else 0

        print(
            f"{name:<22}"
            f"{count}"
        )


driver.close()
