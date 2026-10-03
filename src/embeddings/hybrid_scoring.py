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

ONTOLOGY_FILE = (
    PROJECT_ROOT
    / "ontology"
    / "ontology_concepts.csv"
)

ALIAS_FILE = (
    PROJECT_ROOT
    / "config"
    / "semantic_aliases.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "hybrid_mapping_results.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

source_df = cast(Any, pd.read_csv(SOURCE_FILE))
candidate_df = cast(Any, pd.read_csv(CANDIDATE_FILE))
gemini_df = cast(Any, pd.read_csv(GEMINI_FILE))
ontology_df = cast(Any, pd.read_csv(ONTOLOGY_FILE))
alias_df = cast(Any, pd.read_csv(ALIAS_FILE))


# ============================================================
# CREATE LOOKUPS
# ============================================================

alias_lookup = dict(
    zip(
        alias_df["source_alias"],
        alias_df["concept_id"]
    )
)

ontology_lookup = (
    ontology_df
    .set_index("concept_id")
    .to_dict("index")
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(value: Any) -> str:

    if pd.isna(value):
        return ""

    return str(value).strip().lower()


def datatype_score(
    source_datatype: Any,
    candidate_datatype: Any,
) -> float:

    source_datatype = normalize_text(
        source_datatype
    )

    candidate_datatype = normalize_text(
        candidate_datatype
    )

    if source_datatype == candidate_datatype:
        return 1.0

    compatible = {
        ("integer", "decimal"),
        ("decimal", "integer"),
        ("date", "datetime"),
        ("datetime", "date"),
    }

    if (
        source_datatype,
        candidate_datatype
    ) in compatible:

        return 0.7

    return 0.0


def domain_score(
    source_domain: Any,
    candidate_entity: Any,
) -> float:

    source_domain = normalize_text(
        source_domain
    )

    candidate_entity = normalize_text(
        candidate_entity
    )

    if source_domain == candidate_entity:
        return 1.0

    return 0.0


# ============================================================
# HYBRID SCORING
# ============================================================

results: list[dict[str, Any]] = []


for _, source_row in source_df.iterrows():

    source_column = source_row[
        "source_column"
    ]

    # --------------------------------------------------------
    # ALIAS MATCH
    # --------------------------------------------------------

    alias_concept = alias_lookup.get(
        source_column
    )

    alias_match_score = (
        1.0
        if alias_concept
        else 0.0
    )


    # --------------------------------------------------------
    # GEMINI DECISION
    # --------------------------------------------------------

    gemini_row = gemini_df[
        gemini_df["source_column"]
        == source_column
    ]

    if not gemini_row.empty:

        gemini_row = gemini_row.iloc[0]

        gemini_concept = gemini_row[
            "concept_id"
        ]

        gemini_confidence = (
            float(
                gemini_row[
                    "gemini_confidence"
                ]
            )
            if pd.notna(
                gemini_row[
                    "gemini_confidence"
                ]
            )
            else 0.0
        )

    else:

        gemini_concept = None
        gemini_confidence = 0.0


    # --------------------------------------------------------
    # TOP EMBEDDING CANDIDATE
    # --------------------------------------------------------

    candidates = candidate_df[
        candidate_df["source_column"]
        == source_column
    ].sort_values(
        "candidate_rank"
    )


    if candidates.empty:

        continue


    top_candidate = candidates.iloc[0]

    top_concept = top_candidate[
        "concept_id"
    ]

    embedding_score = float(
        top_candidate[
            "similarity_score"
        ]
    )


    # --------------------------------------------------------
    # SELECT WORKING CONCEPT
    # --------------------------------------------------------

    if alias_concept:

        selected_concept = alias_concept

    elif pd.notna(gemini_concept):

        selected_concept = gemini_concept

    else:

        selected_concept = top_concept


    # --------------------------------------------------------
    # ONTOLOGY METADATA
    # --------------------------------------------------------

    concept_info = ontology_lookup.get(
        selected_concept,
        {}
    )

    candidate_entity = concept_info.get(
        "entity"
    )

    candidate_property = concept_info.get(
        "property"
    )

    candidate_datatype = concept_info.get(
        "datatype"
    )


    # --------------------------------------------------------
    # COMPATIBILITY SCORES
    # --------------------------------------------------------

    dtype_score = datatype_score(
        source_row[
            "source_datatype"
        ],
        candidate_datatype
    )

    entity_score = domain_score(
        source_row[
            "source_domain"
        ],
        candidate_entity
    )


    # --------------------------------------------------------
    # CONSENSUS BONUS
    # --------------------------------------------------------

    consensus_score = 0.0

    if (
        alias_concept
        and alias_concept
        == selected_concept
    ):
        consensus_score += 0.5

    if (
        pd.notna(gemini_concept)
        and gemini_concept
        == selected_concept
    ):
        consensus_score += 0.25

    if top_concept == selected_concept:
        consensus_score += 0.25


    # --------------------------------------------------------
    # HYBRID SCORE
    # --------------------------------------------------------

    hybrid_score = (
        alias_match_score * 0.25
        + embedding_score * 0.25
        + gemini_confidence * 0.25
        + dtype_score * 0.10
        + entity_score * 0.10
        + consensus_score * 0.05
    )


    hybrid_score = min(
        round(hybrid_score, 4),
        1.0
    )


    gemini_decision = None
    if not gemini_df[gemini_df["source_column"] == source_column].empty:
        gemini_decision = gemini_row.get("decision")

    # --------------------------------------------------------
    # ROUTING
    # --------------------------------------------------------

    if gemini_decision == "CREATE_NEW_CONCEPT":

        route = "ONTOLOGY_GAP_REVIEW"

    elif hybrid_score >= 0.90:

        route = "AUTO_APPROVE"

    elif hybrid_score >= 0.75:

        route = "SOFT_REVIEW"

    elif hybrid_score >= 0.50:

        route = "HUMAN_ESCALATION"

    else:

        route = "REJECT"

    results.append(
        {
            "source_column": source_column,
            "selected_concept": selected_concept,
            "entity": candidate_entity,
            "property": candidate_property,
            "alias_score": alias_match_score,
            "embedding_score": round(float(embedding_score), 4),
            "gemini_confidence": round(float(gemini_confidence), 4),
            "datatype_score": dtype_score,
            "domain_score": entity_score,
            "consensus_score": consensus_score,
            "hybrid_score": hybrid_score,
            "routing_decision": route,
        }
    )


result_df = pd.DataFrame(results)

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("=" * 70)
print("HYBRID SEMANTIC SCORING COMPLETE")
print("=" * 70)

print(
    result_df["routing_decision"].value_counts(dropna=False)
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)
