# src/app/schemas/item.py

from pydantic import BaseModel
from typing import Optional


class ItemCreate(BaseModel):
    item_code: str
    description: str
    photo: Optional[str] = None  # Default to None if not provided
    unit_of_measure: str


class ItemResponse(BaseModel):
    id: int
    item_code: str
    description: str
    photo: Optional[str] = None  # Default to None if not provided
    unit_of_measure: str

    class Config:
        from_attributes = True  # Enable ORM compatibility
