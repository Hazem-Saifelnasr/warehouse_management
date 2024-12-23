# src/app/routers/reports.py

import re
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from src.app.core.database import get_db
from src.app.models.item import Item
from src.app.models.project import Project
from src.app.models.warehouse import Warehouse
from src.app.models.location import Location

router = APIRouter()


@router.get("/items/export")
def export_inventory_report(db: Session = Depends(get_db)):
    items = db.query(Item).options(
        joinedload(Item.location),
        joinedload(Item.warehouses),
        joinedload(Item.projects)
    ).all()

    data = [
        {
            "Item Code": item.item_code,
            "Description": item.description,
            "Photo": item.photo,
            "Quantity": item.total_qty,
            "Location": item.location.name if item.location else None,  # Safe access
            "Warehouses": [warehouse.name for warehouse in item.warehouses],  # Get warehouse names
            "Projects": [project.project_name for project in item.projects],  # Get project names
        }
        for item in items
    ]

    df = pd.DataFrame(data)
    file_path = "src/assets/reports/inventory_report.xlsx"
    df.to_excel(file_path, index=False)
    return {"detail": f"Report generated at {file_path}", "items": data}


@router.get("/warehouse/{warehouse_id}")
def export_inventory_report_by_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    # Fetch the warehouse
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    # Fetch items for the warehouse with eager loading
    items = db.query(Item).options(
        joinedload(Item.location)
    ).join(Item.warehouses).filter(Warehouse.id == warehouse_id).all()

    data = [
        {
            "Item Code": item.item_code,
            "Description": item.description,
            "Photo": item.photo,
            "Quantity": item.total_qty,
            "Location": item.location.name if item.location else None,  # Safe access to location name
        }
        for item in items
    ]

    # Sanitize warehouse name for the file path
    sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', warehouse.name)

    df = pd.DataFrame(data)
    file_path = f"src/assets/reports/inventory_report_warehouse_{sanitized_name}.xlsx"
    df.to_excel(file_path, index=False)
    return {"detail": f"Report generated at {file_path}", "items": data}


@router.get("/project/{project_id}")
def export_inventory_by_project(project_id: int, db: Session = Depends(get_db)):
    # Fetch the project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    # Fetch items for the warehouse with eager loading
    items = db.query(Item).options(
        joinedload(Item.location)
    ).join(Item.projects).filter(Project.id == project_id).all()

    data = [
        {
            "Item Code": item.item_code,
            "Description": item.description,
            "Photo": item.photo,
            "Quantity": item.total_qty,
            "Location": item.location.name if item.location else None,  # Safe access to location name
        }
        for item in items
    ]

    # Sanitize project name for the file path
    sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', project.project_name)

    df = pd.DataFrame(data)
    file_path = f"src/assets/reports/inventory_report_project_{sanitized_name}.xlsx"
    df.to_excel(file_path, index=False)
    return {"detail": f"Report generated at {file_path}", "items": data}


@router.get("/location/{location_id}")
def export_inventory_by_location(location_id: int, db: Session = Depends(get_db)):
    # Fetch the location
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    items = db.query(Item).filter(Item.location_id == location_id).all()

    data = [
        {
            "Item Code": item.item_code,
            "Description": item.description,
            "Photo": item.photo,
            "Quantity": item.total_qty,
            "Location": location.name,
        }
        for item in items
    ]

    # Sanitize location name for the file path
    sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', location.name)

    df = pd.DataFrame(data)
    file_path = f"src/assets/reports/inventory_report_location_{sanitized_name}.xlsx"
    df.to_excel(file_path, index=False)
    return {"detail": f"Report generated at {file_path}", "items": data}
