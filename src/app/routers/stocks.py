# src/app/routers/stock.py

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session, joinedload
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.services.stock_service import StockService
from src.app.schemas.stock import StockCreate, StockDeduct, StockResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.models.stock import Stock
from src.app.models.item import Item
from src.app.models.project import Project
from src.app.models.warehouse import Warehouse
from src.app.models.location import Location

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="stocks", access_type="read")  # Highlight: Added decorator
def stock_page(request: Request, db: Session = Depends(get_db)):
    try:
        stocks = (
            db.query(Stock)
            .options(
                joinedload(Stock.item),  # Load related Item model
                joinedload(Stock.project)  # Load related Project model
                .joinedload(Project.location),  # Load Location via Project
                joinedload(Stock.warehouse)  # Load related Warehouse model
                .joinedload(Warehouse.location),  # Load Location via Warehouse
            )
            .all()
        )
        items = db.query(Item).all()
        projects = db.query(Project).all()
        warehouses = db.query(Warehouse).all()
        locations = db.query(Location).all()
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "message": str(e)})
    return templates.TemplateResponse("stocks.html", {
        "request": request,
        "stocks": stocks,
        "items": items,
        "projects": projects,
        "warehouses": warehouses,
        "locations": locations,
    })


@router.post("/add", response_model=StockResponse)
@rbac_check(entity="stocks", access_type="write")  # Highlight: Added decorator
def add_stock(request: Request, stock: StockCreate, db: Session = Depends(get_db)):
    return StockService.add_stock(db, stock.item_id, stock.project_id, stock.warehouse_id, stock.quantity)


@router.post("/deduct", response_model=list[StockResponse])
@rbac_check(entity="stocks", access_type="write")  # Highlight: Added decorator
def deduct_stock(request: Request, stock: StockDeduct, db: Session = Depends(get_db)):
    return StockService.deduct_stock(db, stock.item_id, stock.project_id, stock.warehouse_id, stock.quantity)


@router.post("/transfer", response_model=StockResponse)
@rbac_check(entity="stocks", access_type="write")  # Highlight: Added decorator
def transfer_stock(request: Request, item_id: int, from_project_id: int = None, to_project_id: int = None, from_warehouse_id: int = None,
                   to_warehouse_id: int = None, quantity: float = 0, db: Session = Depends(get_db)):
    return StockService.transfer_stock(
        db, item_id=item_id,
        from_project_id=from_project_id,
        to_project_id=to_project_id,
        from_warehouse_id=from_warehouse_id,
        to_warehouse_id=to_warehouse_id,
        quantity=quantity)


@router.get("/location/{location_id}", response_model=list[StockResponse])
@rbac_check(entity="stocks", access_type="read")  # Highlight: Added decorator
def get_items_by_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    """
    Retrieve stock items by location.
    """
    return StockService.get_stock_by_location_or_project_or_warehouse(db, location_id=location_id)


@router.get("/warehouse/{warehouse_id}", response_model=list[StockResponse])
@rbac_check(entity="stocks", access_type="read")  # Highlight: Added decorator
def get_items_by_warehouse(request: Request, warehouse_id: int, db: Session = Depends(get_db)):
    """
    Retrieve stock items by warehouse.
    """
    return StockService.get_stock_by_location_or_project_or_warehouse(db, warehouse_id=warehouse_id)


@router.get("/project/{project_id}", response_model=list[StockResponse])
@rbac_check(entity="stocks", access_type="read")  # Highlight: Added decorator
def get_items_by_project(request: Request, project_id: int, db: Session = Depends(get_db)):
    """
    Retrieve stock items by project.
    """
    return StockService.get_stock_by_location_or_project_or_warehouse(db, project_id=project_id)


@router.get("/item/{item_id}/location/{location_id}", response_model=list[StockResponse])
@rbac_check(entity="stocks", access_type="read")  # Highlight: Added decorator
def get_item_locations_and_quantities(request: Request, item_id: int, location_id: int, db: Session = Depends(get_db)):
    return StockService.get_stock_of_item_by_location_or_project_or_warehouse(
        db, item_id=item_id, location_id=location_id)


@router.get("/item/{item_id}/warehouse/{warehouse_id}", response_model=list[StockResponse])
@rbac_check(entity="stocks", access_type="read")  # Highlight: Added decorator
def get_item_locations_and_quantities(request: Request, item_id: int, warehouse_id: int, db: Session = Depends(get_db)):
    return StockService.get_stock_of_item_by_location_or_project_or_warehouse(
        db, item_id=item_id, warehouse_id=warehouse_id)


@router.get("/item/{item_id}/project/{project_id}", response_model=list[StockResponse])
@rbac_check(entity="stocks", access_type="read")  # Highlight: Added decorator
def get_item_locations_and_quantities(request: Request, item_id: int, project_id: int, db: Session = Depends(get_db)):
    return StockService.get_stock_of_item_by_location_or_project_or_warehouse(
        db, item_id=item_id, project_id=project_id)


@router.get("/item/{item_id}/locations", response_model=list[dict])
@rbac_check(entity="stocks", access_type="read")  # Highlight: Added decorator
def get_item_locations_and_quantities(request: Request, item_id: int, db: Session = Depends(get_db)):
    """
    Retrieve locations and quantities of an item across projects and warehouses.
    """
    return StockService.get_item_location_and_qty(db, item_id=item_id)


@router.get("/item/{item_id}/total", response_model=dict)
@rbac_check(entity="stocks", access_type="read")  # Highlight: Added decorator
def get_total_stock_by_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    """
    Retrieve total stock of an item across all locations.
    """
    return StockService.get_total_stock_by_item(db, item_id=item_id)
