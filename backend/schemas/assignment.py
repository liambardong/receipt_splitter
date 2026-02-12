from pydantic import BaseModel

from .person import PersonResponse


class AssignmentAdd(BaseModel):
    person_id: str


class AssignmentResponse(BaseModel):
    id: str
    item_id: str
    person_id: str
    person: PersonResponse

    class Config:
        from_attributes = True
