from typing import Any

from fastapi.testclient import TestClient

from src.api.main import app


client: Any = TestClient(
    app
)


def test_root():

    response: Any = client.get(
        "/"
    )

    assert (
        response.status_code
        == 200
    )


def test_health():

    response: Any = client.get(
        "/health"
    )

    assert (
        response.status_code
        == 200
    )


def test_invalid_graphrag_question():

    response: Any = client.post(
        "/graphrag/ask",
        json={
            "question": ""
        }
    )

    assert (
        response.status_code
        == 422
    )
