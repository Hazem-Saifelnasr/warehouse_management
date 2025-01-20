# src/app/routers/locations.py

from typing import Union
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.schemas.pending_approval import PendingApprovalResponse
from src.app.services.location_service import LocationService
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models.location import Location
from src.app.schemas.location import LocationCreate, LocationResponse

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="locations", access_type="read")  
def locations_page(request: Request, db: Session = Depends(get_db), page: int = 1, size: int = 10):
    locations_query = db.query(Location).filter(Location.is_active == True)
    total_locations = locations_query.count()  # Total number of items
    offset = (page - 1) * size
    total_pages = (total_locations + size - 1) // size  # Calculate total pages
    locations = locations_query.offset(offset).limit(size).all()
    return templates.TemplateResponse("locations.html", {
        "request": request,
        "locations": locations,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "user_id": request.state.user_id,
        "user_role": request.state.role
    })


@router.post("/add", response_model=Union[LocationResponse, PendingApprovalResponse])
@rbac_check(entity="locations", access_type="create")  
def create_location(request: Request, location: LocationCreate, db: Session = Depends(get_db)):
    return LocationService.create_location(location, request.state.user_id, db)


@router.get("/list", response_model=list[LocationResponse])
@rbac_check(entity="locations", access_type="read")
def list_locations(request: Request, db: Session = Depends(get_db)):
    return LocationService.list_locations(db)


@router.put("/{location_id}", response_model=Union[LocationResponse, PendingApprovalResponse])
@rbac_check(entity="locations", access_type="write")
def update_location(request: Request, location_id: int, update_data: dict, db: Session = Depends(get_db)):
    return LocationService.update_location(location_id, update_data, request.state.user_id, db)


@router.delete("/{location_id}")
@rbac_check(entity="locations", access_type="delete")
def delete_location_soft(request: Request, location_id: int, db: Session = Depends(get_db)):
    return LocationService.delete_location_soft(location_id, request.state.user_id, db)


@router.delete("/permanent/{location_id}")
@rbac_check(entity="locations", access_type="delete")
def delete_location_permanent(request: Request, location_id: int, db: Session = Depends(get_db)):
    return LocationService.delete_location_permanent(location_id, request.state.user_id, db)


@router.post("/archive/{location_id}")
@rbac_check(entity="locations", access_type="archive")
def archive_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    return LocationService.archive_location(location_id, request.state.user_id, db)


@router.post("/restore/{location_id}")
@rbac_check(entity="locations", access_type="restore")
def restore_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    return LocationService.restore_location(location_id, request.state.user_id, db)


@router.get("/{location_id}", response_model=LocationResponse)
@rbac_check(entity="locations", access_type="read")
def get_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    return LocationService.get_location(location_id, db)


@router.get("/{location_id}/entities", response_model=dict)
@rbac_check(entity="locations", access_type="read")  
def get_warehouses_and_projects(request: Request, location_id: int, db: Session = Depends(get_db)):
    return LocationService.get_warehouses_and_projects(location_id, db)
