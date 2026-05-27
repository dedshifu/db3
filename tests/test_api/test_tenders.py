"""Интеграционные тесты API"""
import pytest
from unittest.mock import patch
from httpx import AsyncClient
from app.services.ingest import fetch_and_clean_tenders

@pytest.mark.asyncio
async def test_search_endpoint_empty(client: AsyncClient):
    response = await client.get("/api/v1/tenders/search")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

@pytest.mark.asyncio
@patch("app.api.v1.tenders.fetch_and_clean_tenders")
@patch("app.api.v1.tenders.upsert_tenders")
async def test_ingest_endpoint(mock_upsert, mock_fetch, client: AsyncClient):
    mock_fetch.return_value = []
    mock_upsert.return_value = 0
    response = await client.post("/api/v1/tenders/ingest")
    assert response.status_code == 200
    assert response.json()["status"] == "success"