# src/app/schemas/user.py

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    employee_id: Optional[int]
    username: str
    email: EmailStr
    password: str
    role: Optional[str]


class UserResponse(BaseModel):
    id: int
    employee_id: Optional[int]
    username: str
    email: EmailStr
    role: Optional[str] = "user"  # Default role

    class Config:
        from_attributes = True  # Enable ORM compatibility
