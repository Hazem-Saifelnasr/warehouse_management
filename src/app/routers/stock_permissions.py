# src/app/routers/invoices.py

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models.invoice import Invoice
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="stock_permissions", access_type="read")  # Highlight: Added decorator
def stock_permissions_page(request: Request, db: Session = Depends(get_db)):
    stock_permissions = db.query(Invoice).all()
    return templates.TemplateResponse("stock_permissions.html", {
        "request": request,
        "stock_permissions": stock_permissions,
        "user_id": request.state.user_id,
        "user_role": request.state.role
    })
