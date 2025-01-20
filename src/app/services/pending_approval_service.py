# src/app/services/pending_approval_service.py

from sqlalchemy.orm import Session
from datetime import datetime, UTC
from fastapi import HTTPException
from src.app.core.rbac import has_approval_privileges
from src.app.models import User, PendingApproval, ApprovalStatus
from src.app.services.history_log_service import HistoryLogService


class PendingApprovalService:
    @staticmethod
    def submit_approval_request(db: Session, entity: str, action: str, requested_by: int, new_value_dict: dict,
                                entity_id: int = None):
        """
        Submits a request for approval if the user is not an admin. If the user is an admin, directly processes the
        request.

        Args:
            db (Session): Database session.
            entity (str): Entity type (e.g., "item", "project").
            entity_id (int): ID of the entity being acted upon.
            action (str): Action type ("create", "update", "delete").
            new_value_dict (dict): New data to be applied if approved.
            requested_by (int): ID of the user making the request.

        Returns:
            dict: Response message indicating the request status.
        """
        existing_request = None
        if action not in ["create"]:
            existing_request = db.query(PendingApproval).filter(
                PendingApproval.entity == entity,
                PendingApproval.entity_id == entity_id,
                PendingApproval.action == action,
                PendingApproval.approval_status == ApprovalStatus.PENDING
            ).first()

        if existing_request:
            raise HTTPException(status_code=400, detail="A pending approval for this action already exists.")

        user = db.query(User).filter(User.id == requested_by).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        request_entry = PendingApproval(
            entity=entity,
            entity_id=entity_id,
            action=action,
            new_value=new_value_dict,
            requested_by=requested_by,
            requested_at=datetime.now(UTC),
            approval_status=ApprovalStatus.PENDING
        )
        db.add(request_entry)
        db.commit()
        db.refresh(request_entry)

        # Log action
        HistoryLogService.log_action(db, entity, entity_id, action, requested_by)
        return request_entry
        # return {"detail": f"Approval request for {action} submitted successfully", "request_id": request_entry.id}

    @staticmethod
    def approval_request(db: Session, approval_id: int, approver_id: int, action: str):
        """
        Approves a pending request and applies the corresponding action.

        Args:
            db (Session): Database session.
            approval_id (int): ID of the pending approval request.
            approver_id (int): ID of the admin approving the request.
            action (str): Action by admin approve or reject

        Returns:
            dict: Response message indicating the approval status.
        """
        # Step 1: Fetch the pending approval request
        pending = db.query(PendingApproval).filter(PendingApproval.id == approval_id).first()
        if not pending:
            raise HTTPException(status_code=404, detail="Approval request not found")

        if pending.approval_status != ApprovalStatus.PENDING:
            raise HTTPException(status_code=400, detail="Request already processed")

        # Step 2: Check if approver is eligible (admin, superuser, or direct manager)
        approver = db.query(User).filter(User.id == approver_id).first()
        requester = db.query(User).filter(User.id == pending.requested_by).first()

        if not (approver and has_approval_privileges(db, approver_id) or
                approver.id == requester.direct_manager_id):
            raise HTTPException(status_code=403, detail="You are not authorized to make this action")

        if action == "reject":
            # Reject the request
            pending.approval_status = ApprovalStatus.REJECTED
            pending.approved_by = approver_id
            pending.approved_at = datetime.now(UTC)
            db.commit()

            # Log the rejection in history
            HistoryLogService.approval_log_action(
                db=db,
                user_id=approver_id,
                entity=pending.entity,
                entity_id=pending.entity_id,
                details=f"{pending.action} - rejected"
            )

            # Delete the request after history logged
            db.delete(pending)
            db.commit()

            return {"detail": f"Request for {pending.action} rejected successfully"}

        # Step 3: Apply the action (create, update, delete) dynamically based on the entity type

        # late import to avoid circulation
        from src.app.utils.helpers import ENTITY_SERVICE_MAPPING, ENTITY_MODEL_MAPPING

        entity_model = ENTITY_MODEL_MAPPING.get(pending.entity)
        entity_service = ENTITY_SERVICE_MAPPING.get(pending.entity)

        if not entity_model or not entity_service:
            raise HTTPException(status_code=400, detail=f"Unknown entity type: {pending.entity}")

        if pending.action == "create":
            entity_service.direct_create(pending.new_value, db)
        elif pending.action == "update":
            entity_id = pending.entity_id
            entity_service.direct_update(pending.new_value, entity_id, db)
        elif pending.action == "soft_delete":
            entity_id = pending.entity_id
            entity_service.direct_soft_delete(entity_id, db)
        elif pending.action == "archive":
            entity_id = pending.entity_id
            entity_service.direct_archive(entity_id, db)
        elif pending.action == "restore":
            entity_id = pending.entity_id
            entity_service.direct_restore(entity_id, db)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action type: {pending.action}")

        # Step 4: Update pending approval status
        pending.approval_status = ApprovalStatus.APPROVED
        pending.approved_by = approver_id
        pending.approved_at = datetime.now(UTC)
        db.commit()

        # Step 5: Log approval in history
        HistoryLogService.approval_log_action(
            db=db,
            user_id=approver_id,
            entity=pending.entity,
            entity_id=pending.entity_id,
            details=f"{pending.action} - approved"
        )

        # Delete the request after history logged
        db.delete(pending)
        db.commit()

        return {"detail": f"Request for {pending.action} approved successfully"}
