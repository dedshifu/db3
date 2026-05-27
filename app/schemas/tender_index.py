"""Pydantic v2 схемы для плоского JSON (debug_response.json)"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, field_validator

class DocIndexSchema(BaseModel):
    """Схема документа из индексного списка"""
    doc_type: str
    published_at: Optional[datetime] = None

class TenderIndexSchema(BaseModel):
    """Валидатор для индексного ответа API Госплана
    
    Автоматически обрезает пробелы, кастит типы, игнорирует лишние поля
    """
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    purchase_number: str
    object_info: str
    purchase_type: Optional[str] = None
    max_price: Optional[float] = None
    currency_code: str = "RUB"
    contract_guarantee_amount: Optional[float] = None
    contract_guarantee_part: Optional[float] = None
    
    collecting_finished_at: Optional[datetime] = None
    published_at: datetime
    updated_at: datetime
    doc_created_at: Optional[datetime] = None
    doc_updated_at: Optional[datetime] = None

    region: int
    stage: int
    responsible: Optional[str] = None
    
    customers: list[str] = []
    owners: list[str] = []
    ikzs: list[str] = []
    ktru: list[str] = []
    okpd2: list[str] = []
    plan_numbers: list[str] = []
    position_numbers: list[str] = []
    delivery_places: list[str] = []
    delivery_places_kladr: list[str] = []
    docs: list[DocIndexSchema] = []

    @field_validator(
        "purchase_number", "object_info", "currency_code", "responsible",
        "purchase_type", mode="before"
    )
    @classmethod
    def strip_strings(cls, v: Any) -> Any:
        """Удаляет пробелы из строковых полей до валидации типов"""
        return v.strip() if isinstance(v, str) else v