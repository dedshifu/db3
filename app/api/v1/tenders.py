import logging
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.ingest import ingest_tender_safe
from app.schemas.tender import TenderOut

router = APIRouter(prefix="/tenders", tags=["tenders"])
logger = logging.getLogger(__name__)


@router.post("/ingest", response_model=TenderOut, status_code=201)
async def ingest_tender_endpoint(
    raw_json: dict = Body(...),
    session: AsyncSession = Depends(get_db)
):
    """Принимает сырой JSON от ЕИС, валидирует, сохраняет/обновляет в БД."""
    try:
        purchase_num = raw_json.get("purchaseNumber", "unknown")
        logger.info("Начало импорта тендера", extra={"purchase_number": purchase_num})
        tender = await ingest_tender_safe(session, raw_json)
        return TenderOut.model_validate(tender)
    except ValueError as ve:
        logger.error("Ошибка валидации данных импорта", exc_info=True)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error("Критическая ошибка импорта", exc_info=True, extra={"snippet": str(raw_json)[:150]})
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при импорте")