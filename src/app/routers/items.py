# src/app/routers/items.py

from fastapi import APIRouter, Request, Depends, UploadFile, File
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.services.item_service import ItemService
from src.app.schemas.item import ItemCreate, ItemResponse

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.models.item import Item

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="items", access_type="read")  # Highlight: Added decorator
def items_page(request: Request, db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return templates.TemplateResponse("items.html", {
        "request": request,
        "items": items
    })


@router.get("/list", response_model=list[ItemResponse])
@rbac_check(entity="items", access_type="read")  # Highlight: Added decorator
def list_item(request: Request, db: Session = Depends(get_db)):
    return ItemService.list_items(db)


# @router.post("/", response_model=ItemResponse, dependencies=[Depends(rbac_check)])
@router.post("/add", response_model=ItemResponse)
@rbac_check(entity="items", access_type="create")  # Highlight: Added decorator
def create_item(request: Request, item: ItemCreate, db: Session = Depends(get_db)):
    return ItemService.create_item(db, item)


@router.get("/{item_id}", response_model=ItemResponse)
@rbac_check(entity="items", access_type="read")  # Highlight: Added decorator
def get_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    return ItemService.get_item(db, item_id)


@router.put("/{item_id}", response_model=ItemResponse)
@rbac_check(entity="items", access_type="write")  # Highlight: Added decorator
def update_item(request: Request, item_id: int, update_data: dict, db: Session = Depends(get_db)):
    return ItemService.update_item(db, item_id, update_data)


@router.delete("/{item_id}")
@rbac_check(entity="items", access_type="delete")  # Highlight: Added decorator
def delete_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    return ItemService.delete_item(db, item_id)


@router.post("/{item_id}/upload-photo")
@rbac_check(entity="items", access_type="write")  # Highlight: Added decorator
def upload_item_photo(request: Request, item_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return ItemService.upload_item_photo(db, item_id, file)
