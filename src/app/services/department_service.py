# src/app/services/department_service.py

from datetime import datetime, UTC
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.core.rbac import has_approval_privileges
from src.app.models import PendingApproval, ApprovalStatus, Department
from src.app.schemas.department import DepartmentCreate, DepartmentUpdate
from src.app.services.history_log_service import HistoryLogService
from src.app.services.pending_approval_service import PendingApprovalService


class DepartmentService:
    @staticmethod
    def create_department(department: DepartmentCreate, requester_id: int, db: Session = Depends(get_db)):
        # Check for duplicate name
        existing_department = db.query(Department).filter(Department.name == department.name).first()
        if existing_department:
            raise HTTPException(status_code=400, detail="Department with this name already exists")

        # Step 2: Check if a pending approval for the same name already exists
        existing_request = db.query(PendingApproval).filter(
            PendingApproval.entity == "department",
            PendingApproval.action == "create",
            PendingApproval.approval_status == ApprovalStatus.PENDING,
            PendingApproval.new_value["name"].astext == department.name,
        ).first()

        if existing_request:
            raise HTTPException(status_code=400,
                                detail="A pending approval request for this department name already exists")

        # Step 3: If user has approval privileges, create the item directly
        if has_approval_privileges(db, requester_id):
            new_department = Department(**dict(department))
            new_department.is_approved = True
            new_department.is_active = True
            new_department.created_by = requester_id
            new_department.created_at = datetime.now(UTC)

            # new_warehouse = Warehouse(**dict(warehouse))
            db.add(new_department)  # Add the warehouse to the session
            db.commit()
            db.refresh(new_department)  # Refresh to get the updated relationships

            HistoryLogService.log_action(db, "department", new_department.id, "create", requester_id)
            return new_department

        # Step 4: Add to pending approval
        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="department",
            entity_id=None,  # New warehouse, no ID yet
            action="create",
            new_value_dict=department.model_dump(),
            requested_by=requester_id
        )

    @staticmethod
    def update_department(department_id: int, update_data: DepartmentUpdate, requester_id: int, db: Session = Depends(get_db)):
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department or not department.is_active:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        if has_approval_privileges(db, requester_id):
            for key, value in update_data.model_dump(exclude_unset=True).items():
                setattr(department, key, value)

            db.commit()
            db.refresh(department)

            HistoryLogService.log_action(db, "department", department_id, "update", requester_id)
            return department

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="department",
            entity_id=department_id,
            action="update",
            new_value_dict=update_data,
            requested_by=requester_id,
        )

    @staticmethod
    def delete_department_soft(department_id: int, requester_id: int, db: Session = Depends(get_db)):
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department or not department.is_active:
            raise HTTPException(status_code=404, detail="Department not found")

        if has_approval_privileges(db, requester_id):
            department.is_deleted = True
            department.is_active = False
            department.deleted_at = datetime.now(UTC)
            department.deleted_by = requester_id

            db.commit()
            db.refresh(department)
            HistoryLogService.log_action(db, "department", department_id, "soft_delete", requester_id)
            return {"detail": "Department deleted successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="department",
            action="delete",
            entity_id=department_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def delete_department_permanent(department_id: int, requester_id: int, db: Session = Depends(get_db)):
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        meta_data = {"id": department.id, "name": department.name}
        if has_approval_privileges(db, requester_id):
            db.delete(department)
            db.commit()

            # Log permanent deletion
            HistoryLogService.log_action(db, "department", department_id, "delete_permanent", requester_id, meta_data)

            return {"detail": "Department deleted permanently"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="department",
            action="delete_permanent",
            entity_id=department_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def archive_department(department_id: int, requester_id: int, db: Session = Depends(get_db)):
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department or not department.is_active:
            raise HTTPException(status_code=404, detail="Department not found")

        if department.is_deleted:
            raise HTTPException(status_code=400, detail="Department is already deleted")

        if department.is_archived:
            raise HTTPException(status_code=400, detail="Department is already archived")

        if has_approval_privileges(db, requester_id):
            department.is_archived = True
            department.is_active = False
            department.archived_at = datetime.now(UTC)
            department.archived_by = requester_id

            db.commit()
            db.refresh(department)  # Refresh to get updated relationships
            # Log archive action
            HistoryLogService.log_action(db, "department", department_id, "archive", requester_id)
            return {"detail": "Warehouse archived successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="department",
            action="archive",
            entity_id=department_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def restore_department(department_id: int, requester_id: int, db: Session = Depends(get_db)):
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")

        if has_approval_privileges(db, requester_id):
            if department.is_approved:
                department.is_deleted = False
                department.is_archived = False
                department.is_active = True
            db.commit()
            # Log restore action
            HistoryLogService.log_action(db, "department", department_id, "restore", requester_id)
            return {"detail": "Department restored successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="department",
            action="restore",
            entity_id=department_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def get_department(department_id: int, db: Session = Depends(get_db)):
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department or not department.is_active:
            if department.is_archived:
                raise HTTPException(status_code=404, detail="Department is archived")
            raise HTTPException(status_code=404, detail="Department not found")
        return department

    @staticmethod
    def list_departments(db: Session = Depends(get_db)):
        departments = db.query(Department).filter(Department.is_active == True).all()
        return departments

    # === for pending approvals use ===
    @staticmethod
    def direct_create(new_value: dict, db: Session = Depends(get_db)):
        """
        Directly creates a location without approval checks.
        """
        new_value = DepartmentCreate(**new_value)  # Convert dictionary to ProjectCreate model
        department = db.query(Department).filter(Department.name == new_value.name).first()
        if department:
            raise HTTPException(status_code=400, detail="Department already exist")

        new_department = Department(**dict(new_value))
        new_department.is_approved = True
        new_department.is_active = True
        new_department.created_by = new_value.created_by
        new_department.created_at = datetime.now(UTC)

        db.add(new_department)
        db.commit()
        db.refresh(new_department)

    @staticmethod
    def direct_update(new_value: dict, entity_id: int, db: Session = Depends(get_db)):
        department = db.query(Department).filter(Department.id == entity_id).first()
        if not department or not department.is_active:
            raise HTTPException(status_code=404, detail="Department not found")
        for key, value in new_value.items():
            setattr(department, key, value)
        db.commit()
        db.refresh(department)
        return department

    @staticmethod
    def direct_soft_delete(entity_id: int, db: Session = Depends(get_db)):
        department = db.query(Department).filter(Department.id == entity_id).first()
        department.is_deleted = True
        department.is_active = False
        db.commit()
        db.refresh(department)

    @staticmethod
    def direct_archive(entity_id: int, db: Session = Depends(get_db)):
        department = db.query(Department).filter(Department.id == entity_id).first()
        department.is_archived = True
        department.is_active = False

        db.commit()
        db.refresh(department)

    @staticmethod
    def direct_restore(entity_id: int, db: Session = Depends(get_db)):
        department = db.query(Department).filter(Department.id == entity_id).first()
        department.is_deleted = False
        department.is_archived = False
        department.is_active = True

        db.commit()
        db.refresh(department)
