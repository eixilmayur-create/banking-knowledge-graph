from pathlib import Path
from typing import Callable, cast

from rdflib import Graph
from pyshacl import validate as _validate  # type: ignore[reportUnknownVariableType]

validate = cast(
    Callable[..., tuple[bool, object, str]],
    _validate,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_GRAPH_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "rdf"
    / "banking_knowledge_graph.ttl"
)

SHAPES_FILE = (
    PROJECT_ROOT
    / "shapes"
    / "banking_shapes.ttl"
)

ONTOLOGY_FILE = (
    PROJECT_ROOT
    / "ontology"
    / "banking_ontology.ttl"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "validation"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA GRAPH
# ============================================================

data_graph = Graph()

data_graph.parse(
    DATA_GRAPH_FILE,
    format="turtle"
)


# ============================================================
# LOAD SHACL SHAPES
# ============================================================

shapes_graph = Graph()

shapes_graph.parse(
    SHAPES_FILE,
    format="turtle"
)


# ============================================================
# LOAD ONTOLOGY
# ============================================================

ontology_graph = Graph()

ontology_graph.parse(
    ONTOLOGY_FILE,
    format="turtle"
)


# ============================================================
# RUN SHACL
# ============================================================

conforms, results_graph, results_text = validate(

    data_graph=data_graph,

    shacl_graph=shapes_graph,

    ont_graph=ontology_graph,

    inference="rdfs",

    abort_on_first=False,

    allow_infos=True,

    allow_warnings=True,

    meta_shacl=False,

    advanced=True,

    debug=False,
)


# ============================================================
# SAVE REPORT
# ============================================================

report_ttl = (
    OUTPUT_DIR
    / "shacl_validation_report.ttl"
)

if isinstance(results_graph, Graph):
    results_graph.serialize(
        destination=str(report_ttl),
        format="turtle"
    )


report_txt = (
    OUTPUT_DIR
    / "shacl_validation_report.txt"
)

with open(
    report_txt,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        results_text
    )


# ============================================================
# PRINT SUMMARY
# ============================================================

print("=" * 70)
print("SHACL VALIDATION COMPLETE")
print("=" * 70)

print(
    f"\nConforms: {conforms}"
)

print(
    f"\nData graph triples: "
    f"{len(data_graph)}"
)

print(
    f"\nSHACL report saved to:"
    f"\n{report_ttl}"
)

print(
    f"\nReadable report saved to:"
    f"\n{report_txt}"
)

print("\n")
print(results_text)
