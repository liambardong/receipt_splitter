from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base, generate_uuid


class Item(Base):
    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    receipt_id = Column(String(36), ForeignKey("receipts.id"), nullable=False)
    name = Column(String(255), nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    notes = Column(String(512), nullable=True)

    # Relationships
    receipt = relationship("Receipt", back_populates="items")
    assignments = relationship("ItemAssignment", back_populates="item", cascade="all, delete-orphan")
