import os
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "graphs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
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


query = """
MATCH (c:Customer)

OPTIONAL MATCH
(c)-[:HOLDS_ACCOUNT]->(a:BankAccount)

OPTIONAL MATCH
(c)-[:BORROWER_OF]->(l:Loan)

OPTIONAL MATCH
(c)-[:HAS_ADDRESS]->(addr:Address)

OPTIONAL MATCH
(c)-[:HAS_BENEFICIARY]->(b:Beneficiary)

WITH
    c,
    count(DISTINCT a) AS accountCount,
    count(DISTINCT l) AS loanCount,
    count(DISTINCT addr) AS addressCount,
    count(DISTINCT b) AS beneficiaryCount

OPTIONAL MATCH
(c)-[r]-()

RETURN
    c.customerId AS customerId,
    accountCount,
    loanCount,
    addressCount,
    beneficiaryCount,
    count(DISTINCT r) AS degree
"""


with driver.session(  # type: ignore[reportUnknownMemberType]
    database=database
) as session:

    result = session.run(
        query
    )

    rows = [
        record.data()
        for record in result
    ]


df = pd.DataFrame(
    rows
)


output_file = (
    OUTPUT_DIR
    / "customer_graph_features.csv"
)


df.to_csv(
    output_file,
    index=False
)


driver.close()


print(
    f"Graph features saved to:\n{output_file}"
)
