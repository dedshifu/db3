from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Numeric, DateTime, Boolean, BigInteger, func, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class TenderDetail(Base):
    """Детальная карточка закупки. Хранит метрики + полный JSON для аналитики"""
    __tablename__ = "tender_details"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    purchase_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    fz: Mapped[Optional[str]] = mapped_column(String(10), default="fz44")
    
    purchase_object_info: Mapped[Optional[str]] = mapped_column(Text)
    tender_price: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    
    collecting_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    collecting_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    summarizing_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    etp_name: Mapped[Optional[str]] = mapped_column(String(1000))
    etp_url: Mapped[Optional[str]] = mapped_column(String(300))
    customer_inn: Mapped[Optional[str]] = mapped_column(String(12), index=True)
    placing_way_name: Mapped[Optional[str]] = mapped_column(String(100))
    lots_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    is_goz: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB, comment="Полный ответ API для экспресс-оценки")
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    ingested_at: Mapped[Optional[datetime]]

    __table_args__ = (
        {"comment": "Детальные карточки закупок 44-ФЗ"},
    )