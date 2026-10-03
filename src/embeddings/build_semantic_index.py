from pathlib import Path
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

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD ONTOLOGY CONCEPTS
# ============================================================

ontology = pd.read_csv(
    ONTOLOGY_FILE
)


# ============================================================
# CREATE TEXT REPRESENTATION
# ============================================================

ontology["embedding_text"] = (

    ontology["entity"].fillna("")
    + " "
    + ontology["property"].fillna("")
    + " "
    + ontology["label"].fillna("")
    + " "
    + ontology["description"].fillna("")
    + " datatype "
    + ontology["datatype"].fillna("")
)


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

model = cast(Any, SentenceTransformer(
    "all-MiniLM-L6-v2"
))


# ============================================================
# GENERATE EMBEDDINGS
# ============================================================

embeddings = np.asarray(
    model.encode(
        ontology["embedding_text"].tolist(),
        normalize_embeddings=True,
        convert_to_numpy=True,
    ),
    dtype=np.float32,
)


# ============================================================
# SAVE DATA
# ============================================================

np.save(
    OUTPUT_DIR
    / "ontology_embeddings.npy",
    embeddings
)


ontology.to_csv(
    OUTPUT_DIR
    / "ontology_index.csv",
    index=False
)


print("=" * 60)
print("ONTOLOGY SEMANTIC INDEX CREATED")
print("=" * 60)

print(
    f"Ontology concepts: {len(ontology)}"
)

print(
    f"Embedding dimensions: {embeddings.shape[1]}"
)
