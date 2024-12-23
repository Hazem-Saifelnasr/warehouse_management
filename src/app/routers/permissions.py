# src/app/routers/permissions.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.services.permission_service import PermissionService
from src.app.schemas.permission import PermissionCreate, PermissionResponse

router = APIRouter()


@router.post("/", response_model=PermissionResponse)
def assign_permission(permission: PermissionCreate, db: Session = Depends(get_db)):
    """
    Endpoint to assign a permission to a user for a specific entity (project or warehouse).
    """
    return PermissionService.assign_permission(db, permission)


@router.delete("/{permission_id}")
def revoke_permission(permission_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to revoke a specific permission by its ID.
    """
    return PermissionService.revoke_permission(db, permission_id)


@router.get("/user/{user_id}", response_model=list[PermissionResponse])
def get_permissions_for_user(user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to list all permissions assigned to a specific user.
    """
    return PermissionService.get_permissions_by_user(db, user_id)
