import os
from typing import Any, cast

from dotenv import load_dotenv
from google import genai
from google.genai.types import HttpOptions


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

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=(
        "Return exactly the text "
        "'Gemini connection successful'."
    )
)

print(
    getattr(response, "text", str(response))
)
