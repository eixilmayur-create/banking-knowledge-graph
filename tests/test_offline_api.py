"""Contract tests using mocked external services; no cloud calls."""
import importlib
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv("NEO4J_PASSWORD", "offline-test-placeholder")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "offline-test-project")
    with patch("neo4j.GraphDatabase.driver", return_value=MagicMock()), patch("google.genai.Client", return_value=MagicMock()):
        module = importlib.import_module("src.api.main")
        monkeypatch.setattr(module, "verify_connection", lambda: None)
        monkeypatch.setattr(module, "close_driver", lambda: None)
        with TestClient(module.app) as client:
            yield module, client

def test_root_and_health(api):
    _, client = api
    assert client.get("/").status_code == 200
    assert client.get("/health").json() == {"status": "healthy", "neo4j": "connected"}

def test_unavailable_database(api, monkeypatch):
    module, client = api
    def unavailable():
        raise RuntimeError("offline")
    monkeypatch.setattr(module, "verify_connection", unavailable)
    assert client.get("/health").status_code == 503

def test_missing_customer(api, monkeypatch):
    module, client = api
    monkeypatch.setattr(module, "get_customer", lambda _: None)
    assert client.get("/customer/missing").status_code == 404

@pytest.mark.parametrize("limit", [0, 201])
def test_transaction_limits(api, limit):
    _, client = api
    assert client.get(f"/customer/demo/transactions?limit={limit}").status_code == 422

def test_empty_question(api):
    _, client = api
    assert client.post("/graphrag/ask", json={"question": ""}).status_code == 422

def test_graphrag_evidence_contract(api, monkeypatch):
    module, client = api
    payload = {"question": "Show demo accounts", "intent": "CUSTOMER_ACCOUNTS", "answer": "One demo account", "evidence": [{"accountId": "DEMO-1"}]}
    monkeypatch.setattr(module, "ask_graphrag", lambda _: payload)
    assert client.post("/graphrag/ask", json={"question": payload["question"]}).json() == payload
