from pydantic import BaseModel, computed_field
from typing import Optional


class PersonBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None


class PersonCreate(PersonBase):
    pass


class PersonResponse(PersonBase):
    id: str

    @computed_field
    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.first_name.strip()

    class Config:
        from_attributes = True
