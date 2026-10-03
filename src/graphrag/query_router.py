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


SUPPORTED_INTENTS = [
    "CUSTOMER_360",
    "CUSTOMER_TRANSACTIONS",
    "CUSTOMER_LOANS",
    "CUSTOMER_ACCOUNTS",
    "HIGH_RISK_ACTIVE_LOANS",
    "SHARED_BENEFICIARIES",
    "SHARED_ADDRESS",
    "CUSTOMER_CONNECTION_PATH",
    "UNKNOWN",
]


def route_question(
    question: str,
) -> dict[str, str | None]:

    prompt = f"""
You are a routing component for a Banking Knowledge Graph.

Classify the user's question into exactly one supported intent.

Supported intents:

CUSTOMER_360
- Complete customer overview including accounts, loans,
  cards and transactions.

CUSTOMER_TRANSACTIONS
- Questions about transactions for one customer.

CUSTOMER_LOANS
- Questions about loans for one customer.

CUSTOMER_ACCOUNTS
- Questions about accounts for one customer.

HIGH_RISK_ACTIVE_LOANS
- Questions about high-risk customers with active loans.

SHARED_BENEFICIARIES
- Questions asking which customers share a beneficiary.

SHARED_ADDRESS
- Questions asking which customers share an address.

CUSTOMER_CONNECTION_PATH
- Questions asking how two customers are connected.

UNKNOWN
- Anything outside these capabilities.

Extract customer IDs when present.
Customer IDs look like GC0000001.

Return JSON only.

Example:

{{
  "intent": "CUSTOMER_ACCOUNTS",
  "customer_id": "GC0000001",
  "customer_id_2": null
}}

USER QUESTION:

{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json"
        )
    )

    text = str(getattr(response, "text", "") or "")
    data = json.loads(text)

    intent = data.get(
        "intent",
        "UNKNOWN"
    )

    if intent not in SUPPORTED_INTENTS:
        intent = "UNKNOWN"

    return {
        "intent":
            intent,

        "customer_id":
            data.get(
                "customer_id"
            ),

        "customer_id_2":
            data.get(
                "customer_id_2"
            )
    }
