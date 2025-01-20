# src/app/routers/warehouses.py

from typing import Union
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session, joinedload
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models.warehouse import Warehouse
from src.app.schemas.pending_approval import PendingApprovalResponse
from src.app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.models.location import Location
from src.app.services.warehouse_service import WarehouseService


router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="warehouses", access_type="read")
def warehouses_page(request: Request, db: Session = Depends(get_db), page: int = 1, size: int = 10):
    warehouses_query = db.query(Warehouse).options(joinedload(Warehouse.location)).filter(Warehouse.is_active == True)
    total_warehouse = warehouses_query.count()  # Total number of items
    offset = (page - 1) * size
    total_pages = (total_warehouse + size - 1) // size  # Calculate total pages
    warehouses = warehouses_query.offset(offset).limit(size).all()
    locations = db.query(Location).filter(Location.is_active == True).all()
    return templates.TemplateResponse("warehouses.html", {
        "request": request,
        "warehouses": warehouses,
        "locations": locations,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "user_id": request.state.user_id,
        "user_role": request.state.role
    })


@router.post("/add", response_model=Union[WarehouseResponse, PendingApprovalResponse])
@rbac_check(entity="warehouses", access_type="create")
def create_warehouse(request: Request, warehouse: WarehouseCreate, db: Session = Depends(get_db)):
    return WarehouseService.create_warehouse(warehouse, request.state.user_id, db)


@router.get("/list", response_model=list[WarehouseResponse])
@rbac_check(entity="warehouses", access_type="read")
def list_warehouses(request: Request, db: Session = Depends(get_db)):
    return WarehouseService.list_warehouses(db)


@router.put("/{warehouse_id}", response_model=Union[WarehouseResponse, PendingApprovalResponse])
@rbac_check(entity="warehouses", access_type="write")
def update_warehouse(request: Request, warehouse_id: int, update_data: WarehouseUpdate, db: Session = Depends(get_db)):
    return WarehouseService.update_warehouse(warehouse_id, update_data, request.state.user_id, db)


@router.delete("/{warehouse_id}")
@rbac_check(entity="warehouses", access_type="delete")
def delete_warehouse_soft(request: Request, warehouse_id: int, db: Session = Depends(get_db)):
    return WarehouseService.delete_warehouse_soft(warehouse_id, request.state.user_id, db)


@router.delete("/permanent/{warehouse_id}")
@rbac_check(entity="warehouses", access_type="delete")
def delete_warehouse_permanent(request: Request, warehouse_id: int, db: Session = Depends(get_db)):
    return WarehouseService.delete_warehouse_permanent(warehouse_id, request.state.user_id, db)


@router.post("/archive/{warehouse_id}")
@rbac_check(entity="warehouse", access_type="archive")
def archive_warehouse(request: Request, warehouse_id: int, db: Session = Depends(get_db)):
    return WarehouseService.archive_warehouse(warehouse_id, request.state.user_id, db)


@router.post("/restore/{warehouse_id}")
@rbac_check(entity="warehouses", access_type="restore")
def restore_warehouse(request: Request, warehouse_id: int, db: Session = Depends(get_db)):
    return WarehouseService.restore_warehouse(warehouse_id, request.state.user_id, db)


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
@rbac_check(entity="warehouses", access_type="read")
def get_warehouse(request: Request, warehouse_id: int, db: Session = Depends(get_db)):
    return WarehouseService.get_warehouse(warehouse_id, db)


@router.get("/location/{location_id}", response_model=list[WarehouseResponse])
@rbac_check(entity="warehouses", access_type="read")
def get_warehouses_by_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    return WarehouseService.get_warehouses_by_location(location_id, db)
