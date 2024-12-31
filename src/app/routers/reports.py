# src/app/routers/reports.py

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.services.report_service import ReportService

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="reports", access_type="read")  # Highlight: Added decorator
def reports_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("reports.html", {"request": request})


@router.get("/list")
@rbac_check(entity="reports", access_type="read")  # Highlight: Added decorator
def list_reports(request: Request, db: Session = Depends(get_db)):
    return ReportService.list_reports()


@router.post("/generate")
@rbac_check(entity="reports", access_type="create")  # Highlight: Added decorator
def generate_report(request: Request, db: Session = Depends(get_db)):
    return ReportService.generate_report(db)


@router.get("/{entity_type}")
@rbac_check(entity="reports", access_type="read")  # Highlight: Added decorator
def entity_report(request: Request, entity_type: str, db: Session = Depends(get_db)):
    return ReportService.entity_report(entity_type, db)


@router.get("/stock/item/{item_id}")
@rbac_check(entity="reports", access_type="read")  # Highlight: Added decorator
def get_stock_by_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    return ReportService.get_stock_by_item(item_id, db)


@router.get("/stock/{entity_type}")
@rbac_check(entity="reports", access_type="read")  # Highlight: Added decorator
def get_stock_by_entity_type(request: Request, entity_type: str, db: Session = Depends(get_db)):
    return ReportService.get_stock_by_entity_type(entity_type, db)


@router.get("/stock/{entity_type}/{entity_id}")
@rbac_check(entity="reports", access_type="read")  # Highlight: Added decorator
def get_stock_by_entity_and_id(request: Request, entity_type: str, entity_id: int, db: Session = Depends(get_db)):
    return ReportService.get_stock_by_entity_and_id(entity_type, entity_id, db)


@router.delete("/delete")
@rbac_check(entity="reports", access_type="delete")  # Highlight: Added decorator
def delete_report(request: Request, data: dict, db: Session = Depends(get_db)):
    return ReportService.delete_report(data)
