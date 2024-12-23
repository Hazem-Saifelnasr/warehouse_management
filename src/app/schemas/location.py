# src/app/schemas/location.py

from pydantic import BaseModel


class LocationCreate(BaseModel):
    name: str


class LocationResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # Enable ORM compatibility
