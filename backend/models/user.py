from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base, generate_uuid


class User(Base):
    """App user (login/account). Can optionally link to a Person for receipt splitting."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # null if using OAuth only
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    person_id = Column(String(36), ForeignKey("people.id"), nullable=True)  # link to Person for "me" on receipts

    person = relationship("Person", backref="user")
