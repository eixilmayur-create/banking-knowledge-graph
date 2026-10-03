from typing import Any, LiteralString, cast

from neo4j import GraphDatabase, Query

from src.config.settings import settings


def require_setting(value: str | None, name: str) -> str:
    if value is None or value == "":
        raise RuntimeError(f"Missing required configuration value: {name}")
    return value


NEO4J_URI = require_setting(settings.NEO4J_URI, "NEO4J_URI")
NEO4J_USERNAME = require_setting(settings.NEO4J_USERNAME, "NEO4J_USERNAME")
NEO4J_PASSWORD = require_setting(settings.NEO4J_PASSWORD, "NEO4J_PASSWORD")
NEO4J_DATABASE = settings.NEO4J_DATABASE or "neo4j"


driver = GraphDatabase.driver(  # type: ignore[reportUnknownMemberType]
    NEO4J_URI,
    auth=(
        NEO4J_USERNAME,
        NEO4J_PASSWORD,
    ),
)


def verify_connection() -> None:
    driver.verify_connectivity()  # type: ignore[reportUnknownMemberType]


def execute_query(
    query: str,
    parameters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = parameters or {}
    safe_query = cast(LiteralString, query)

    with driver.session(  # type: ignore[reportUnknownMemberType]
        database=NEO4J_DATABASE,
    ) as session:
        result = session.run(
            Query(safe_query),
            parameters=params,
        )

        return [
            record.data()
            for record in result
        ]


def close_driver() -> None:
    driver.close()
