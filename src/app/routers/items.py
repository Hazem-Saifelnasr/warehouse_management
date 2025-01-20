# src/app/routers/items.py

from typing import Union
from fastapi import APIRouter, Request, Depends, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.models.item import Item
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.schemas.pending_approval import PendingApprovalResponse
from src.app.services.item_service import ItemService
from src.app.schemas.item import ItemCreate, ItemResponse

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="items", access_type="read")  
def items_page(request: Request, db: Session = Depends(get_db), page: int = 1, size: int = 10):
    items_query = db.query(Item).filter(Item.is_active == True)
    total_items = items_query.count()  # Total number of items
    offset = (page - 1) * size
    total_pages = (total_items + size - 1) // size  # Calculate total pages
    items = items_query.offset(offset).limit(size).all()
    return templates.TemplateResponse("items.html", {
        "request": request,
        "items": items,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "user_id": request.state.user_id,
        "user_role": request.state.role
    })


# @router.post("/", response_model=ItemResponse, dependencies=[Depends(rbac_check)])
@router.post("/add", response_model=Union[ItemResponse, PendingApprovalResponse])
@rbac_check(entity="items", access_type="create")  
def create_item(request: Request, item: ItemCreate, db: Session = Depends(get_db)):
    return ItemService.create_item(item, request.state.user_id, db)


@router.get("/list", response_model=list[ItemResponse])
@rbac_check(entity="items", access_type="read")
def list_items(request: Request, db: Session = Depends(get_db)):
    return ItemService.list_items(db)


@router.put("/{item_id}", response_model=Union[ItemResponse, PendingApprovalResponse])
@rbac_check(entity="items", access_type="write")  
def update_item(request: Request, item_id: int, update_data: dict, db: Session = Depends(get_db)):
    return ItemService.update_item(item_id, update_data, request.state.user_id, db)


@router.delete("/{item_id}")
@rbac_check(entity="items", access_type="delete")  
def delete_item_soft(request: Request, item_id: int, db: Session = Depends(get_db)):
    return ItemService.delete_item_soft(item_id, request.state.user_id, db)


@router.delete("/permanent/{item_id}")
@rbac_check(entity="items", access_type="delete")
def delete_item_permanent(request: Request, item_id: int, db: Session = Depends(get_db)):
    return ItemService.delete_item_permanent(item_id, request.state.user_id, db)


@router.post("/archive/{item_id}")
@rbac_check(entity="items", access_type="archive")  
def archive_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    return ItemService.archive_item(item_id, request.state.user_id, db)


@router.post("/restore/{item_id}")
@rbac_check(entity="items", access_type="restore")  
def restore_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    return ItemService.restore_item(item_id, request.state.user_id, db)


@router.get("/{item_id}", response_model=ItemResponse)
@rbac_check(entity="items", access_type="read")  
def get_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    return ItemService.get_item(item_id, db)


@router.post("/{item_id}/upload-photo")
@rbac_check(entity="items", access_type="write")  
def upload_item_photo(request: Request, item_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    return ItemService.upload_item_photo(item_id, file, db)
