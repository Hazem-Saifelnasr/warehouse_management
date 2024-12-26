# src/app/routers/stock.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.services.stock_service import StockService
from src.app.schemas.stock import StockCreate, StockDeduct, StockResponse

router = APIRouter()


@router.post("/add", response_model=StockResponse)
def add_stock(stock: StockCreate, db: Session = Depends(get_db)):
    return StockService.add_stock(db, stock.item_id, stock.project_id, stock.warehouse_id, stock.quantity)


@router.post("/deduct", response_model=list[StockResponse])
def deduct_stock(stock: StockDeduct, db: Session = Depends(get_db)):
    return StockService.deduct_stock(db, stock.item_id, stock.project_id, stock.warehouse_id, stock.quantity)


@router.post("/transfer", response_model=StockResponse)
def transfer_stock(item_id: int, from_project_id: int = None, to_project_id: int = None, from_warehouse_id: int = None,
                   to_warehouse_id: int = None, quantity: float = 0, db: Session = Depends(get_db)):
    return StockService.transfer_stock(
        db, item_id=item_id,
        from_project_id=from_project_id,
        to_project_id=to_project_id,
        from_warehouse_id=from_warehouse_id,
        to_warehouse_id=to_warehouse_id,
        quantity=quantity)


@router.get("/location/{location_id}", response_model=list[StockResponse])
def get_items_by_location(location_id: int, db: Session = Depends(get_db)):
    """
    Retrieve stock items by location.
    """
    return StockService.get_stock_by_location_or_project_or_warehouse(db, location_id=location_id)


@router.get("/warehouse/{warehouse_id}", response_model=list[StockResponse])
def get_items_by_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    """
    Retrieve stock items by warehouse.
    """
    return StockService.get_stock_by_location_or_project_or_warehouse(db, warehouse_id=warehouse_id)


@router.get("/project/{project_id}", response_model=list[StockResponse])
def get_items_by_project(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieve stock items by project.
    """
    return StockService.get_stock_by_location_or_project_or_warehouse(db, project_id=project_id)


@router.get("/item/{item_id}/location/{location_id}", response_model=list[StockResponse])
def get_item_locations_and_quantities(item_id: int, location_id: int, db: Session = Depends(get_db)):
    return StockService.get_stock_of_item_by_location_or_project_or_warehouse(
        db, item_id=item_id, location_id=location_id)


@router.get("/item/{item_id}/warehouse/{warehouse_id}", response_model=list[StockResponse])
def get_item_locations_and_quantities(item_id: int, warehouse_id: int, db: Session = Depends(get_db)):
    return StockService.get_stock_of_item_by_location_or_project_or_warehouse(
        db, item_id=item_id, warehouse_id=warehouse_id)


@router.get("/item/{item_id}/project/{project_id}", response_model=list[StockResponse])
def get_item_locations_and_quantities(item_id: int, project_id: int, db: Session = Depends(get_db)):
    return StockService.get_stock_of_item_by_location_or_project_or_warehouse(
        db, item_id=item_id, project_id=project_id)


@router.get("/item/{item_id}/locations", response_model=list[dict])
def get_item_locations_and_quantities(item_id: int, db: Session = Depends(get_db)):
    """
    Retrieve locations and quantities of an item across projects and warehouses.
    """
    return StockService.get_item_location_and_qty(db, item_id=item_id)


@router.get("/item/{item_id}/total", response_model=dict)
def get_total_stock_by_item(item_id: int, db: Session = Depends(get_db)):
    """
    Retrieve total stock of an item across all locations.
    """
    return StockService.get_total_stock_by_item(db, item_id=item_id)
