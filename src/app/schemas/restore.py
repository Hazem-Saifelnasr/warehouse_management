# src/app/schemas/restore.py

from pydantic import BaseModel


class EntityRestoreResponse(BaseModel):
    entity_type: str
    entity_id: int
    name: str
    is_archived: bool
    is_deleted: bool


class RestoreResponse(BaseModel):
    detail: str
