from pathlib import Path
import os
import json
from typing import Any, cast

import pandas as pd

from dotenv import load_dotenv
from google import genai
from google.genai.types import HttpOptions


load_dotenv()


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


OUTPUT_FILE = (
    PROJECT_ROOT
    / "outputs"
    / "embeddings"
    / "gemini_mapping_results.csv"
)


source_df = cast(Any, pd.read_csv(
    SOURCE_FILE
))

candidate_df = cast(Any, pd.read_csv(
    CANDIDATE_FILE
))

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

result_rows: list[dict[str, Any]] = []


for _, source_row in source_df.iterrows():

    source_column = source_row[
        "source_column"
    ]


    candidates = candidate_df[
        candidate_df[
            "source_column"
        ] == source_column
    ]

    candidate_text: list[dict[str, Any]] = []

    for _, candidate in candidates.iterrows():

        candidate_text.append(
            {
                "concept_id":
                    candidate[
                        "concept_id"
                    ],

                "entity":
                    candidate[
                        "candidate_entity"
                    ],

                "property":
                    candidate[
                        "candidate_property"
                    ],

                "label":
                    candidate[
                        "candidate_label"
                    ],

                "similarity":
                    float(
                        candidate[
                            "similarity_score"
                        ]
                    )
            }
        )


    prompt = f"""
You are performing ontology schema mapping.

SOURCE FIELD

source_column:
{source_column}

sample_value:
{source_row['sample_value']}

description:
{source_row['description']}


CANDIDATE ONTOLOGY CONCEPTS

{json.dumps(candidate_text, indent=2)}


TASK

Choose the best ontology concept only if the semantic
meaning is sufficiently supported.

Return ONLY valid JSON:

{{
  "decision": "MAP | REVIEW | CREATE_NEW_CONCEPT",
  "concept_id": "candidate concept id or null",
  "entity": "entity or null",
  "property": "property or null",
  "confidence": 0.0,
  "reason": "brief explanation"
}}

Rules:

1. Never invent an existing concept.
2. MAP only when there is strong semantic alignment.
3. REVIEW when two or more candidates remain plausible.
4. CREATE_NEW_CONCEPT when no candidate adequately
   represents the source field.
5. Confidence must be between 0 and 1.
"""


    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )


        text = str(
            getattr(response, "text", "")
        ).replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()


        decision = json.loads(
            text
        )


        result_rows.append(
            {
                "source_column":
                    source_column,

                "sample_value":
                    source_row[
                        "sample_value"
                    ],

                "decision":
                    decision.get(
                        "decision"
                    ),

                "concept_id":
                    decision.get(
                        "concept_id"
                    ),

                "entity":
                    decision.get(
                        "entity"
                    ),

                "property":
                    decision.get(
                        "property"
                    ),

                "gemini_confidence":
                    decision.get(
                        "confidence"
                    ),

                "reason":
                    decision.get(
                        "reason"
                    )
            }
        )


    except Exception as error:

        result_rows.append(
            {
                "source_column":
                    source_column,

                "sample_value":
                    source_row[
                        "sample_value"
                    ],

                "decision":
                    "REVIEW",

                "concept_id":
                    None,

                "entity":
                    None,

                "property":
                    None,

                "gemini_confidence":
                    0,

                "reason":
                    (
                        f"Gemini request failed: "
                        f"{error}"
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
print("GEMINI SEMANTIC MAPPING COMPLETE")
print("=" * 60)

print(
    result_df[
        "decision"
    ].value_counts(
        dropna=False
    )
)

print(
    f"\nSaved to:\n{OUTPUT_FILE}"
)
