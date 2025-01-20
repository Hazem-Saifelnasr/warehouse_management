# src/app/schemas/location.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LocationCreate(BaseModel):

    name: str

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


class LocationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None  # Default to None if not provided

    class Config:
        from_attributes = True  # Enable ORM compatibility
