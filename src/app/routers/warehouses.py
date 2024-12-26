# src/app/routers/warehouses.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.models.warehouse import Warehouse
from src.app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse

router = APIRouter()


@router.post("/", response_model=WarehouseResponse)
def create_warehouse(warehouse: WarehouseCreate, db: Session = Depends(get_db)):
    # Check for duplicate name in the same location
    if db.query(Warehouse).filter(
            Warehouse.name == warehouse.name, Warehouse.location_id == warehouse.location_id).first():
        raise HTTPException(status_code=400, detail="Warehouse with this name already exists in the specified location")

    new_warehouse = Warehouse(**dict(warehouse))
    db.add(new_warehouse)
    db.commit()
    db.refresh(new_warehouse)
    return new_warehouse


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(warehouse_id: int, update_data: WarehouseUpdate, db: Session = Depends(get_db)):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(warehouse, key, value)

    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.delete("/{warehouse_id}")
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    db.delete(warehouse)
    db.commit()
    return {"detail": "Warehouse deleted successfully"}


@router.get("/", response_model=list[WarehouseResponse])
def list_warehouses(db: Session = Depends(get_db)):
    warehouses = db.query(Warehouse).all()
    return warehouses


@router.get("/location/{location_id}", response_model=list[WarehouseResponse])
def get_warehouses_by_location(location_id: int, db: Session = Depends(get_db)):
    """
    Fetch all warehouses in a given location.
    """
    return db.query(Warehouse).filter(Warehouse.location_id == location_id).all()
