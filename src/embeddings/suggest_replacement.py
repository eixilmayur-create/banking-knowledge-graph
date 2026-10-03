from pathlib import Path
import argparse
from typing import Any, cast

import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]


ONTOLOGY_FILE = (
    PROJECT_ROOT
    / "ontology"
    / "ontology_concepts.csv"
)


parser = argparse.ArgumentParser()

parser.add_argument(
    "--concept",
    required=True,
    help="Concept ID such as C004"
)

args = parser.parse_args()


ontology = cast(Any, pd.read_csv(
    ONTOLOGY_FILE
))


current = ontology[
    ontology["concept_id"]
    == args.concept
]


if current.empty:

    raise ValueError(
        "Concept ID not found."
    )


current = current.iloc[0]


model = cast(Any, SentenceTransformer(
    "all-MiniLM-L6-v2"
))


ontology["search_text"] = (

    ontology["entity"].fillna("")
    + " "
    + ontology["property"].fillna("")
    + " "
    + ontology["label"].fillna("")
    + " "
    + ontology["description"].fillna("")
)


embeddings = np.asarray(
    model.encode(
        ontology["search_text"].tolist(),
        normalize_embeddings=True,
        convert_to_numpy=True,
    ),
    dtype=np.float32,
)


query_text = (
    f"{current['entity']} "
    f"{current['property']} "
    f"{current['label']} "
    f"{current['description']}"
)


query_embedding = np.asarray(
    model.encode(
        [query_text],
        normalize_embeddings=True,
        convert_to_numpy=True,
    )[0],
    dtype=np.float32,
)


scores = np.dot(
    embeddings,
    query_embedding
)


ontology[
    "replacement_similarity"
] = scores


# Remove same concept
candidates = ontology[
    ontology["concept_id"]
    != args.concept
].copy()


# Prefer same domain/datatype
candidates[
    "same_domain"
] = (
    candidates["entity"]
    == current["entity"]
).astype(int)


candidates[
    "same_datatype"
] = (
    candidates["datatype"]
    == current["datatype"]
).astype(int)


candidates[
    "replacement_score"
] = (

    candidates[
        "replacement_similarity"
    ] * 0.70

    + candidates[
        "same_domain"
    ] * 0.20

    + candidates[
        "same_datatype"
    ] * 0.10
)


top = candidates.sort_values(
    "replacement_score",
    ascending=False
).head(5)


print("=" * 70)
print("REPLACEMENT SUGGESTIONS")
print("=" * 70)

print(
    f"\nCurrent concept:"
    f"\n{args.concept}"
    f" -> "
    f"{current['entity']}."
    f"{current['property']}"
)

print("\nTop candidates:\n")

print(
    top[
        [
            "concept_id",
            "entity",
            "property",
            "label",
            "replacement_similarity",
            "same_domain",
            "same_datatype",
            "replacement_score",
        ]
    ].to_string(
        index=False
    )
)
