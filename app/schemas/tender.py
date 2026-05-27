from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class LotOut(BaseModel):
    id: int
    lot_number: int
    max_price: Optional[float] = None
    currency: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TenderOut(BaseModel):
    id: int
    purchase_number: str
    max_price: Optional[float] = None
    currency: Optional[str] = None
    publish_date: Optional[datetime] = None
    fz: Optional[str] = None
    status: Optional[str] = None
    customer_inn: Optional[str] = None
    lots: List[LotOut] = []

    model_config = ConfigDict(from_attributes=True)