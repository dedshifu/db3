import logging
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tender import Tender, Lot

logger = logging.getLogger(__name__)


def safe_get(data: dict, *keys, default=None):
    """Безопасный доступ к вложенным ключам без выброса KeyError"""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current


def parse_dt(val: Optional[str]) -> Optional[datetime]:
    """Безопасный парсинг дат из ЕИС (поддержка +03:00, Z, null)."""
    if not val:
        return None
    try:
        val = val.strip().replace("Z", "+00:00")
        return datetime.fromisoformat(val)
    except (ValueError, TypeError, AttributeError):
        logger.warning("Невалидная дата при парсинге: %s", val)
        return None


async def upsert_lots(session: AsyncSession, tender_id: int, lots_raw: list[dict]) -> None:
    """Идемпотентное сохранение/обновление лотов через ON CONFLICT"""
    if not lots_raw:
        return

    lot_values = []
    for lot in lots_raw:
        lot_values.append({
            "tender_id": tender_id,
            "lot_number": lot.get("lotNumber", 0),
            "max_price": lot.get("maxPrice"),
            "currency": safe_get(lot, "currency", "code"),
            "objects_description": lot.get("purchaseObjects"),
            "guarantee_info": {
                "application": lot.get("lot_applicationGuarantee"),
                "customer": lot.get("lot_customerGuarantee"),
                "contract_amount": safe_get(lot, "contractGuarantee", "amount"),
                "contract_procedure": safe_get(lot, "contractGuarantee", "procedureInfo"),
                "warranty": lot.get("warrantyInfo")
            }
        })

    stmt = insert(Lot).values(lot_values)
    stmt = stmt.on_conflict_do_update(
        index_elements=["tender_id", "lot_number"],
        set_={
            "max_price": stmt.excluded.max_price,
            "objects_description": stmt.excluded.objects_description,
            "guarantee_info": stmt.excluded.guarantee_info,
        }
    )
    await session.execute(stmt)


async def upsert_tender(session: AsyncSession, raw_json: dict) -> Tender:
    """Идемпотентное сохранение/обновление тендера"""
    purchase_number = (raw_json.get("purchaseNumber") or "").strip()
    if not purchase_number:
        raise ValueError("Отсутствует обязательное поле purchaseNumber")

    lots_raw = raw_json.get("lots", [])
    first_lot = lots_raw[0] if lots_raw else {}

    publish_str = raw_json.get("docPublishDate") or raw_json.get("last_PublishDate")
    sub_end_str = safe_get(raw_json, "procedureInfo", "collecting", "endDate")

    tender_dict = {
        "purchase_number": purchase_number,
        "max_price": first_lot.get("maxPrice"),
        "currency": safe_get(first_lot, "currency", "code"),
        "publish_date": parse_dt(publish_str),
        "submission_end": parse_dt(sub_end_str),
        "fz": raw_json.get("fz"),
        "placing_way_code": safe_get(raw_json, "placingWay", "code"),
        "status": raw_json.get("tender_stage_placement"),
        "customer_inn": safe_get(raw_json, "purchaseResponsible", "responsibleOrg", "INN"),
        "customer_name": safe_get(raw_json, "purchaseResponsible", "responsibleOrg", "fullName"),
        "region": raw_json.get("customer_region_name_for_user_view"),
        "raw_data": raw_json
    }

    stmt = insert(Tender).values(**tender_dict)
    stmt = stmt.on_conflict_do_update(
        index_elements=["purchase_number"],
        set_={k: stmt.excluded[k] for k in tender_dict if k != "purchase_number"}
    )
    await session.execute(stmt)
    await session.flush()

    tender = (await session.execute(
        select(Tender).where(Tender.purchase_number == purchase_number)
    )).scalar_one()

    await upsert_lots(session, tender.id, lots_raw)
    logger.info("Успешно сохранён/обновлён тендер %s, лотов: %d", purchase_number, len(lots_raw))
    return tender


async def ingest_tender_safe(session: AsyncSession, raw_json: dict) -> Tender:
    """Обёртка в транзакцию: либо всё, либо ничего"""
    async with session.begin():
        tender = await upsert_tender(session, raw_json)
    return tender