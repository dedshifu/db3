"""Тесты сервиса ingest"""
import pytest
from unittest.mock import AsyncMock
from httpx import Response
from app.services.ingest import clean_json_payload, upsert_tenders

@pytest.mark.asyncio
async def test_clean_json_payload():
    data = {" key ": "  value  ", "nested": {" a ": [" b ", 1]}}
    assert clean_json_payload(data) == {"key": "value", "nested": {"a": ["b", 1]}}

@pytest.mark.asyncio
async def test_upsert_skips_invalid():
    valid = {
        "purchase_number": "T1", "object_info": "Test", "published_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-01T00:00:00", "region": 1, "stage": 1, "customers": [], "owners": [],
        "ikzs": [], "ktru": [], "okpd2": [], "plan_numbers": [], "position_numbers": [],
        "delivery_places": [], "delivery_places_kladr": [], "docs": []
    }
    invalid = {"purchase_number": "T2"}
    
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    
    count = await upsert_tenders(session, [valid, invalid])
    assert count == 1
    session.commit.assert_awaited_once()