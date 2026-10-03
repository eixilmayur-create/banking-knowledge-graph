from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


INPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "hybrid_mapping_results.csv"
)


df = pd.read_csv(
    INPUT_FILE
)


total = len(df)


auto_approved = len(
    df[
        df["routing_decision"]
        == "AUTO_APPROVE"
    ]
)


review_required = len(
    df[
        df[
            "routing_decision"
        ].isin(
            [
                "SOFT_REVIEW",
                "HUMAN_ESCALATION",
                "ONTOLOGY_GAP_REVIEW"
            ]
        )
    ]
)


rejected = len(
    df[
        df["routing_decision"]
        == "REJECT"
    ]
)


automation_rate = (
    auto_approved
    / total
    * 100
    if total
    else 0
)


review_rate = (
    review_required
    / total
    * 100
    if total
    else 0
)


print("=" * 60)
print("SEMANTIC MAPPING METRICS")
print("=" * 60)

print(
    f"Total fields: {total}"
)

print(
    f"Auto approved: {auto_approved}"
)

print(
    f"Review required: {review_required}"
)

print(
    f"Rejected: {rejected}"
)

print(
    f"Automation rate: "
    f"{automation_rate:.2f}%"
)

print(
    f"Manual review rate: "
    f"{review_rate:.2f}%"
)
