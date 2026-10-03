from pathlib import Path
from typing import Any, cast

import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]


ONTOLOGY_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "ontology_index.csv"
)

EMBEDDING_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "ontology_embeddings.npy"
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
    / "mapping_candidates.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

ontology = cast(Any, pd.read_csv(
    ONTOLOGY_FILE
))

ontology_embeddings = np.load(
    EMBEDDING_FILE
)

source = cast(Any, pd.read_csv(
    SOURCE_FILE
))


model = cast(Any, SentenceTransformer(
    "all-MiniLM-L6-v2"
))


# ============================================================
# RETRIEVE TOP CANDIDATES
# ============================================================

result_rows: list[dict[str, Any]] = []


for _, row in source.iterrows():

    source_text = (
        f"column {row['source_column']} "
        f"sample {row['sample_value']} "
        f"description {row['description']}"
    )


    query_embedding = np.asarray(
        model.encode(
            [source_text],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0],
        dtype=np.float32,
    )


    scores = np.dot(
        ontology_embeddings,
        query_embedding
    )


    top_indices = np.argsort(
        scores
    )[::-1][:3]


    for rank, index in enumerate(
        top_indices,
        start=1
    ):

        candidate = ontology.iloc[index]

        result_rows.append(
            {
                "source_system":
                    row["source_system"],

                "source_column":
                    row["source_column"],

                "sample_value":
                    row["sample_value"],

                "candidate_rank":
                    rank,

                "concept_id":
                    candidate[
                        "concept_id"
                    ],

                "candidate_entity":
                    candidate[
                        "entity"
                    ],

                "candidate_property":
                    candidate[
                        "property"
                    ],

                "candidate_label":
                    candidate[
                        "label"
                    ],

                "similarity_score":
                    round(
                        float(
                            scores[index]
                        ),
                        4
                    )
            }
        )


result_df = pd.DataFrame(
    result_rows
)


result_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("=" * 60)
print("SEMANTIC CANDIDATE RETRIEVAL COMPLETE")
print("=" * 60)

print(
    f"Source fields processed: {len(source)}"
)

print(
    f"Candidates generated: {len(result_df)}"
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)
