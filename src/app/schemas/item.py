# src/app/schemas/item.py

from pydantic import BaseModel
from typing import List, Optional


class ItemCreate(BaseModel):
    item_code: str
    description: str
    photo: str
    total_qty: int
    location_id: int
    warehouse_ids: Optional[List[int]] = None
    project_ids: Optional[List[int]] = None


class ItemResponse(BaseModel):
    id: int
    item_code: str
    description: str
    photo: str
    total_qty: int
    location_id: int

    class Config:
        from_attributes = True  # Enable ORM compatibility
