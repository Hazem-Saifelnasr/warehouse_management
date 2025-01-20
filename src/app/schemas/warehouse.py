# src/app/schemas/warehouse.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WarehouseCreate(BaseModel):
    name: str
    capacity: Optional[float] = None
    location_id: int
    description: Optional[str] = None

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


class WarehouseResponse(BaseModel):
    id: int
    name: str
    capacity: Optional[float] = None
    location_id: int
    description: Optional[str] = None

    class Config:
        from_attributes = True  # Enable ORM compatibility


class WarehouseUpdate(BaseModel):
    name: str
    capacity: Optional[float] = None
    location_id: int
    description: Optional[str] = None
