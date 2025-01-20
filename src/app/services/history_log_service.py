# src/app/services/history_log_service.py


from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, UTC
from src.app.core.rbac import has_approval_privileges
from src.app.models.history_log import HistoryLog


class HistoryLogService:
    @staticmethod
    def log_action(db: Session, entity: str, entity_id: int, action: str, requester_id: int, metadata: dict = None):
        """
        Create a history log entry.

        Args:
            db (Session): Database session.
            entity (str): The entity type (e.g., "item", "project").
            entity_id (int): The ID of the entity affected by the action.
            action (str): The action performed (e.g., "create", "update", "delete").
            requester_id (int): ID of the user who performed the action or approve it.

        Returns:
            HistoryLog: The created history log entry.
        """
        log_entry = HistoryLog(entity=entity, entity_id=entity_id, action=action, requested_by=requester_id,
                               request_at=datetime.now(UTC), entity_metadata=metadata)
        db.add(log_entry)
        db.commit()

        if has_approval_privileges(db, requester_id):
            HistoryLogService.approval_log_action(db, entity, entity_id, requester_id, "Done with privileges",
                                                  log_entry.id)

        return log_entry

    @staticmethod
    def approval_log_action(db: Session, entity: str, entity_id: int, user_id: int, details: str = None,
                            id: int = None):
        """
        Update a history log entry.

        Args:
            db (Session): Database session.
            id (int): The ID of the log.
            entity (str): The entity type (e.g., "item", "project").
            entity_id (int): The ID of the entity affected by the action.
            user_id (int): ID of the user who performed the action or approve it.
            details (str, optional): A summary of the changes made.

        Returns:
            HistoryLog: The update history log entry.
        """
        if not id:
            exist_log_entry = db.query(HistoryLog).filter(
                HistoryLog.entity == entity,
                HistoryLog.entity_id == entity_id
            ).first()
        else:
            exist_log_entry = db.query(HistoryLog).filter(HistoryLog.id == id).first()

        if not exist_log_entry:
            raise HTTPException(status_code=400, detail="Log doesn't exists")

        if has_approval_privileges(db, user_id):
            exist_log_entry.details = details
            exist_log_entry.approved_by = user_id
            exist_log_entry.approval_at = datetime.now(UTC)

            db.commit()
            db.refresh(exist_log_entry)
            return exist_log_entry

    @staticmethod
    def get_logs_by_entity(db: Session, entity: str, entity_id: int):
        """
        Retrieve history logs for a specific entity and entity ID.

        Args:
            db (Session): Database session.
            entity (str): The entity type (e.g., "item", "project").
            entity_id (int): The ID of the entity.

        Returns:
            List[HistoryLog]: A list of history log entries.
        """
        return (
            db.query(HistoryLog)
            .filter(HistoryLog.entity == entity, HistoryLog.entity_id == entity_id)
            .order_by(HistoryLog.action_date.desc())
            .all()
        )

    @staticmethod
    def get_logs_by_requester(db: Session, user_id: int):
        """
        Retrieve history logs created by a specific user.

        Args:
            db (Session): Database session.
            user_id (int): The ID of the user.

        Returns:
            List[HistoryLog]: A list of history log entries created by the user.
        """
        return (
            db.query(HistoryLog)
            .filter(HistoryLog.requested_by == user_id)
            .order_by(HistoryLog.action_date.desc())
            .all()
        )

    @staticmethod
    def get_logs_by_approver(db: Session, user_id: int):
        """
        Retrieve history logs created by a specific user.

        Args:
            db (Session): Database session.
            user_id (int): The ID of the user.

        Returns:
            List[HistoryLog]: A list of history log entries created by the user.
        """
        return (
            db.query(HistoryLog)
            .filter(HistoryLog.approved_by == user_id)
            .order_by(HistoryLog.action_date.desc())
            .all()
        )

    @staticmethod
    def get_all_logs(db: Session, limit: int = 100):
        """
        Retrieve all history logs, with an optional limit on the number of entries.

        Args:
            db (Session): Database session.
            limit (int, optional): The maximum number of logs to retrieve. Defaults to 100.

        Returns:
            List[HistoryLog]: A list of all history log entries.
        """
        return (
            db.query(HistoryLog)
            .order_by(HistoryLog.action_date.desc())
            .limit(limit)
            .all()
        )


#
# @router.delete("/{item_id}/soft-delete", response_model=ItemResponse)
# def soft_delete_item(item_id: int, db: Session = Depends(get_db), request: Request = None):
#     item = db.query(Item).filter(Item.id == item_id).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#
#     item.is_deleted = True
#     db.commit()
#
#     # Log the action
#     log_action(db, entity="item", entity_id=item_id, action="soft delete", performed_by=request.state.user)
#
#     return {"detail": "Item soft deleted successfully"}
#
# @router.post("/{item_id}/archive", response_model=ItemResponse)
# def archive_item(item_id: int, db: Session = Depends(get_db), request: Request = None):
#     item = db.query(Item).filter(Item.id == item_id).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#
#     item.is_archived = True
#     db.commit()
#
#     # Log the action
#     log_action(db, entity="item", entity_id=item_id, action="archive", performed_by=request.state.user)
#
#     return {"detail": "Item archived successfully"}
#
# @router.post("/{item_id}/restore", response_model=ItemResponse)
# def restore_item(item_id: int, db: Session = Depends(get_db), request: Request = None):
#     item = db.query(Item).filter(Item.id == item_id).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#
#     item.is_deleted = False
#     item.is_archived = False
#     db.commit()
#
#     # Log the action
#     log_action(db, entity="item", entity_id=item_id, action="restore", performed_by=request.state.user)
#
#     return {"detail": "Item restored successfully"}
#
# @router.post("/{item_id}/approve", response_model=ItemResponse)
# def approve_item(item_id: int, db: Session = Depends(get_db), request: Request = None):
#     item = db.query(Item).filter(Item.id == item_id).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#
#     item.is_approved = True
#     db.commit()
#
#     # Log the action
#     log_action(db, entity="item", entity_id=item_id, action="approve", performed_by=request.state.user)
#
#     return {"detail": "Item approved successfully"}
#
# @router.get("/history/{entity}/{entity_id}", response_model=List[HistoryLogResponse])
# def get_history_logs(entity: str, entity_id: int, db: Session = Depends(get_db)):
#     logs = db.query(HistoryLog).filter(HistoryLog.entity == entity, HistoryLog.entity_id == entity_id).all()
#     return logs
