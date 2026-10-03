from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


INPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "gemini_mapping_results.csv"
)


OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "semantic_review_queue.csv"
)


df = pd.read_csv(
    INPUT_FILE
)


review = df[
    df["decision"].isin(
        [
            "REVIEW",
            "CREATE_NEW_CONCEPT"
        ]
    )
].copy()


review["reviewer_decision"] = ""
review["reviewer_comment"] = ""
review["reviewed_by"] = ""
review["reviewed_at"] = ""


review.to_csv(
    OUTPUT_FILE,
    index=False
)


print("=" * 60)
print("SEMANTIC REVIEW QUEUE CREATED")
print("=" * 60)

print(
    f"Items requiring review: {len(review)}"
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)
