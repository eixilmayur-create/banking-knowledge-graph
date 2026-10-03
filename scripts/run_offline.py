"""Run the local data pipeline without cloud credentials."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STEPS = [
    "cleaning/clean_sources", "entity_resolution/create_external_customer_source",
    "entity_resolution/normalize_entities", "entity_resolution/deterministic_match",
    "entity_resolution/fuzzy_match", "entity_resolution/resolution_decision",
    "entity_resolution/create_golden_customers", "rdf/csv_to_rdf",
    "validation/validate_shacl", "neo4j/prepare_neo4j_data",
]
if __name__ == "__main__":
    for step in STEPS:
        print(f"Running {step}", flush=True)
        subprocess.run([sys.executable, str(ROOT / "src" / (step + ".py"))], cwd=ROOT, check=True)
    print("Pipeline completed. Inspect the SHACL report for conformance and violations.")
