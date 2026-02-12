from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    name: str
    receipt_id: str
    unit_price: float
    quantity: int
    notes: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: str

    class Config:
        from_attributes = True
