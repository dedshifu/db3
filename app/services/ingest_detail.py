"""Асинхронный сервис загрузки детальных закупок."""
import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from pydantic import ValidationError

from app.models.tender_detail import TenderDetail
from app.schemas.tender_detail import TenderDetailSchema
from app.utils.json_cleaner import clean_json_payload
from app.utils.helpers import safe_get

logger = logging.getLogger("app.ingest_detail")

async def upsert_tender_details(session: AsyncSession, raw_items: List[dict]) -> int:
    """Валидирует и сохраняет детальные закупки в БД.
    
    Args:
        session: Асинхронная сессия БД.
        raw_items: Список сырых JSON-объектов (response_*.json).
        
    Returns:
        Количество успешно сохранённых/обновлённых записей.
    """
    records = []
    for item in raw_items:
        try:
            cleaned = clean_json_payload(item)
            schema = TenderDetailSchema.from_raw_json(cleaned)
            records.append({
                "purchase_number": schema.purchase_number,
                "fz": schema.fz,
                "purchase_object_info": schema.purchase_object_info,
                "tender_price": schema.tender_price,
                "collecting_start": schema.collecting_start,
                "collecting_end": schema.collecting_end,
                "summarizing_date": schema.summarizing_date,
                "etp_name": schema.etp_name,
                "etp_url": schema.etp_url,
                "customer_inn": schema.customer_inn,
                "placing_way_name": schema.placing_way_name,
                "lots_count": schema.lots_count,
                "is_goz": schema.is_goz,
                "raw_data": cleaned,
            })
        except (ValidationError, AttributeError, TypeError) as exc:
            logger.warning("Пропущена детальная закупка %s: %s", 
                          safe_get(item, "purchaseNumber", default="UNKNOWN"), exc)
            continue

    if not records:
        return 0

    stmt = insert(TenderDetail).values(records)
    stmt = stmt.on_conflict_do_update(
        index_elements=["purchase_number"],
        set_={
            "tender_price": stmt.excluded.tender_price,
            "collecting_end": stmt.excluded.collecting_end,
            "lots_count": stmt.excluded.lots_count,
            "raw_data": stmt.excluded.raw_data,
        }
    )
    await session.execute(stmt)
    # commit выполняется на уровне запроса в get_db (Unit of Work)
    logger.info("Сохранено/обновлено %d детальных закупок.", len(records))
    return len(records)