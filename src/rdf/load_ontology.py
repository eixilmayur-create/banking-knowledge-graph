from pathlib import Path
from rdflib import Graph


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ONTOLOGY_FILE = (
    PROJECT_ROOT
    / "ontology"
    / "banking_ontology.ttl"
)


graph = Graph()

graph.parse(
    ONTOLOGY_FILE,
    format="turtle"
)


print("=" * 60)
print("ONTOLOGY LOADED SUCCESSFULLY")
print("=" * 60)

print(
    f"Ontology file: {ONTOLOGY_FILE}"
)

print(
    f"Ontology triples: {len(graph)}"
)
