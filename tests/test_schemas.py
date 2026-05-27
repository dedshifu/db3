"""Тесты Pydantic валидации"""
import pytest
from app.schemas.tender_index import TenderIndexSchema
from datetime import datetime

def test_valid_index_schema():
    data = {
        "purchase_number ": "0123456789 ",
        "object_info ": "Тестовая закупка ",
        "published_at ": "2026-05-15T10:00:00",
        "updated_at ": "2026-05-15T10:00:00",
        "region ": 77, "stage ": 1
    }
    schema = TenderIndexSchema.model_validate(data)
    assert schema.purchase_number == "0123456789"
    assert schema.object_info == "Тестовая закупка"
    assert schema.published_at == datetime(2026, 5, 15, 10, 0)

def test_invalid_missing_required():
    with pytest.raises(Exception):
        TenderIndexSchema.model_validate({"purchase_number": "T1"})