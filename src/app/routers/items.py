# src/app/routers/items.py

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.services.item_service import ItemService
from src.app.schemas.item import ItemCreate, ItemResponse

router = APIRouter()


# @router.post("/", response_model=ItemResponse, dependencies=[Depends(rbac_check)])
@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return ItemService.create_item(db, item)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    return ItemService.get_item(db, item_id)


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, update_data: dict, db: Session = Depends(get_db)):
    return ItemService.update_item(db, item_id, update_data)


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    return ItemService.delete_item(db, item_id)


@router.get("/", response_model=list[ItemResponse])
def list_item(db: Session = Depends(get_db)):
    return ItemService.list_items(db)


@router.post("/{item_id}/upload-photo")
def upload_item_photo(item_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return ItemService.upload_item_photo(db, item_id, file)
