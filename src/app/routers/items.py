from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.services.item_service import ItemService
from src.app.schemas.item import ItemCreate, ItemResponse

router = APIRouter()


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


@router.get("/location/{location_id}", response_model=list[ItemResponse])
def get_item_by_location(location_id: int, db: Session = Depends(get_db)):
    return ItemService.get_items_by_location(db, location_id)


@router.get("/warehouse/{warehouse_id}", response_model=list[ItemResponse])
def get_item_by_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
    return ItemService.get_items_by_warehouse(db, warehouse_id)


@router.get("/project/{project_id}", response_model=list[ItemResponse])
def get_item_by_project(project_id: int, db: Session = Depends(get_db)):
    return ItemService.get_items_by_project(db, project_id)


@router.get("/", response_model=list[ItemResponse])
def list_item(db: Session = Depends(get_db)):
    return ItemService.list_items(db)

