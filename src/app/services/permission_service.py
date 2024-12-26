# src/app/services/permission_service.py

from sqlalchemy import or_
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
    def assign_permissions_bulk(db: Session, permissions_data: list[PermissionCreate]):
        new_permissions = []
        for permission_data in permissions_data:
            existing_permission = db.query(Permission).filter(
                Permission.user_id == permission_data.user_id,
                Permission.entity == permission_data.entity,
                Permission.entity_id == permission_data.entity_id,
                Permission.access_type == permission_data.access_type
            ).first()

            if not existing_permission:
                new_permission = Permission(**dict(permission_data))
                db.add(new_permission)
                new_permissions.append(new_permission)

        db.commit()
        return new_permissions

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

    @staticmethod
    def get_permissions(db: Session, entity: str, entity_id: str):
        return db.query(Permission).filter(
            or_(Permission.entity == entity, Permission.entity == "*"),
            or_(Permission.entity_id == entity_id, Permission.entity_id == "*")
        ).all()

    @staticmethod
    def get_permissions_by_warehouse(db: Session, warehouse_id: int):
        return PermissionService.get_permissions(db, "warehouse", str(warehouse_id))

    @staticmethod
    def get_permissions_by_project(db: Session, project_id: int):
        return PermissionService.get_permissions(db, "project", str(project_id))

    @staticmethod
    def get_permissions_by_location(db: Session, location_id: int):
        return PermissionService.get_permissions(db, "location", str(location_id))
