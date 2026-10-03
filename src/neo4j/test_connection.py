from pathlib import Path
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def require_setting(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required .env setting: {name}")
    return value


NEO4J_URI = require_setting("NEO4J_URI")
NEO4J_USERNAME = require_setting("NEO4J_USERNAME")
NEO4J_PASSWORD = require_setting("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


driver = GraphDatabase.driver(  # type: ignore[reportUnknownMemberType]
    NEO4J_URI,
    auth=(
        NEO4J_USERNAME,
        NEO4J_PASSWORD
    )
)


with driver.session(  # type: ignore[reportUnknownMemberType]
    database=NEO4J_DATABASE
) as session:

    result = session.run(
        "RETURN 'Neo4j connected successfully' AS message"
    )

    record = result.single()
    if record is None:
        raise RuntimeError("The connection test returned no result.")

    print(str(record["message"]))


driver.close()
