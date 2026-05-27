# app/schemas/tender_detail.py
"""Pydantic-схема для детальной информации о закупке + безопасный парсер ЕИС"""
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.utils.helpers import safe_get, parse_iso_date, clean_price


class TenderDetailSchema(BaseModel):
    """
    Схема детальной информации о закупке
    Адаптирована под структуру ответов ЕИС/Госплан и схему БД
    """
    model_config = ConfigDict(from_attributes=True)

    
    id: Optional[int] = None
    purchase_number: str = Field(..., description="Номер закупки")
    max_price: Optional[float] = Field(None, description="Начальная (максимальная) цена контракта")
    currency: str = Field(default="RUB", description="Код валюты")
    publish_date: Optional[datetime] = Field(None, description="Дата публикации")
    submission_end: Optional[datetime] = Field(None, description="Окончание подачи заявок")
    fz: Optional[str] = Field(None, description="Тип закона (44-ФЗ, 223-ФЗ и т.д.)")
    placing_way_code: Optional[str] = Field(None, description="Код способа закупки")
    status: Optional[str] = Field(None, description="Текущий статус закупки")
    customer_inn: Optional[str] = Field(None, description="ИНН заказчика")
    customer_name: Optional[str] = Field(None, description="Полное наименование заказчика")
    region: Optional[str] = Field(None, description="Код или название региона")

    
    collecting_start: Optional[datetime] = Field(None, description="Начало приема заявок")
    collecting_end: Optional[datetime] = Field(None, description="Окончание приема заявок")
    summarizing_date: Optional[datetime] = Field(None, description="Дата подведения итогов")
    etp_name: Optional[str] = Field(None, description="Название электронной площадки")
    etp_url: Optional[str] = Field(None, description="Ссылка на площадку")
    placing_way_name: Optional[str] = Field(None, description="Название способа закупки")
    lots_count: Optional[int] = Field(None, description="Количество лотов")
    is_goz: Optional[bool] = Field(False, description="Признак Гособоронзаказа")
    purchase_object_info: Optional[str] = Field(None, description="Предмет закупки")

    
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Исходный JSON от ЕИС")

    @classmethod
    def from_raw_json(cls, raw_json: Dict[str, Any]) -> "TenderDetailSchema":
        """
        Безопасный парсинг сырого JSON от ЕИС/Госплан
        Использует утилиты для защиты от KeyError, None и некорректных форматов
        """
        procedure = safe_get(raw_json, "procedure", default={})
        collecting = safe_get(raw_json, "collecting", default={})
        customer = safe_get(raw_json, "customer", default={})
        etp = safe_get(raw_json, "etp", default={})

        return cls(
            
            purchase_number=safe_get(raw_json, "purchaseNumber", default="UNKNOWN"),
            max_price=clean_price(safe_get(procedure, "maxPrice")),
            currency=safe_get(procedure, "currencyCode", default="RUB"),
            publish_date=parse_iso_date(safe_get(raw_json, "publishDate")),
            submission_end=parse_iso_date(safe_get(procedure, "applicationSummDate")),
            fz=safe_get(raw_json, "fzType") or safe_get(raw_json, "fz"),
            placing_way_code=safe_get(raw_json, "placingWayCode"),
            status=safe_get(raw_json, "status") or safe_get(raw_json, "purchaseStatus"),
            customer_inn=safe_get(customer, "inn"),
            customer_name=safe_get(customer, "fullName"),
            region=safe_get(raw_json, "regionCode") or safe_get(raw_json, "region", "name"),

            
            collecting_start=parse_iso_date(safe_get(collecting, "startDate")),
            collecting_end=parse_iso_date(safe_get(collecting, "endDate")),
            summarizing_date=parse_iso_date(safe_get(procedure, "summarizingDate")),
            etp_name=safe_get(etp, "name") or safe_get(etp, "shortName"),
            etp_url=safe_get(etp, "url") or safe_get(etp, "link"),
            placing_way_name=safe_get(raw_json, "placingWayName"),
            lots_count=safe_get(raw_json, "lotsCount", default=1),
            is_goz=bool(safe_get(raw_json, "isGoz", default=False)),
            purchase_object_info=safe_get(raw_json, "purchaseObjectInfo"),

            
            raw_data=raw_json
        )