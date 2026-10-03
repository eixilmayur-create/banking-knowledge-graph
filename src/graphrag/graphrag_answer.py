from query_router import (
    route_question
)

from graph_retriever import (
    retrieve_graph_context,
    close_driver
)

from answer_generator import (
    generate_grounded_answer
)


def ask_graph(
    question: str,
) -> str:

    print("\n" + "=" * 70)

    print("QUESTION")

    print("=" * 70)

    print(question)


    # ========================================================
    # 1. ROUTE QUESTION
    # ========================================================

    routing = route_question(
        question
    )


    print("\nROUTING")

    print(routing)


    if routing[
        "intent"
    ] == "UNKNOWN":

        return (
            "This question is outside the currently "
            "supported Banking GraphRAG capabilities."
        )


    # ========================================================
    # 2. RETRIEVE GRAPH EVIDENCE
    # ========================================================

    graph_context = (
        retrieve_graph_context(
            routing
        )
    )


    print(
        f"\nGRAPH RECORDS RETRIEVED: "
        f"{len(graph_context)}"
    )


    # ========================================================
    # 3. GENERATE GROUNDED ANSWER
    # ========================================================

    answer = generate_grounded_answer(
        question,
        graph_context
    )


    return answer


if __name__ == "__main__":

    try:

        while True:

            question = input(
                "\nAsk the Banking Knowledge Graph "
                "(type 'exit' to stop):\n> "
            )


            if question.lower() in {
                "exit",
                "quit"
            }:

                break


            answer = ask_graph(
                question
            )


            print("\nANSWER")

            print("=" * 70)

            print(answer)


    finally:

        close_driver()
