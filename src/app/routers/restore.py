# src/app/routers/restore.py

from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models import Department, Item, Project, Warehouse, Location, User
from src.app.schemas.restore import EntityRestoreResponse, RestoreResponse
from src.app.services.general_service import GeneralService

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="restores", access_type="read")
def restores_page(
    request: Request,
    entity_type: Optional[str] = None,
    status: Optional[str] = "all",  # all, active, archived, deleted
    db: Session = Depends(get_db),
    page: int = 1,
    size: int = 10,
):
    """
    Retrieve all entities of a given type and status with pagination.
    """
    entity_model_map = {
        "department": Department,
        "item": Item,
        "project": Project,
        "warehouse": Warehouse,
        "location": Location,
        "user": User,
    }

    # Validate entity type
    if entity_type and entity_type not in entity_model_map:
        raise HTTPException(status_code=400, detail="Invalid entity type")

    # Validate status
    valid_statuses = {"all", "archived", "deleted"}
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status value")

    results = []

    model = entity_model_map.get(entity_type) if entity_type else None

    if model:
        # Query builder
        query = db.query(model) if model else db.query()
        # Apply status filter
        if status == "all":
            query = query.filter(model.is_active == False, model.is_approved == True)
        elif status == "archived":
            query = query.filter(model.is_archived == True)
        elif status == "deleted":
            query = query.filter(model.is_deleted == True)

        records = query.offset((page - 1) * size).limit(size).all()
        results.extend([(entity_type, record) for record in records])  # Store tuple with entity name

    else:
        for entity, model in entity_model_map.items():
            if status == "all":
                query = (
                    db.query(model)
                    .filter(or_(model.is_archived == True, model.is_deleted == True))
                    .offset((page - 1) * size)
                    .limit(size)
                    .all()
                )
            elif status == "archived":
                query = (
                    db.query(model)
                    .filter(model.is_archived == True)
                    .offset((page - 1) * size)
                    .limit(size)
                    .all()
                )
            elif status == "deleted":
                query = (
                    db.query(model)
                    .filter(model.is_deleted == True)
                    .offset((page - 1) * size)
                    .limit(size)
                    .all()
                )

            for record in query:
                results.append((entity, record))  # Store entity name with record

    total_records = len(results)
    offset = (page - 1) * size
    total_pages = (total_records + size - 1) // size  # Calculate total pages
    # entities = query.offset(offset).limit(size).all()

    # Prepare the response for rendering
    entity_data = [
        {
            "entity_type": entity_type if entity_type else entity_name,
            "id": entity.id,
            "name": getattr(entity, "username", getattr(entity, "item_code", getattr(entity, "name", "N/A"))),
            "status": "archived" if entity.is_archived else "deleted",
            "deleted_at": entity.deleted_at,
            "archived_at": entity.archived_at,
        }
        for entity_name, entity in results
    ]

    # Render the template with data
    return templates.TemplateResponse(
        "restore.html",
        {
            "request": request,
            "entities": entity_data,
            "page": page,
            "size": size,
            "total_pages": total_pages,
            "entity_type": entity_type,
            "status": status,
            "user_id": request.state.user_id,
            "user_role": request.state.role,
        },
    )


@router.get("/restore", response_model=list[EntityRestoreResponse])
@rbac_check(entity="restore", access_type="view")
def get_restore_entities(
    request: Request,
    db: Session = Depends(get_db),
    entity_type: Optional[str] = None,
    page: int = 1,
    size: int = 10,
):
    """
    List all archived or soft-deleted entities based on the entity type.
    """
    return GeneralService.get_archived_entities(entity_type, page, size, db)


@router.post("/restore/{entity_type}/{entity_id}", response_model=RestoreResponse)
@rbac_check(entity="restore", access_type="restore")
def restore_entity(
    request: Request,
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
):
    """
    Restore a specific entity by type and ID.
    """
    return GeneralService.restore_entity(entity_type, entity_id, request.state.user_id, db)