from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


REVIEW_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "human_review_queue.csv"
)


FEEDBACK_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "semantic_mapping_feedback.csv"
)


review_df = pd.read_csv(
    REVIEW_FILE
)


completed = review_df[
    review_df[
        "reviewer_decision"
    ].notna()
].copy()


completed = completed[
    completed[
        "reviewer_decision"
    ].astype(str).str.strip()
    != ""
]


feedback_columns = [
    "source_column",
    "selected_concept",
    "hybrid_score",
    "routing_decision",
    "reviewer_decision",
    "approved_concept",
    "reviewer_comment",
    "reviewed_by",
    "reviewed_at",
]


feedback_df = completed[
    feedback_columns
]


feedback_df.to_csv(
    FEEDBACK_FILE,
    index=False
)


print("=" * 60)
print("REVIEWER FEEDBACK PROCESSED")
print("=" * 60)

print(
    f"Completed reviews: {len(feedback_df)}"
)

print(
    f"\nSaved to:\n{FEEDBACK_FILE}"
)
