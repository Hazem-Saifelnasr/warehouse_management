# src/app/schemas/permission.py

from pydantic import BaseModel
from typing import Optional


class PermissionCreate(BaseModel):
    user_id: int
    entity: str
    entity_id: str
    access_type: str


class PermissionResponse(BaseModel):
    id: int
    user_id: int
    entity: str
    entity_id: str
    access_type: str

    class Config:
        from_attributes = True  # Enable ORM compatibility


class PermissionUpdate(BaseModel):
    entity: Optional[str]
    entity_id: Optional[int]
    access_type: Optional[str]
