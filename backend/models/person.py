from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base, generate_uuid


class Person(Base):
    __tablename__ = "people"
    __table_args__ = (UniqueConstraint("first_name", "last_name", name="uq_people_first_last"),)

    id = Column(String(36), primary_key=True, default=generate_uuid)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)

    # Relationships
    participations = relationship("ReceiptParticipants", back_populates="person")
    assignments = relationship("ItemAssignment", back_populates="person")
