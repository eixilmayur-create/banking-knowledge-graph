from typing import Any

from pydantic import BaseModel, Field


# ============================================================
# GRAPHRAG REQUEST
# ============================================================

class GraphRAGRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description=(
            "Natural-language question for "
            "the Banking Knowledge Graph."
        )
    )


# ============================================================
# GRAPHRAG RESPONSE
# ============================================================

class GraphRAGResponse(BaseModel):

    question: str

    intent: str

    answer: str

    evidence: list[dict[str, Any]]


# ============================================================
# HEALTH RESPONSE
# ============================================================

class HealthResponse(BaseModel):

    status: str

    neo4j: str
