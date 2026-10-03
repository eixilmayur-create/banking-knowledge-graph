from pathlib import Path
import pandas as pd
from rdflib import Graph


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GRAPH_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "rdf"
    / "banking_knowledge_graph.ttl"
)

QUERY_DIR = (
    PROJECT_ROOT
    / "queries"
    / "sparql"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "validation"
    / "sparql"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD GRAPH
# ============================================================

graph = Graph()

graph.parse(
    GRAPH_FILE,
    format="turtle"
)


print("=" * 70)
print("SPARQL QUALITY CHECKS")
print("=" * 70)

print(
    f"Graph triples: {len(graph)}"
)


# ============================================================
# RUN EVERY .RQ FILE
# ============================================================

summary_rows: list[dict[str, str | int]] = []


query_files = sorted(
    QUERY_DIR.glob("*.rq")
)


for query_file in query_files:

    print("\n" + "-" * 70)

    print(
        f"Running: {query_file.name}"
    )

    query_text = query_file.read_text(
        encoding="utf-8"
    )

    results = graph.query(
        query_text
    )


    # --------------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------------

    columns = [
        str(variable)
        for variable in (results.vars or [])
    ]

    rows: list[list[str | None]] = []

    for result in results:

        if isinstance(result, bool):
            if not columns:
                columns = ["ask_result"]
            rows.append([str(result)])
            continue

        row: list[str | None] = []

        for value in result:
            row.append(str(value))

        rows.append(row)


    df = pd.DataFrame(
        rows,
        columns=columns
    )


    # --------------------------------------------------------
    # SAVE QUERY RESULT
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR
        / f"{query_file.stem}.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )


    print(
        f"Rows returned: {len(df)}"
    )

    print(
        f"Saved: {output_file.name}"
    )


    summary_rows.append(
        {
            "query":
                query_file.name,

            "result_count":
                len(df),

            "output_file":
                output_file.name
        }
    )


# ============================================================
# SAVE SUMMARY
# ============================================================

summary_df = pd.DataFrame(
    summary_rows
)

summary_file = (
    OUTPUT_DIR
    / "sparql_check_summary.csv"
)

summary_df.to_csv(
    summary_file,
    index=False
)


print("\n" + "=" * 70)
print("SPARQL CHECKS COMPLETE")
print("=" * 70)

print(
    f"Queries executed: {len(query_files)}"
)

print(
    f"\nSummary saved to:\n{summary_file}"
)
