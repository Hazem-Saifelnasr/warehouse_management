# src/app/services/general_service.py

from datetime import datetime, UTC
from typing import Optional
from fastapi import HTTPException, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.services.history_log_service import HistoryLogService
from src.app.models import Department, Item, Project, Warehouse, Location, User


class GeneralService:
    @staticmethod
    def get_archived_entities(entity_type: Optional[str], page: int, size: int, db: Session = Depends(get_db)):
        """
        Retrieve all archived or soft-deleted entities for the specified type.
        """
        entity_model_map = {
            "department": Department,
            "item": Item,
            "project": Project,
            "warehouse": Warehouse,
            "location": Location,
            "user": User,
        }

        if entity_type and entity_type not in entity_model_map:
            raise HTTPException(status_code=400, detail="Invalid entity type")

        results = []

        if entity_type:
            model = entity_model_map[entity_type]
            query = (
                db.query(model)
                .filter(or_(model.is_archived == True, model.is_deleted == True))
                .offset((page - 1) * size)
                .limit(size)
                .all()
            )
            results.extend(query)
        else:
            for model in entity_model_map.values():
                query = (
                    db.query(model)
                    .filter(or_(model.is_archived == True, model.is_deleted == True))
                    .offset((page - 1) * size)
                    .limit(size)
                    .all()
                )
                results.extend(query)

        # Format the results for response
        data = [
            {
                "entity_type": entity_type or model.__tablename__,
                "entity_id": row.id,
                "name": getattr(row, "username", getattr(row, "item_code", getattr(row, "name", "N/A"))),
                "is_archived": row.is_archived,
                "is_deleted": row.is_deleted,
            }
            for row in results
        ]

        return {"data": data, "page": page, "size": size}

    @staticmethod
    def restore_entity(entity_type: str, entity_id: int, requester_id: int, db: Session = Depends(get_db)):
        """
        Restore a specific entity based on its type and ID.
        """
        entity_model_map = {
            "department": Department,
            "item": Item,
            "project": Project,
            "warehouse": Warehouse,
            "location": Location,
            "user": User,
        }

        if entity_type not in entity_model_map:
            raise HTTPException(status_code=400, detail="Invalid entity type")

        model = entity_model_map[entity_type]
        entity = db.query(model).filter(model.id == entity_id).first()

        if not entity:
            raise HTTPException(status_code=404, detail=f"{entity_type.capitalize()} not found")

        if entity.is_archived or entity.is_deleted:
            entity.is_archived = False
            entity.is_deleted = False
            entity.is_active = True
            entity.updated_at = datetime.now(UTC)
            entity.updated_by = requester_id
            db.commit()
            HistoryLogService.log_action(db, entity_type, entity_id, "restore", requester_id)
            return {"detail": f"{entity_type.capitalize()} restored successfully"}

        raise HTTPException(status_code=400, detail=f"{entity_type.capitalize()} is not archived or deleted")
