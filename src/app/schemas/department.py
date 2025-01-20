# src/app/schemas/department.py

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class DepartmentCreate(BaseModel):
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


class DepartmentResponse(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Enable ORM compatibility


class DepartmentUpdate(BaseModel):
    name: str
    updated_at: Optional[datetime] = None
