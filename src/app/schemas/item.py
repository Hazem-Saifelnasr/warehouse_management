# src/app/schemas/item.py

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ItemCreate(BaseModel):
    item_code: str
    name: str
    unified_code: Optional[str] = None
    description: str
    photo: Optional[str] = None  # Default to None if not provided
    unit_of_measure: str

    category: Optional[str] = None  # Main category of the item
    subcategory: Optional[str] = None  # Subcategory of the item
    brand: Optional[str] = None  # Brand or manufacturer
    model: Optional[str] = None  # Model number or name
    serial_number: Optional[str] = None  # Serial number (if applicable)

    bar_code: Optional[int] = None
    qr_code: Optional[str] = None
    remarks: Optional[str] = None

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


class ItemResponse(BaseModel):
    id: int
    item_code: str
    name: str
    unified_code: Optional[str] = None
    description: str
    photo: Optional[str] = None  # Default to None if not provided
    unit_of_measure: str

    category: Optional[str] = None  # Main category of the item
    subcategory: Optional[str] = None  # Subcategory of the item
    brand: Optional[str] = None  # Brand or manufacturer
    model: Optional[str] = None  # Model number or name
    serial_number: Optional[str] = None  # Serial number (if applicable)

    bar_code: Optional[int] = None
    qr_code: Optional[str] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True  # Enable ORM compatibility
