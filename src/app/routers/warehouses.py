# src/app/routers/warehouses.py

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models.warehouse import Warehouse
from src.app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.models.location import Location


router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="warehouse", access_type="read")  # Highlight: Added decorator
def warehouses_page(request: Request, db: Session = Depends(get_db)):
    warehouses = db.query(Warehouse).options(joinedload(Warehouse.location)).all()
    locations = db.query(Location).all()
    return templates.TemplateResponse("warehouses.html", {
        "request": request,
        "warehouses": warehouses,
        "locations": locations,
    })


@router.post("/add", response_model=WarehouseResponse)
@rbac_check(entity="warehouse", access_type="create")  # Highlight: Added decorator
def create_warehouse(request: Request, warehouse: WarehouseCreate, db: Session = Depends(get_db)):
    # Check for duplicate name in the same location
    if db.query(Warehouse).filter(
            Warehouse.name == warehouse.name, Warehouse.location_id == warehouse.location_id).first():
        raise HTTPException(status_code=400, detail="Warehouse with this name already exists in the specified location")

    new_warehouse = Warehouse(**dict(warehouse))
    db.add(new_warehouse)
    db.commit()
    db.refresh(new_warehouse)
    return new_warehouse


@router.get("/list", response_model=list[WarehouseResponse])
@rbac_check(entity="warehouse", access_type="read")  # Highlight: Added decorator
def list_warehouses(request: Request, db: Session = Depends(get_db)):
    warehouses = db.query(Warehouse).all()
    return warehouses


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
@rbac_check(entity="warehouse", access_type="read")  # Highlight: Added decorator
def get_warehouse(request: Request, warehouse_id: int, db: Session = Depends(get_db)):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
@rbac_check(entity="warehouse", access_type="write")  # Highlight: Added decorator
def update_warehouse(request: Request, warehouse_id: int, update_data: WarehouseUpdate, db: Session = Depends(get_db)):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(warehouse, key, value)

    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.delete("/{warehouse_id}")
@rbac_check(entity="warehouse", access_type="delete")  # Highlight: Added decorator
def delete_warehouse(request: Request, warehouse_id: int, db: Session = Depends(get_db)):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    db.delete(warehouse)
    db.commit()
    return {"detail": "Warehouse deleted successfully"}


@router.get("/location/{location_id}", response_model=list[WarehouseResponse])
@rbac_check(entity="warehouse", access_type="read")  # Highlight: Added decorator
def get_warehouses_by_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    """
    Fetch all warehouses in a given location.
    """
    return db.query(Warehouse).filter(Warehouse.location_id == location_id).all()
