from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


COLLISION_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "semantic_collisions.csv"
)


SOURCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "new_source_schema.csv"
)


OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "ontology_gap_proposals.csv"
)


collisions = pd.read_csv(
    COLLISION_FILE
)

source_df = pd.read_csv(
    SOURCE_FILE
)


gaps = collisions[
    collisions[
        "collision_type"
    ].str.contains(
        "ONTOLOGY_GAP",
        na=False
    )
].copy()


if not gaps.empty:

    source_columns = [
        "source_column",
        "sample_value",
        "description",
        "source_datatype",
        "source_domain",
    ]

    gaps = gaps.merge(
        source_df[source_columns],
        on="source_column",
        how="left",
        suffixes=("", "_source")
    )

    proposals = gaps[
        [
            "source_column",
            "sample_value",
            "description",
            "source_datatype",
            "source_domain",
        ]
    ].copy()


    proposals[
        "proposed_entity"
    ] = proposals[
        "source_domain"
    ]


    proposals[
        "proposed_property"
    ] = ""


    proposals[
        "proposed_label"
    ] = ""


    proposals[
        "reuse_checked"
    ] = "NO"


    proposals[
        "review_status"
    ] = "PENDING"


else:

    proposals = pd.DataFrame(
        columns=[
            "source_column",
            "sample_value",
            "description",
            "source_datatype",
            "source_domain",
            "proposed_entity",
            "proposed_property",
            "proposed_label",
            "reuse_checked",
            "review_status",
        ]
    )


proposals.to_csv(
    OUTPUT_FILE,
    index=False
)


print("=" * 70)
print("ONTOLOGY GAP PROPOSALS CREATED")
print("=" * 70)

print(
    f"Ontology gaps: {len(proposals)}"
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)
