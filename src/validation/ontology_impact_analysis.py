from pathlib import Path
import argparse

from rdflib import Graph, URIRef


PROJECT_ROOT = Path(__file__).resolve().parents[2]


GRAPH_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "rdf"
    / "banking_knowledge_graph.ttl"
)


parser = argparse.ArgumentParser()

parser.add_argument(
    "--concept",
    required=True,
    help="Full ontology URI to analyze"
)

args = parser.parse_args()


concept = URIRef(
    args.concept
)


graph = Graph()

graph.parse(
    GRAPH_FILE,
    format="turtle"
)


# ============================================================
# USED AS PREDICATE
# ============================================================

predicate_usage = list(
    graph.triples(
        (
            None,
            concept,
            None
        )
    )
)


# ============================================================
# USED AS OBJECT
# ============================================================

object_usage = list(
    graph.triples(
        (
            None,
            None,
            concept
        )
    )
)


# ============================================================
# USED AS SUBJECT
# ============================================================

subject_usage = list(
    graph.triples(
        (
            concept,
            None,
            None
        )
    )
)


print("=" * 70)
print("ONTOLOGY IMPACT ANALYSIS")
print("=" * 70)

print(
    f"Concept:\n{concept}"
)

print(
    f"\nPredicate usage: "
    f"{len(predicate_usage)}"
)

print(
    f"Object usage: "
    f"{len(object_usage)}"
)

print(
    f"Subject usage: "
    f"{len(subject_usage)}"
)

print(
    "\nTotal direct references:",
    (
        len(predicate_usage)
        + len(object_usage)
        + len(subject_usage)
    )
)
