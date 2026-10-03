from pathlib import Path

import pandas as pd

from rdflib import (
    Graph,
    Namespace,
)

from rdflib.namespace import RDF


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "validation"
    / "shacl_validation_report.ttl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "validation"
    / "shacl_violations.csv"
)


SH = Namespace(
    "http://www.w3.org/ns/shacl#"
)


graph = Graph()

graph.parse(
    REPORT_FILE,
    format="turtle"
)


rows: list[dict[str, str | None]] = []


for result in graph.subjects(
    RDF.type,
    SH.ValidationResult
):

    focus_node = graph.value(
        result,
        SH.focusNode
    )

    result_path = graph.value(
        result,
        SH.resultPath
    )

    message = graph.value(
        result,
        SH.resultMessage
    )

    severity = graph.value(
        result,
        SH.resultSeverity
    )

    source_shape = graph.value(
        result,
        SH.sourceShape
    )

    constraint_component = graph.value(
        result,
        SH.sourceConstraintComponent
    )


    rows.append(
        {
            "focus_node":
                str(focus_node)
                if focus_node
                else None,

            "property_path":
                str(result_path)
                if result_path
                else None,

            "message":
                str(message)
                if message
                else None,

            "severity":
                str(severity)
                if severity
                else None,

            "source_shape":
                str(source_shape)
                if source_shape
                else None,

            "constraint_component":
                str(constraint_component)
                if constraint_component
                else None,
        }
    )


df = pd.DataFrame(
    rows
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("=" * 70)
print("SHACL REPORT CONVERTED TO CSV")
print("=" * 70)

print(
    f"Violations found: {len(df)}"
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)
