from sqlalchemy import Column, ForeignKey, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base, generate_uuid


class ReceiptParticipants(Base):
    __tablename__ = "receipt_participants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    receipt_id = Column(String(36), ForeignKey("receipts.id"), nullable=False)
    person_id = Column(String(36), ForeignKey("people.id"), nullable=False)
    paid = Column(Boolean, default=False, nullable=False)
    paid_at = Column(DateTime, nullable=True)  # when they were marked as paid

    # Relationships
    receipt = relationship("Receipt", back_populates="participants")
    person = relationship("Person", back_populates="participations")
