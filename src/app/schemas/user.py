# src/app/schemas/user.py
from datetime import datetime

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    employee_id: int
    name: Optional[int] = None
    username: str
    email: EmailStr
    password: str

    position: Optional[str] = None
    department_id: Optional[int] = None
    direct_manager_id: Optional[int] = None
    role: Optional[str] = "user"

    is_superuser: Optional[bool] = False

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


class UserResponse(BaseModel):
    id: int
    employee_id: int
    name: Optional[int] = None
    username: str
    email: EmailStr
    position: Optional[str] = None
    department_id: Optional[int] = None
    direct_manager_id: Optional[int] = None
    role: Optional[str] = "user"  # Default role

    class Config:
        from_attributes = True  # Enable ORM compatibility
