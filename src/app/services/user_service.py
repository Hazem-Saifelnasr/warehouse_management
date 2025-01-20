# src/app/services/user_service.py

from datetime import datetime, UTC

from sqlalchemy import Integer
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from src.app.core.database import get_db
from src.app.core.rbac import has_approval_privileges
from src.app.models import PendingApproval, ApprovalStatus
from src.app.models.user import User
from src.app.schemas.user import UserCreate
from src.app.core.security import get_password_hash
from src.app.services.history_log_service import HistoryLogService
from src.app.services.pending_approval_service import PendingApprovalService


class UserService:
    @staticmethod
    def create_user(user_data: UserCreate, requester_id: int, db: Session = Depends(get_db)):
        # Check if the username or email already exists
        existing_user = db.query(User).filter(User.employee_id == user_data.employee_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this Employee Id already taken")

        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this name already taken")

        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="User with this email already registered")

        # Step 2: Check if a pending approval for the same name already exists
        existing_request = db.query(PendingApproval).filter(
            PendingApproval.entity == "user",
            PendingApproval.action == "create",
            PendingApproval.approval_status == ApprovalStatus.PENDING,
            PendingApproval.new_value["employee_id"].astext.cast(Integer) == user_data.employee_id,
        ).first()

        if existing_request:
            raise HTTPException(status_code=400,
                                detail="A pending approval request for this employee id already exists")

        # Step 3: If user has approval privileges, create the item directly
        if has_approval_privileges(db, requester_id):
            hashed_password = get_password_hash(user_data.password)
            user_dict = dict(user_data)
            user_dict.pop("password", None)  # Remove "password" if it exists, safely

            new_user = User(**dict(user_dict))
            new_user.hashed_password = hashed_password
            new_user.role = user_data.role or "user"  # Default role
            new_user.is_approved = True
            new_user.is_active = True
            new_user.created_by = requester_id
            new_user.created_at = datetime.now(UTC)

            db.add(new_user)  # Add the user to the session
            db.commit()
            db.refresh(new_user)  # Refresh to get the updated relationships

            HistoryLogService.log_action(db, "user", new_user.id, "create", requester_id)
            return new_user

        # Step 4: Add to pending approval
        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="user",
            entity_id=None,  # New user, no ID yet
            action="create",
            new_value_dict=user_data.model_dump(),
            requested_by=requester_id
        )

    @staticmethod
    def update_user(user_id: int, update_data: dict, requester_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=404, detail="User not found")

        if has_approval_privileges(db, requester_id):
            for key, value in update_data.items():
                if key == "hashed_password":
                    raise HTTPException(status_code=400, detail="Cannot update hashed_password directly")
                setattr(user, key, value)

            db.commit()
            db.refresh(user)

            HistoryLogService.log_action(db, "user", user_id, "update", requester_id)
            return user

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="user",
            entity_id=user_id,
            action="update",
            new_value_dict=update_data,
            requested_by=requester_id,
        )

    @staticmethod
    def delete_user_soft(user_id: int, requester_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=404, detail="User not found")

        if has_approval_privileges(db, requester_id):
            user.is_deleted = True
            user.is_active = False
            user.deleted_at = datetime.now(UTC)
            user.deleted_by = requester_id

            db.commit()
            db.refresh(user)
            HistoryLogService.log_action(db, "user", user_id, "soft_delete", requester_id)
            return {"detail": "User deleted successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="user",
            action="delete",
            entity_id=user_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def delete_user_permanent(user_id: int, requester_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        meta_data = {"id": user.id, "name": user.username}
        if has_approval_privileges(db, requester_id):
            db.delete(user)
            db.commit()

            # Log permanent deletion
            HistoryLogService.log_action(db, "user", user_id, "delete_permanent", requester_id, meta_data)

            return {"detail": "User deleted successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="user",
            action="delete_permanent",
            entity_id=user_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def archive_user(user_id: int, requester_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_deleted:
            raise HTTPException(status_code=400, detail="User is already deleted")

        if user.is_archived:
            raise HTTPException(status_code=400, detail="User is already archived")

        if has_approval_privileges(db, requester_id):
            user.is_archived = True
            user.is_active = False
            user.archived_at = datetime.now(UTC)
            user.archived_by = requester_id

            db.commit()
            db.refresh(user)  # Refresh to get updated relationships
            # Log archive action
            HistoryLogService.log_action(db, "user", user_id, "archive", requester_id)
            return {"detail": "User archived successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="user",
            action="archive",
            entity_id=user_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def restore_user(user_id: int, requester_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if has_approval_privileges(db, requester_id):
            if user.is_approved:
                user.is_deleted = False
                user.is_archived = False
                user.is_active = True
            db.commit()
            # Log restore action
            HistoryLogService.log_action(db, "user", user_id, "restore", requester_id)
            return {"detail": "User restored successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="user",
            action="restore",
            entity_id=user_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            if user.is_archived:
                raise HTTPException(status_code=404, detail="User is archived")
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def list_users(db: Session = Depends(get_db)):
        users = db.query(User).filter(User.is_active == True).all()
        return users

    # === for pending approvals use ===
    @staticmethod
    def direct_create(new_value: dict, db: Session = Depends(get_db)):
        """
        Directly creates a location without approval checks.
        """
        new_value = UserCreate(**new_value)  # Convert dictionary to ProjectCreate model
        user = db.query(User).filter(User.username == new_value.username).first()
        if user:
            raise HTTPException(status_code=400, detail="User already exist")

        hashed_password = get_password_hash(new_value.password)

        new_user = User(**dict(new_value))
        new_user.hashed_password = hashed_password
        new_user.role = new_value.role or "user"  # Default role
        new_user.is_approved = True
        new_user.is_active = True
        new_user.created_by = new_value.created_by
        new_user.created_at = datetime.now(UTC)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    @staticmethod
    def direct_update(new_value: dict, entity_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == entity_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=404, detail="User not found")
        for key, value in new_value.items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def direct_soft_delete(entity_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == entity_id).first()
        user.is_deleted = True
        user.is_active = False
        db.commit()
        db.refresh(user)

    @staticmethod
    def direct_archive(entity_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == entity_id).first()
        user.is_archived = True
        user.is_active = False

        db.commit()
        db.refresh(user)

    @staticmethod
    def direct_restore(entity_id: int, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == entity_id).first()
        user.is_deleted = False
        user.is_archived = False
        user.is_active = True

        db.commit()
        db.refresh(user)
