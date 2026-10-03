import json
import os
from typing import Any, cast

from dotenv import load_dotenv

from google import genai
from google.genai.types import (
    GenerateContentConfig,
    HttpOptions,
)


load_dotenv()


client = cast(
    Any,
    genai.Client(
        vertexai=True,
        project=os.getenv(
            "GOOGLE_CLOUD_PROJECT"
        ),
        location=os.getenv(
            "GOOGLE_CLOUD_LOCATION",
            "global"
        ),
        http_options=HttpOptions(
            api_version="v1"
        )
    )
)


def generate_grounded_answer(
    question: str,
    graph_context: list[dict[str, Any]] | None,
) -> str:

    if not graph_context:

        return (
            "I could not find sufficient evidence "
            "in the Knowledge Graph to answer "
            "this question."
        )


    context_json = json.dumps(
        graph_context,
        indent=2,
        default=str
    )


    prompt = f"""
You are answering questions using evidence retrieved
from a Banking Knowledge Graph.

USER QUESTION

{question}


GRAPH EVIDENCE

{context_json}


RULES

1. Answer using ONLY the graph evidence above.

2. Do not invent accounts, loans, customers,
   transactions, relationships, dates, amounts,
   or explanations.

3. If evidence is insufficient, explicitly say
   that the Knowledge Graph does not contain
   enough evidence.

4. Clearly distinguish graph facts from any
   interpretation.

5. Keep the answer concise.

6. When identifiers are available, include them.

7. Do not claim that a connection implies fraud,
   wrongdoing, or risk unless such a fact explicitly
   exists in the graph.

Answer the user question.
"""


    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=GenerateContentConfig(
            temperature=0
        )
    )


    return response.text
