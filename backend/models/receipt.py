from sqlalchemy import Column, String, Float, Date
from sqlalchemy.orm import relationship
from database import Base, generate_uuid

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(String(36), primary_key=True, default=generate_uuid)

    
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)

    tax_amount = Column(Float, default=0.0)
    tip_amount = Column(Float, default=0.0)
    tax_split_method = Column(String(20), default="proportional")

    items = relationship("Item", back_populates="receipt", cascade="all, delete-orphan")
    participants = relationship("ReceiptParticipants", back_populates="receipt", cascade="all, delete-orphan")
