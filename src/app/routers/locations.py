# src/app/routers/locations.py

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models.location import Location
from src.app.schemas.location import LocationCreate, LocationResponse
from src.app.schemas.project import ProjectResponse
from src.app.schemas.warehouse import WarehouseResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="locations", access_type="read")  # Highlight: Added decorator
def locations_page(request: Request, db: Session = Depends(get_db)):
    locations = db.query(Location).all()
    return templates.TemplateResponse("locations.html", {
        "request": request,
        "locations": locations
    })


@router.post("/add", response_model=LocationResponse)
@rbac_check(entity="locations", access_type="create")  # Highlight: Added decorator
def create_location(request: Request, location: LocationCreate, db: Session = Depends(get_db)):
    if db.query(Location).filter(Location.name == location.name).first():
        raise HTTPException(status_code=400, detail="Location with this name already exists")

    new_location = Location(**dict(location))
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location


@router.get("/list", response_model=list[LocationResponse])
@rbac_check(entity="locations", access_type="read")  # Highlight: Added decorator
def list_locations(request: Request, db: Session = Depends(get_db)):
    return db.query(Location).all()


@router.get("/{location_id}", response_model=LocationResponse)
@rbac_check(entity="locations", access_type="read")  # Highlight: Added decorator
def get_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.put("/{location_id}", response_model=LocationResponse)
@rbac_check(entity="locations", access_type="write")  # Highlight: Added decorator
def update_location(request: Request, location_id: int, update_data: dict, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    for key, value in update_data.items():
        setattr(location, key, value)

    db.commit()
    db.refresh(location)
    return location


@router.delete("/{location_id}")
@rbac_check(entity="locations", access_type="delete")  # Highlight: Added decorator
def delete_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.delete(location)
    db.commit()
    return {"detail": "Location deleted successfully"}


@router.get("/{location_id}/entities", response_model=dict)
@rbac_check(entity="locations", access_type="read")  # Highlight: Added decorator
def get_warehouses_and_projects(request: Request, location_id: int, db: Session = Depends(get_db)):
    """
    Get all warehouses and projects in a specific location.
    """
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    warehouses = location.warehouses
    projects = location.projects

    return {
        "warehouses": [WarehouseResponse.model_validate(warehouse) for warehouse in warehouses],
        "projects": [ProjectResponse.model_validate(project) for project in projects]
    }

# # GET /locations/?skip=0&limit=5
# @router.get("/", response_model=list[LocationResponse])
# def list_locations(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(10, ge=1),
#     db: Session = Depends(get_db)
# ):
#     """
#     List all locations with pagination.
#     """
#     return db.query(Location).offset(skip).limit(limit).all()
