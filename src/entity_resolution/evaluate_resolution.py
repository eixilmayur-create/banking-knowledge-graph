from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"

OUTPUT_DIR = (
    PROJECT_ROOT /
    "outputs" /
    "entity_resolution"
)


truth = pd.read_csv(
    RAW_DIR /
    "external_customer_ground_truth.csv"
)

predictions = pd.read_csv(
    OUTPUT_DIR /
    "entity_resolution_decisions.csv"
)


evaluation = predictions.merge(
    truth,
    on="external_customer_id",
    how="left"
)


evaluation["correct_match"] = (
    evaluation["crm_customer_id"]
    ==
    evaluation["original_crm_customer_id"]
)


accuracy = (
    evaluation["correct_match"]
    .mean()
    * 100
)


print("=" * 60)
print("ENTITY RESOLUTION EVALUATION")
print("=" * 60)

print(
    f"Matching accuracy: {accuracy:.2f}%"
)

print(
    "\nDecision distribution:"
)

print(
    evaluation[
        "resolution_decision"
    ].value_counts()
)


evaluation.to_csv(
    OUTPUT_DIR /
    "entity_resolution_evaluation.csv",
    index=False
)
