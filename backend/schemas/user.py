from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: Optional[str] = None
    person_id: Optional[str] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    person_id: Optional[str] = None

    class Config:
        from_attributes = True
