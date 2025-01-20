# src/app/routers/users.py

from typing import Union
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session, joinedload
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.app.models import Department
from src.app.models.user import User
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.schemas.pending_approval import PendingApprovalResponse
from src.app.services.user_service import UserService
from src.app.schemas.user import UserCreate, UserResponse

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="users", access_type="read")  
def user_page(request: Request, db: Session = Depends(get_db), page: int = 1, size: int = 10):
    users_query = db.query(User).options(
        joinedload(User.department),  # Eager load the department relationship
        joinedload(User.direct_manager)  # Eager load the direct manager relationship
    ).filter(User.is_active == True)
    total_users = users_query.count()  # Total number of items
    offset = (page - 1) * size
    total_pages = (total_users + size - 1) // size  # Calculate total pages
    users = users_query.offset(offset).limit(size).all()
    departments = db.query(Department).filter(Department.is_active == True)
    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users,
        "departments": departments,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "user_id": request.state.user_id,
        "user_role": request.state.role
    })


@router.post("/add", response_model=Union[UserResponse, PendingApprovalResponse])
@rbac_check(entity="users", access_type="create")  
def create_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    return UserService.create_user(user, request.state.user_id, db)


@router.get("/list", response_model=list[UserResponse])
@rbac_check(entity="users", access_type="read")
def list_users(request: Request, db: Session = Depends(get_db)):
    return UserService.list_users(db)


@router.put("/{user_id}", response_model=Union[UserResponse, PendingApprovalResponse])
@rbac_check(entity="users", access_type="write")
def update_user(request: Request, user_id: int, update_data: dict, db: Session = Depends(get_db)):
    return UserService.update_user(user_id, update_data, request.state.user_id, db)


@router.delete("/{user_id}")
@rbac_check(entity="users", access_type="delete")
def delete_user_soft(request: Request, user_id: int, db: Session = Depends(get_db)):
    return UserService.delete_user_soft(user_id, request.state.user_id, db)


@router.delete("/permanent/{user_id}")
@rbac_check(entity="users", access_type="delete")
def delete_user_permanent(request: Request, user_id: int, db: Session = Depends(get_db)):
    return UserService.delete_user_permanent(user_id, request.state.user_id, db)


@router.post("/archive/{user_id}")
@rbac_check(entity="users", access_type="archive")
def archive_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    return UserService.archive_user(user_id, request.state.user_id, db)


@router.post("/restore/{user_id}")
@rbac_check(entity="users", access_type="restore")
def restore_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    return UserService.restore_user(user_id, request.state.user_id, db)


@router.get("/{user_id}", response_model=UserResponse)
@rbac_check(entity="users", access_type="read")
def get_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    return UserService.get_user_by_id(user_id, db)
