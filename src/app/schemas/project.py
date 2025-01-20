# src/app/schemas/project.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    budget: Optional[float] = None
    description: Optional[str] = None
    location_id: int

    # Approval and archiving
    is_approved: Optional[bool] = False
    approval_status: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None

    is_archived: Optional[bool] = False
    archived_at: Optional[datetime] = None
    archived_by: Optional[int] = None

    # Soft delete
    is_deleted: Optional[bool] = False

    is_active: Optional[bool] = False

    # Audit fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    budget: Optional[float] = None
    description: Optional[str] = None
    location_id: int

    class Config:
        from_attributes = True  # Enable ORM compatibility


class ProjectUpdate(BaseModel):
    name: str
    budget: Optional[float] = None
    description: Optional[str] = None
    location_id: int
