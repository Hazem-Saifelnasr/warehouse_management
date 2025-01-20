# src/app/routers/stock.py

from fastapi import APIRouter, Request, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models import Permission, User
from src.app.services.stock_service import StockService
from src.app.schemas.stock import StockCreate, StockDeduct, StockResponse, StockTransfer
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
def stock_page(request: Request, db: Session = Depends(get_db), page: int = 1, size: int = 10):
    try:
        stocks_query = db.query(Stock).options(
            joinedload(Stock.item),  # Load related Item model
            joinedload(Stock.project)  # Load related Project model
            .joinedload(Project.location),  # Load Location via Project
            joinedload(Stock.warehouse)  # Load related Warehouse model
            .joinedload(Warehouse.location),  # Load Location via Warehouse
        )

        total_stock = stocks_query.count()  # Total number of items
        offset = (page - 1) * size
        total_pages = (total_stock + size - 1) // size  # Calculate total pages

        user = db.query(User).filter(User.id == request.state.user_id).first()
        if user.role == "admin" or user.is_superuser:
            stocks = stocks_query.offset(offset).limit(size).all()
        else:
            # Query user permissions
            permissions = db.query(Permission).filter(Permission.user_id == request.state.user_id).all()

            # Initialize project and warehouse IDs
            project_ids = []
            warehouse_ids = []

            # Process permissions
            for perm in permissions:
                if perm.entity == "*":
                    project_ids = [proj.id for proj in db.query(Project.id).all()]
                    warehouse_ids = [wh.id for wh in db.query(Warehouse.id).all()]
                else:
                    if perm.entity == "project" and perm.access_type in {"READ", "ALL"}:
                        if perm.entity_id == "*":
                            # Global project access: fetch all project IDs
                            project_ids = [proj.id for proj in db.query(Project.id).all()]
                            break  # No need to process further; user has access to all projects
                        else:
                            project_ids.append(int(perm.entity_id))

                    if perm.entity == "warehouse" and perm.access_type in {"READ", "ALL"}:
                        if perm.entity_id == "*":
                            # Global warehouse access: fetch all warehouse IDs
                            warehouse_ids = [wh.id for wh in db.query(Warehouse.id).all()]
                            break  # No need to process further; user has access to all warehouses
                        else:
                            warehouse_ids.append(int(perm.entity_id))

            # Filter stocks by permitted project or warehouse IDs
            stocks = stocks_query.filter(
                or_(
                    Stock.project_id.in_(project_ids) if project_ids else False,
                    # Include project filter only if there are IDs
                    Stock.warehouse_id.in_(warehouse_ids) if warehouse_ids else False
                    # Include warehouse filter only if there are IDs
                )
            ).offset(offset).limit(size).all()

        items = db.query(Item).filter(Item.is_active == True).all()
        projects = db.query(Project).filter(Project.is_active == True).all()
        warehouses = db.query(Warehouse).filter(Warehouse.is_active == True).all()
        locations = db.query(Location).filter(Location.is_active == True).all()
    except Exception as e:
        return templates.TemplateResponse("error.html", {"request": request, "message": str(e)})
    return templates.TemplateResponse("stocks.html", {
        "request": request,
        "stocks": stocks,
        "items": items,
        "projects": projects,
        "warehouses": warehouses,
        "locations": locations,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "user_id": request.state.user_id,
        "user_role": request.state.role
    })


@router.post("/add", response_model=StockResponse)
@rbac_check(entity="stocks", access_type="write")  # Highlight: Added decorator
def add_stock(request: Request, stock: StockCreate, db: Session = Depends(get_db)):
    return StockService.add_stock(stock, request.state.user_id, db)


@router.post("/deduct", response_model=list[StockResponse])
@rbac_check(entity="stocks", access_type="write")  # Highlight: Added decorator
def deduct_stock(request: Request, stock: StockDeduct, db: Session = Depends(get_db)):
    return StockService.deduct_stock(stock, request.state.user_id, db)


@router.post("/transfer", response_model=StockResponse)
@rbac_check(entity="stocks", access_type="write")  # Highlight: Added decorator
def transfer_stock(request: Request, stock: StockTransfer, db: Session = Depends(get_db)):
    return StockService.transfer_stock(stock, request.state.user_id, db)


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
