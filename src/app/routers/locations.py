# src/app/routers/locations.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.models.location import Location
from src.app.schemas.location import LocationCreate, LocationResponse

router = APIRouter()


@router.post("/", response_model=LocationResponse)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    new_location = Location(**dict(location))
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(location_id: int, update_data: dict, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    for key, value in update_data.items():
        setattr(location, key, value)

    db.commit()
    db.refresh(location)
    return location


@router.delete("/{location_id}")
def delete_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.delete(location)
    db.commit()
    return {"detail": "Location deleted successfully"}


@router.get("/", response_model=list[LocationResponse])
def list_warehouses(db: Session = Depends(get_db)):
    locations = db.query(Location).all()
    return locations
