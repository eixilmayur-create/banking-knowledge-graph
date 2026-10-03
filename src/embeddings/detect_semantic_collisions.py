from pathlib import Path
from typing import Any, cast

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "new_source_schema.csv"
)

CANDIDATE_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "mapping_candidates.csv"
)

GEMINI_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "gemini_mapping_results.csv"
)

HYBRID_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "hybrid_mapping_results.csv"
)

ONTOLOGY_FILE = (
    PROJECT_ROOT
    / "ontology"
    / "ontology_concepts.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "semantic_collisions.csv"
)


source_df = cast(Any, pd.read_csv(SOURCE_FILE))
candidate_df = cast(Any, pd.read_csv(CANDIDATE_FILE))
gemini_df = cast(Any, pd.read_csv(GEMINI_FILE))
hybrid_df = cast(Any, pd.read_csv(HYBRID_FILE))
ontology_df = cast(Any, pd.read_csv(ONTOLOGY_FILE))


ontology_lookup = (
    ontology_df
    .set_index("concept_id")
    .to_dict("index")
)


def norm(value: Any) -> str:

    if pd.isna(value):
        return ""

    return str(value).strip().lower()


collision_rows: list[dict[str, Any]] = []


for _, source_row in source_df.iterrows():

    source_column = source_row["source_column"]

    source_domain = norm(
        source_row["source_domain"]
    )

    source_datatype = norm(
        source_row["source_datatype"]
    )


    # ========================================================
    # TOP EMBEDDING CANDIDATE
    # ========================================================

    candidates = candidate_df[
        candidate_df["source_column"]
        == source_column
    ].sort_values(
        "candidate_rank"
    )

    if candidates.empty:
        continue

    top_candidate = candidates.iloc[0]

    embedding_concept = (
        top_candidate["concept_id"]
    )


    # ========================================================
    # GEMINI CANDIDATE
    # ========================================================

    gemini_match = gemini_df[
        gemini_df["source_column"]
        == source_column
    ]

    if not gemini_match.empty:

        gemini_concept = (
            gemini_match.iloc[0]["concept_id"]
        )

        gemini_decision = (
            gemini_match.iloc[0]["decision"]
        )

    else:

        gemini_concept = None
        gemini_decision = None


    # ========================================================
    # HYBRID SELECTION
    # ========================================================

    hybrid_match = hybrid_df[
        hybrid_df["source_column"]
        == source_column
    ]

    if hybrid_match.empty:
        continue

    hybrid_row = hybrid_match.iloc[0]

    selected_concept = (
        hybrid_row["selected_concept"]
    )


    # ========================================================
    # ONTOLOGY METADATA
    # ========================================================

    concept_info = ontology_lookup.get(
        selected_concept,
        {}
    )

    target_domain = norm(
        concept_info.get("entity")
    )

    target_datatype = norm(
        concept_info.get("datatype")
    )


    # ========================================================
    # COLLISION FLAGS
    # ========================================================

    embedding_gemini_disagree = (
        pd.notna(gemini_concept)
        and
        embedding_concept != gemini_concept
    )


    domain_mismatch = (
        source_domain
        and target_domain
        and source_domain != target_domain
    )


    datatype_mismatch = (
        source_datatype
        and target_datatype
        and source_datatype != target_datatype
    )


    ontology_gap = (
        gemini_decision
        == "CREATE_NEW_CONCEPT"
    )


    # ========================================================
    # DETERMINE COLLISION
    # ========================================================

    flags: list[str] = []

    if embedding_gemini_disagree:
        flags.append(
            "EMBEDDING_GEMINI_DISAGREEMENT"
        )

    if domain_mismatch:
        flags.append(
            "DOMAIN_MISMATCH"
        )

    if datatype_mismatch:
        flags.append(
            "DATATYPE_MISMATCH"
        )

    if ontology_gap:
        flags.append(
            "ONTOLOGY_GAP"
        )


    if flags:

        collision_rows.append(
            {
                "source_column":
                    source_column,

                "selected_concept":
                    selected_concept,

                "embedding_concept":
                    embedding_concept,

                "gemini_concept":
                    gemini_concept,

                "source_domain":
                    source_domain,

                "target_domain":
                    target_domain,

                "source_datatype":
                    source_datatype,

                "target_datatype":
                    target_datatype,

                "collision_type":
                    "|".join(flags),

                "routing_decision":
                    hybrid_row[
                        "routing_decision"
                    ]
            }
        )


collision_df = pd.DataFrame(
    collision_rows
)


collision_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("=" * 70)
print("SEMANTIC COLLISION DETECTION COMPLETE")
print("=" * 70)

print(
    f"Collisions detected: {len(collision_df)}"
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)
