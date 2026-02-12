from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .person import PersonResponse


class ParticipantAdd(BaseModel):
    person_id: str


class ParticipantUpdate(BaseModel):
    paid: bool


class ParticipantResponse(BaseModel):
    person: PersonResponse
    paid: bool = False
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True
