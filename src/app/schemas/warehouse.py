# src/app/schemas/warehouse.py

from pydantic import BaseModel


class WarehouseCreate(BaseModel):
    name: str
    location_id: int


class WarehouseResponse(BaseModel):
    id: int
    name: str
    location_id: int

    class Config:
        from_attributes = True  # Enable ORM compatibility


class WarehouseUpdate(BaseModel):
    name: str
    location_id: int
