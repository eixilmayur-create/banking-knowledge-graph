from typing import Any

from src.graphrag.query_router import (
    route_question
)

from src.graphrag.graph_retriever import (
    retrieve_graph_context
)

from src.graphrag.answer_generator import (
    generate_grounded_answer
)


def ask_graphrag(
    question: str,
) -> dict[str, Any]:

    # ========================================================
    # ROUTING
    # ========================================================

    routing: dict[str, Any] = route_question(
        question
    )


    if routing["intent"] == "UNKNOWN":

        return {
            "question":
                question,

            "intent":
                "UNKNOWN",

            "answer":
                (
                    "This question is outside the "
                    "currently supported graph "
                    "capabilities."
                ),

            "evidence":
                []
        }


    # ========================================================
    # RETRIEVAL
    # ========================================================

    evidence: list[dict[str, Any]] = retrieve_graph_context(
        routing
    )


    # ========================================================
    # GENERATION
    # ========================================================

    answer = generate_grounded_answer(
        question,
        evidence
    )


    return {
        "question":
            question,

        "intent":
            routing["intent"],

        "answer":
            answer,

        "evidence":
            evidence
    }
