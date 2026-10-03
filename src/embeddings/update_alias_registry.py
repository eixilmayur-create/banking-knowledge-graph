from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


FEEDBACK_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "semantic_mapping_feedback.csv"
)


ALIAS_FILE = (
    PROJECT_ROOT
    / "config"
    / "semantic_aliases.csv"
)


feedback = pd.read_csv(
    FEEDBACK_FILE
)


aliases = pd.read_csv(
    ALIAS_FILE
)


approved = feedback[
    feedback[
        "reviewer_decision"
    ].isin(
        [
            "APPROVE",
            "CORRECT_MAPPING"
        ]
    )
].copy()


new_aliases = approved[
    [
        "source_column",
        "approved_concept"
    ]
].copy()


new_aliases.rename(
    columns={
        "source_column":
            "source_alias",

        "approved_concept":
            "concept_id"
    },
    inplace=True
)


combined = pd.concat(
    [
        aliases,
        new_aliases
    ],
    ignore_index=True
)


combined.drop_duplicates(
    subset=[
        "source_alias"
    ],
    keep="last",
    inplace=True
)


combined.to_csv(
    ALIAS_FILE,
    index=False
)


print(
    "Semantic alias registry updated."
)
