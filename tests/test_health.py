"""Тесты для health check endpoint"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_success():
    """Проверка, что health endpoint возвращает 200"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"]
    assert "service" in data
    assert data["service"] == "tender-search-api"


@pytest.mark.asyncio
async def test_health_with_db_mock():
    """Тест с моком БД (для будущего расширения)"""
    
    pass