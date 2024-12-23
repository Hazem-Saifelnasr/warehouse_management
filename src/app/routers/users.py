# src/app/routers/users.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.services.user_service import UserService
from src.app.schemas.user import UserCreate, UserResponse
from src.app.core.security import create_access_token

router = APIRouter()


@router.post("/create", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to create a new user. Admin access is required.
    """
    return UserService.create_user(db, user)


@router.post("/login")
def login_user(username: str, password: str, db: Session = Depends(get_db)):
    """
    Endpoint for user login. Returns a JWT token upon successful authentication.
    """
    user = UserService.authenticate_user(db, username, password)
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a user by ID.
    """
    return UserService.get_user_by_id(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, update_data: dict, db: Session = Depends(get_db)):
    """
    Endpoint to update user details.
    """
    return UserService.update_user(db, user_id, update_data)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to delete a user by ID. Admin access is required.
    """
    return UserService.delete_user(db, user_id)
