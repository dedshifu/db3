"""SQLAlchemy 2.0 модель для детальных закупок (response_*.json)"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from .base import Base

class TenderDetail(Base):
    """Детальная карточка закупки. Хранит метрики + полный JSON для аналитики"""
    __tablename__ = "tender_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    purchase_number = Column(String(50), unique=True, nullable=False, index=True)
    fz = Column(String(10), default="fz44")
    
    purchase_object_info = Column(String(3000))
    tender_price = Column(Numeric(18, 2))
    
    collecting_start = Column(DateTime(timezone=True))
    collecting_end = Column(DateTime(timezone=True), index=True)
    summarizing_date = Column(DateTime(timezone=True))
    
    etp_name = Column(String(1000))
    etp_url = Column(String(300))
    customer_inn = Column(String(12), index=True)
    placing_way_name = Column(String(100))
    lots_count = Column(Integer, default=0)
    is_goz = Column(Boolean, default=False)
    
    raw_data = Column(JSONB, comment="Полный ответ API для экспресс-оценки")
    
    __table_args__ = (
        Index("ix_details_purchase_number", "purchase_number"),
        Index("ix_details_collecting_end", "collecting_end"),
        Index("ix_details_customer_inn", "customer_inn"),
        {"comment": "Детальные карточки закупок 44-ФЗ"},
    )