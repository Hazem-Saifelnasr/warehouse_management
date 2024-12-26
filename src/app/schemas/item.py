# src/app/schemas/item.py

from pydantic import BaseModel


class ItemCreate(BaseModel):
    item_code: str
    description: str
    photo: str
    unit_of_measure: str


class ItemResponse(BaseModel):
    id: int
    item_code: str
    description: str
    photo: str
    unit_of_measure: str

    class Config:
        from_attributes = True  # Enable ORM compatibility
