from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from database import Base, generate_uuid


class ItemAssignment(Base):
    __tablename__ = "item_assignments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    item_id = Column(String(36), ForeignKey("items.id"), nullable=False)
    person_id = Column(String(36), ForeignKey("people.id"), nullable=False)

    # Relationships
    item = relationship("Item", back_populates="assignments")
    person = relationship("Person", back_populates="assignments")
