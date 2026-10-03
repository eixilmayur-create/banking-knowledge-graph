from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "hybrid_mapping_results.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "human_review_queue.csv"
)


df = pd.read_csv(
    INPUT_FILE
)


review_routes = [
    "SOFT_REVIEW",
    "HUMAN_ESCALATION",
    "ONTOLOGY_GAP_REVIEW",
]


review_df = df[
    df[
        "routing_decision"
    ].isin(
        review_routes
    )
].copy()


review_df[
    "reviewer_decision"
] = ""

review_df[
    "approved_concept"
] = ""

review_df[
    "reviewer_comment"
] = ""

review_df[
    "reviewed_by"
] = ""

review_df[
    "reviewed_at"
] = ""


review_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("=" * 60)
print("HUMAN REVIEW QUEUE CREATED")
print("=" * 60)

print(
    f"Review items: {len(review_df)}"
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)
