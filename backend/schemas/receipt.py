from pydantic import BaseModel
from datetime import date


class ReceiptBase(BaseModel):
    name: str
    date: date
    tax_amount: float = 0.0
    tip_amount: float = 0.0
    tax_split_method: str = "proportional"


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptResponse(ReceiptBase):
    id: str

    class Config:
        from_attributes = True
