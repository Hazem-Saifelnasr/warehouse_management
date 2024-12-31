# src/app/routers/users.py

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.services.user_service import UserService
from src.app.schemas.user import UserCreate, UserResponse

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="users", access_type="read")  # Highlight: Added decorator
def user_page(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users
    })


@router.post("/add", response_model=UserResponse)
@rbac_check(entity="users", access_type="create")  # Highlight: Added decorator
def create_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to create a new user. Admin access is required.
    """
    return UserService.create_user(db, user)


@router.get("/list", response_model=list[UserResponse])
@rbac_check(entity="users", access_type="read")  # Highlight: Added decorator
def get_users(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a list of users with pagination.
    """
    return UserService.list_users(db)


@router.get("/{user_id}", response_model=UserResponse)
@rbac_check(entity="users", access_type="read")  # Highlight: Added decorator
def get_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a user by ID.
    """
    return UserService.get_user_by_id(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
@rbac_check(entity="users", access_type="write")  # Highlight: Added decorator
def update_user(request: Request, user_id: int, update_data: dict, db: Session = Depends(get_db)):
    """
    Endpoint to update user details.
    """
    return UserService.update_user(db, user_id, update_data)


@router.delete("/{user_id}")
@rbac_check(entity="users", access_type="delete")  # Highlight: Added decorator
def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to delete a user by ID. Admin access is required.
    """
    return UserService.delete_user(db, user_id)
