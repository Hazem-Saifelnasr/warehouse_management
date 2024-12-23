# src/app/services/permission_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.app.models.permission import Permission
from src.app.schemas.permission import PermissionCreate


class PermissionService:
    @staticmethod
    def assign_permission(db: Session, permission_data: PermissionCreate):
        # Check if the user already has this permission
        existing_permission = db.query(Permission).filter(
            Permission.user_id == permission_data.user_id,
            Permission.entity == permission_data.entity,
            Permission.entity_id == permission_data.entity_id,
            Permission.access_type == permission_data.access_type
        ).first()

        if existing_permission:
            raise HTTPException(status_code=400, detail="Permission already assigned")

        # Create a new permission
        new_permission = Permission(**dict(permission_data))
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)
        return new_permission

    @staticmethod
    def revoke_permission(db: Session, permission_id: int):
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        db.delete(permission)
        db.commit()
        return {"detail": "Permission revoked successfully"}

    @staticmethod
    def get_permissions_by_user(db: Session, user_id: int):
        permissions = db.query(Permission).filter(Permission.user_id == user_id).all()
        return permissions
