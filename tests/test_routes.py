import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_llm():
    with patch("app.services.llm_client.call_llm", new_callable=AsyncMock) as m:
        m.return_value = "Краткая суммаризация тестового текста."
        yield m

def test_valid_request(mock_llm):
    r = client.post("/api/v1/process", json={"text": "Это длинный текст, который нужно сократить для теста."})
    assert r.status_code == 200
    assert r.json()["source"] in ["llm", "cache"]

def test_validation_error():
    r = client.post("/api/v1/process", json={"text": "ab"})
    assert r.status_code == 422  # Pydantic validation

def test_fallback_on_error():
    with patch("app.services.llm_client.call_llm", side_effect=Exception("Network Down")):
        r = client.post("/api/v1/process", json={"text": "Текст при сбое сети."})
        assert r.status_code == 200
        assert r.json()["source"] == "fallback"