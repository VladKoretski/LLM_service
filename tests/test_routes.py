# tests/test_routes.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.services.llm_client import FALLBACK_RESPONSE

client = TestClient(app)

@pytest.mark.asyncio
async def test_valid_request():
    """Тест успешного запроса с моком call_llm"""
    # Патчим там, где функция используется (в processor), а не где определена!
    with patch("app.services.processor.call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "Краткая суммаризация тестового текста."
        
        response = client.post("/api/v1/process", json={"text": "Это длинный текст для теста."})
        
        assert response.status_code == 200
        data = response.json()
        assert data["source"] in ["llm", "cache"]
        assert "суммаризация" in data["result"].lower()

@pytest.mark.asyncio
async def test_validation_error():
    """Тест валидации: текст короче 5 символов"""
    response = client.post("/api/v1/process", json={"text": "аб"})
    assert response.status_code == 422  # Pydantic validation error

@pytest.mark.asyncio
async def test_fallback_on_error():
    """Тест fallback при ошибке вызова LLM"""
    # Патчим там, где функция используется
    with patch("app.services.processor.call_llm", new_callable=AsyncMock) as mock_llm:
        # Имитируем падение сети
        mock_llm.side_effect = Exception("Network Down")
        
        response = client.post("/api/v1/process", json={"text": "Текст при сбое сети."})
        
        assert response.status_code == 200  # Сервис не падает, а возвращает 200
        data = response.json()
        assert data["source"] == "fallback"
        assert "недоступен" in data["result"]
