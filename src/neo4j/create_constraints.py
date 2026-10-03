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


constraints: list[Query] = [

    Query("""
    CREATE CONSTRAINT customer_id_unique IF NOT EXISTS
    FOR (c:Customer)
    REQUIRE c.customerId IS UNIQUE
    """),

    Query("""
    CREATE CONSTRAINT account_id_unique IF NOT EXISTS
    FOR (a:BankAccount)
    REQUIRE a.accountId IS UNIQUE
    """),

    Query("""
    CREATE CONSTRAINT card_id_unique IF NOT EXISTS
    FOR (c:Card)
    REQUIRE c.cardId IS UNIQUE
    """),

    Query("""
    CREATE CONSTRAINT loan_id_unique IF NOT EXISTS
    FOR (l:Loan)
    REQUIRE l.loanId IS UNIQUE
    """),

    Query("""
    CREATE CONSTRAINT transaction_id_unique IF NOT EXISTS
    FOR (t:Transaction)
    REQUIRE t.transactionId IS UNIQUE
    """),

    Query("""
    CREATE CONSTRAINT branch_id_unique IF NOT EXISTS
    FOR (b:Branch)
    REQUIRE b.branchId IS UNIQUE
    """)
]


with driver.session(  # type: ignore[reportUnknownMemberType]
    database=database
) as session:

    for query in constraints:

        session.run(query)


print(
    "Neo4j constraints created successfully."
)

driver.close()
