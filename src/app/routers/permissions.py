# src/app/routers/permissions.py

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy import case, cast, Integer
from sqlalchemy.orm import Session, joinedload
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models.user import User
from src.app.models.item import Item
from src.app.models.location import Location
from src.app.models.permission import Permission
from src.app.models.project import Project
from src.app.models.warehouse import Warehouse
from src.app.services.permission_service import PermissionService
from src.app.schemas.permission import PermissionCreate, PermissionResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.app.utils.error_handler import error_page

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="permissions", access_type="read")  # Highlight: Added decorator
def permissions_page(request: Request, db: Session = Depends(get_db)):
    permissions = (
        db.query(
            Permission.id,
            Permission.access_type,
            User.username.label("user_name"),
            Permission.entity,
            Permission.entity_id,
            case(
                (Permission.entity == "items",
                 db.query(Item.item_code)
                 .filter(Item.id == cast(Permission.entity_id, Integer))
                 .correlate(Permission).scalar_subquery()),
                (Permission.entity == "projects",
                 db.query(Project.project_name)
                 .filter(Project.id == cast(Permission.entity_id, Integer))
                 .correlate(Permission).scalar_subquery()),
                (Permission.entity == "warehouses",
                 db.query(Warehouse.name)
                 .filter(Warehouse.id == cast(Permission.entity_id, Integer))
                 .correlate(Permission).scalar_subquery()),
                (Permission.entity == "locations",
                 db.query(Location.name)
                 .filter(Location.id == cast(Permission.entity_id, Integer))
                 .correlate(Permission).scalar_subquery()),
                else_="Unknown",
            ).label("entity_name"),
        )
        .join(User, Permission.user_id == User.id)
    )

    # Retrieve user's permissions
    user_permissions = db.query(Permission).filter(Permission.user_id == request.state.user_id).all()

    if db.query(User).filter(User.id == request.state.user_id).first():
        user_permissions_list = [
            {"entity": "*", "entity_id": "*", "access_type": "*"}
        ]
    elif user_permissions:
        user_permissions_list = [
            {"entity": perm.entity, "entity_id": perm.entity_id, "access_type": perm.access_type}
            for perm in user_permissions
        ]
    else:
        user_permissions_list = {}

    users = db.query(User).all()
    items = db.query(Item).all()
    projects = db.query(Project).all()
    warehouses = db.query(Warehouse).all()
    locations = db.query(Location).all()
    access_types = ["read", "write", "delete", "create", "manage", "assign", "export", "approve",
                    "revoke", "archive", "restore", "share", "execute", "*"]

    return templates.TemplateResponse("permissions.html", {
        "request": request,
        "permissions": permissions,
        "user_permissions": user_permissions_list,  # Pass permissions to the template
        "users": users,
        "items": items,
        "projects": projects,
        "warehouses": warehouses,
        "locations": locations,
        "access_types": access_types
    })


@router.post("/add", response_model=PermissionResponse)
@rbac_check(entity="permissions", access_type="create")  # Highlight: Added decorator
def assign_permission(request: Request, permission: PermissionCreate, db: Session = Depends(get_db)):
    """
    Endpoint to assign a permission to a user for a specific entity (project or warehouse).
    """
    return PermissionService.assign_permission(db, permission)


@router.post("/bulk", response_model=list[PermissionResponse])
@rbac_check(entity="permissions", access_type="create")  # Highlight: Added decorator
def assign_permission(request: Request, permissions: list[PermissionCreate], db: Session = Depends(get_db)):
    """
    Endpoint to assign multiple permissions in bulk to users.
    """
    if not permissions:
        return error_page(request, 400, "Permissions list cannot be empty")
    return PermissionService.assign_permissions_bulk(db, permissions)


@router.delete("/{permission_id}")
@rbac_check(entity="permissions", access_type="delete")  # Highlight: Added decorator
def revoke_permission(request: Request, permission_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to revoke a specific permission by its ID.
    """
    return PermissionService.revoke_permission(db, permission_id)


@router.get("/user/{user_id}", response_model=list[PermissionResponse])
@rbac_check(entity="permissions", access_type="read")  # Highlight: Added decorator
def get_permissions_for_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to list all permissions assigned to a specific user.
    """
    return PermissionService.get_permissions_by_user(db, user_id)


@router.get("/warehouse/{warehouse_id}", response_model=list[PermissionResponse])
@rbac_check(entity="permissions", access_type="read")  # Highlight: Added decorator
def get_permissions_by_warehouse(request: Request, warehouse_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to list all permissions assigned to a specific warehouse.
    """
    return PermissionService.get_permissions_by_warehouse(db, warehouse_id)


@router.get("/project/{project_id}", response_model=list[PermissionResponse])
@rbac_check(entity="permissions", access_type="read")  # Highlight: Added decorator
def get_permissions_by_project(request: Request, project_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to list all permissions assigned to a specific project.
    """
    return PermissionService.get_permissions_by_project(db, project_id)


@router.get("/location/{location_id}", response_model=list[PermissionResponse])
@rbac_check(entity="permissions", access_type="read")  # Highlight: Added decorator
def get_permissions_by_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to list all permissions assigned to a specific location.
    """
    return PermissionService.get_permissions_by_location(db, location_id)
