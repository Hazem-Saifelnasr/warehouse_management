# src/app/services/auth_service.py

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.models.user import User
from src.app.core.security import verify_password


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    # Validate input
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User not yet activated")
    return user
