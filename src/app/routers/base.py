# src/app/routers/base.py

from src.app.core.config import get_settings, Settings
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.core.rbac import get_permissions_for_user, has_permission
from src.app.models.item import Item
from src.app.models.project import Project
from src.app.models.stock import Stock
from src.app.models.warehouse import Warehouse
from starlette.responses import RedirectResponse

from src.app.core.security import decode_access_token

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/health")
def health_check(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "status": "ok",
        "message": "server is running"
    }


@router.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    # Get the session_token from the cookie
    session_token = request.cookies.get("session_token")
    if not session_token:
        return RedirectResponse(url="/login", status_code=307)

    # Optionally, decode the token to access user info
    payload = decode_access_token(session_token)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_id": request.state.user_id,
        "user_role": request.state.role
    })


@router.get("/dashboard/metrics")
async def get_dashboard_metrics(request: Request, db: Session = Depends(get_db)):
    if not request.state.user:
        # raise HTTPException(status_code=401, detail="Not authenticated")
        return templates.TemplateResponse("error.html", {"request": request,"status_code": 401,
                                                         "message": "Not authenticated"})

    total_items = db.query(Item).filter(Item.is_active == True).count()
    total_warehouses = db.query(Warehouse).filter(Warehouse.is_active == True).count()
    total_projects = db.query(Project).filter(Project.is_active == True).count()
    total_stock = db.query(func.sum(Stock.quantity)).scalar() or 0

    # Stock distribution by warehouse/project
    stock_distribution = (
        db.query(
            func.coalesce(Warehouse.name, Project.name).label("entity_name"),
            func.sum(Stock.quantity).label("total_quantity"),
        )
        .outerjoin(Warehouse, Stock.warehouse_id == Warehouse.id)
        .outerjoin(Project, Stock.project_id == Project.id)
        .group_by("entity_name")
        .all()
    )

    distribution_data = {row.entity_name: row.total_quantity for row in stock_distribution}

    return {
        "total_items": total_items,
        "total_warehouses": total_warehouses,
        "total_projects": total_projects,
        "total_stock": total_stock,
        "stock_distribution": distribution_data,
    }
