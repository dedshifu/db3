from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import Index, Computed, String, Numeric, DateTime, BigInteger, ForeignKey, func, Text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Tender(Base):
    __tablename__ = "tenders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    purchase_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    max_price: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(3))
    publish_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    submission_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    fz: Mapped[Optional[str]] = mapped_column(String(10), index=True)
    placing_way_code: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    customer_inn: Mapped[Optional[str]] = mapped_column(String(12), index=True)
    customer_name: Mapped[Optional[str]] = mapped_column(String(300), index=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Полнотекстовый поиск через generated column (без Mapped для Computed с TSVECTOR)
    search_vector = mapped_column(
        TSVECTOR,
        Computed(
            "to_tsvector('russian', coalesce(customer_name,'') || ' ' || coalesce(purchase_number,'') || ' ' || coalesce(raw_data->>'purchaseObjectInfo',''))",
            persisted=True
        ),
        index=False  # Индекс создаётся отдельно в __table_args__
    )

    # Временные метки
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    ingested_at: Mapped[Optional[datetime]]

    lots: Mapped[List["Lot"]] = relationship(back_populates="tender", cascade="all, delete-orphan", lazy="raise")

    __table_args__ = (
        Index("idx_tender_search_vector_gin", "search_vector", postgresql_using="gin"),
        Index("idx_tender_raw_gin", "raw_data", postgresql_using="gin"),
        # Оптимизированные индексы под реальные запросы
        Index("idx_open_tenders", "submission_end", "publish_date", postgresql_where="submission_end > NOW()"),
        Index("idx_tender_filter", "fz", "region", "publish_date"),
    )


class Lot(Base):
    __tablename__ = "lots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False, index=True)
    lot_number: Mapped[int] = mapped_column(nullable=False)
    max_price: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(3))
    objects_description: Mapped[Optional[dict]] = mapped_column(JSONB, comment="КТРУ и характеристики")
    guarantee_info: Mapped[Optional[dict]] = mapped_column(JSONB, comment="Обеспечение заявки/контракта")

    tender: Mapped["Tender"] = relationship(back_populates="lots")

    __table_args__ = (
        Index("idx_lot_tender_lot", "tender_id", "lot_number", unique=True),
        Index("idx_lot_objects_gin", "objects_description", postgresql_using="gin"),
    )