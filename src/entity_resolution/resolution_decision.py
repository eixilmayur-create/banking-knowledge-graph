from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    PROJECT_ROOT /
    "outputs" /
    "entity_resolution"
)


fuzzy = pd.read_csv(
    OUTPUT_DIR /
    "fuzzy_matches.csv"
)


def classify_match(score: float) -> str:

    if score >= 90:
        return "MATCH"

    elif score >= 75:
        return "REVIEW"

    else:
        return "NO_MATCH"


fuzzy["resolution_decision"] = (
    fuzzy["fuzzy_score"]
    .apply(classify_match)
)


output_file = (
    OUTPUT_DIR /
    "entity_resolution_decisions.csv"
)

fuzzy.to_csv(
    output_file,
    index=False
)


print("=" * 60)
print("ENTITY RESOLUTION DECISIONS")
print("=" * 60)

print(
    fuzzy[
        "resolution_decision"
    ].value_counts()
)

print(
    f"\nSaved to:\n{output_file}"
)
