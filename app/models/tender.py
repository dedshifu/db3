from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Numeric, DateTime, Index, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
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

    lots = relationship("Lot", back_populates="tender", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index("idx_tender_search", "publish_date", "max_price", "customer_inn", "fz"),
        Index("idx_tender_raw_gin", "raw_data", postgresql_using="gin"),
    )


class Lot(Base):
    __tablename__ = "lots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False)
    lot_number: Mapped[int] = mapped_column(nullable=False)
    max_price: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    currency: Mapped[Optional[str]] = mapped_column(String(3))
    objects_description: Mapped[Optional[dict]] = mapped_column(JSONB, comment="КТРУ и характеристики")
    guarantee_info: Mapped[Optional[dict]] = mapped_column(JSONB, comment="Обеспечение заявки/контракта")

    tender = relationship("Tender", back_populates="lots")

    __table_args__ = (
        Index("idx_lot_tender_lot", "tender_id", "lot_number", unique=True),
        Index("idx_lot_objects_gin", "objects_description", postgresql_using="gin"),
    )