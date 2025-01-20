# src/app/services/login.py

from fastapi import Response, Depends, Form
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from starlette.responses import RedirectResponse
from src.app.core.security import create_access_token
from src.app.services.auth_service import authenticate_user
from src.app.services.user_service import UserService


session_store = {}


class LoginService:
    @staticmethod
    def login_user(
            username: str = Form(...),
            password: str = Form(...),
            response: Response = None,
            db: Session = Depends(get_db),
    ):
        user = authenticate_user(username, password, db)

        if user.is_superuser:
            session_token = create_access_token({"sub": user.username, "role": "superuser", "id": user.id})
        else:
            session_token = create_access_token({"sub": user.username, "role": user.role, "id": user.id})

        redirect = RedirectResponse(url="/", status_code=303)
        redirect.set_cookie("session_token", session_token, httponly=True, secure=True, samesite="lax")
        return redirect

    @staticmethod
    def logout(response: Response):
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("session_token")
        return response
