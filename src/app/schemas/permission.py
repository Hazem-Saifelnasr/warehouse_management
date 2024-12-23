# src/app/schemas/permission.py

from pydantic import BaseModel


class PermissionCreate(BaseModel):
    user_id: int
    entity: str
    entity_id: int
    access_type: str


class PermissionResponse(BaseModel):
    id: int
    user_id: int
    entity: str
    entity_id: int
    access_type: str

    class Config:
        from_attributes = True  # Enable ORM compatibility
