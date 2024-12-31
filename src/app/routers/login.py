from fastapi import APIRouter, Request, Response, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from starlette.responses import RedirectResponse
from src.app.core.security import create_access_token
from src.app.services.user_service import UserService

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")

# Session simulation for demo (use a proper session store in production)
session_store = {}


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
def login_user(
        username: str = Form(...),
        password: str = Form(...),
        response: Response = None,
        db: Session = Depends(get_db),
):
    user = UserService.authenticate_user(db, username, password)

    session_token = create_access_token({"sub": user.username, "role": user.role, "id": user.id})

    redirect = RedirectResponse(url="/", status_code=303)
    redirect.set_cookie("session_token", session_token, httponly=True)
    return redirect


@router.get("/logout", response_class=HTMLResponse)
def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_token")
    return response
