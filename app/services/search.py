"""Сервис поиска тендеров с полнотекстовым запросом"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tender import Tender


async def search_tenders(
    session: AsyncSession,
    query: str = "",
    only_open: bool = True,
    region: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    fz: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> Tuple[List[dict], int]:
    """
    Поиск тендеров с фильтрами и полнотекстовым поиском
    Возвращает список словарей и общее количество
    """
    conditions = []
    
   
    if only_open:
        now = datetime.now(timezone.utc)
        conditions.append(or_(
            Tender.submission_end.is_(None),
            Tender.submission_end > now
        ))
    
    
    if region is not None:
        conditions.append(Tender.region == region)
    if min_price is not None:
        conditions.append(Tender.max_price >= min_price)
    if max_price is not None:
        conditions.append(Tender.max_price <= max_price)
    if fz is not None:
        conditions.append(Tender.fz == fz)
    if status is not None:
        conditions.append(Tender.status == status)
    
   
    base_query = select(Tender).where(*conditions) if conditions else select(Tender)
    
   
    if query.strip():
       
        ts_query = func.to_tsquery(
            "russian", 
            query.replace("&", " & ").replace("|", " | ").strip()
        )
        
        search_vector = func.to_tsvector("russian", 
            func.coalesce(Tender.customer_name, "") + " " + 
            func.coalesce(Tender.purchase_number, "")
        )
        base_query = base_query.where(search_vector.op("@@")(ts_query))
    
   
    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await session.execute(count_query)).scalar() or 0
    
   
    results_query = base_query.order_by(
        Tender.publish_date.desc(), 
        Tender.id.desc()
    ).limit(limit).offset(offset)
    
    tenders = (await session.execute(results_query)).scalars().all()
    
   
    results = []
    for t in tenders:
        item = t.__dict__.copy()
        item.pop("search_vector", None)  
        item.pop("_sa_instance_state", None)
        results.append(item)
    
    return results, total


async def get_tender_by_purchase_number(
    session: AsyncSession, 
    purchase_number: str
) -> Optional[dict]:
    """Получение тендера по номеру закупки"""
    result = await session.execute(
        select(Tender).where(Tender.purchase_number == purchase_number)
    )
    tender = result.scalar_one_or_none()
    if tender is None:
        return None
    item = tender.__dict__.copy()
    item.pop("search_vector", None)
    item.pop("_sa_instance_state", None)
    return item