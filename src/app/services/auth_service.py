# src/app/services/auth_service.py

from fastapi import HTTPException
from src.app.models.user import User
from src.app.core.security import verify_password


def authenticate_user(db, username: str, password: str):
    # Validate input
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user
