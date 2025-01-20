# src/app/routers/login.py

from fastapi import APIRouter, Request, Response, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.services.login_service import LoginService

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
def login_user(username: str = Form(...), password: str = Form(...), response: Response = None,
               db: Session = Depends(get_db)):
    return LoginService.login_user(username, password, response, db)


@router.get("/logout", response_class=HTMLResponse)
def logout(response: Response):
    return LoginService.logout(response)
