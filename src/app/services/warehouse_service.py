# src/app/services/warehouse_service.py

from datetime import datetime, UTC
from fastapi import HTTPException, Depends
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.core.rbac import has_approval_privileges
from src.app.models import PendingApproval, ApprovalStatus
from src.app.models.warehouse import Warehouse
from src.app.schemas.warehouse import WarehouseCreate, WarehouseUpdate
from src.app.services.history_log_service import HistoryLogService
from src.app.services.pending_approval_service import PendingApprovalService


class WarehouseService:

    @staticmethod
    def create_warehouse(warehouse: WarehouseCreate, requester_id: int, db: Session = Depends(get_db)):
        # Check for duplicate name in the same location
        existing_warehouse = db.query(Warehouse).filter(Warehouse.name == warehouse.name,
                                                        Warehouse.location_id == warehouse.location_id).first()
        if existing_warehouse:
            raise HTTPException(status_code=400,
                                detail="Warehouse with this name already exists in the specified location")

        # Step 2: Check if a pending approval for the same name already exists
        existing_request = db.query(PendingApproval).filter(
            PendingApproval.entity == "location",
            PendingApproval.action == "create",
            PendingApproval.approval_status == ApprovalStatus.PENDING,
            PendingApproval.new_value["name"].astext == warehouse.name,
        ).first()

        if existing_request:
            raise HTTPException(status_code=400,
                                detail="A pending approval request for this warehouse name already exists")

        # Step 3: If user has approval privileges, create the item directly
        if has_approval_privileges(db, requester_id):
            new_warehouse = Warehouse(**dict(warehouse))
            new_warehouse.is_approved = True
            new_warehouse.is_active = True
            new_warehouse.created_by = requester_id
            new_warehouse.created_at = datetime.now(UTC)

            # new_warehouse = Warehouse(**dict(warehouse))
            db.add(new_warehouse)  # Add the warehouse to the session
            db.commit()
            db.refresh(new_warehouse)  # Refresh to get the updated relationships

            HistoryLogService.log_action(db, "warehouse", new_warehouse.id, "create", requester_id)
            return new_warehouse

        # Step 4: Add to pending approval
        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="warehouse",
            entity_id=None,  # New warehouse, no ID yet
            action="create",
            new_value_dict=warehouse.model_dump(),
            requested_by=requester_id
        )

    @staticmethod
    def update_warehouse(warehouse_id: int, update_data: WarehouseUpdate, requester_id: int, db: Session = Depends(get_db)):
        warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not warehouse or not warehouse.is_active:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        if has_approval_privileges(db, requester_id):
            for key, value in update_data.model_dump(exclude_unset=True).items():
                setattr(warehouse, key, value)

            db.commit()
            db.refresh(warehouse)

            HistoryLogService.log_action(db, "warehouse", warehouse_id, "update", requester_id)
            return warehouse

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="warehouse",
            entity_id=warehouse_id,
            action="update",
            new_value_dict=update_data,
            requested_by=requester_id,
        )

    @staticmethod
    def delete_warehouse_soft(warehouse_id: int, requester_id: int, db: Session = Depends(get_db)):
        warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not warehouse or not warehouse.is_active:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        if has_approval_privileges(db, requester_id):
            warehouse.is_deleted = True
            warehouse.is_active = False
            warehouse.deleted_at = datetime.now(UTC)
            warehouse.deleted_by = requester_id

            db.commit()
            db.refresh(warehouse)
            HistoryLogService.log_action(db, "warehouse", warehouse_id, "soft_delete", requester_id)
            return {"detail": "Warehouse deleted successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="warehouse",
            action="delete",
            entity_id=warehouse_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def delete_warehouse_permanent(warehouse_id: int, requester_id: int, db: Session = Depends(get_db)):
        warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        meta_data = {"id": warehouse.id, "name": warehouse.name}
        if has_approval_privileges(db, requester_id):
            db.delete(warehouse)
            db.commit()

            # Log permanent deletion
            HistoryLogService.log_action(db, "warehouse", warehouse_id, "delete_permanent", requester_id, meta_data)

            return {"detail": "Warehouse deleted permanently"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="warehouse",
            action="delete_permanent",
            entity_id=warehouse_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def archive_warehouse(warehouse_id: int, requester_id: int, db: Session = Depends(get_db)):
        warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not warehouse or not warehouse.is_active:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        if warehouse.is_deleted:
            raise HTTPException(status_code=400, detail="Warehouse is already deleted")

        if warehouse.is_archived:
            raise HTTPException(status_code=400, detail="Warehouse is already archived")

        if has_approval_privileges(db, requester_id):
            warehouse.is_archived = True
            warehouse.is_active = False
            warehouse.archived_at = datetime.now(UTC)
            warehouse.archived_by = requester_id

            db.commit()
            db.refresh(warehouse)  # Refresh to get updated relationships
            # Log archive action
            HistoryLogService.log_action(db, "warehouse", warehouse_id, "archive", requester_id)
            return {"detail": "Warehouse archived successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="warehouse",
            action="archive",
            entity_id=warehouse_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def restore_warehouse(warehouse_id: int, requester_id: int, db: Session = Depends(get_db)):
        warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not warehouse:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        if has_approval_privileges(db, requester_id):
            if warehouse.is_approved:
                warehouse.is_deleted = False
                warehouse.is_archived = False
                warehouse.is_active = True
            db.commit()
            # Log restore action
            HistoryLogService.log_action(db, "warehouse", warehouse_id, "restore", requester_id)
            return {"detail": "Warehouse restored successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="warehouse",
            action="restore",
            entity_id=warehouse_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)):
        warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not warehouse or not warehouse.is_active:
            if warehouse.is_archived:
                raise HTTPException(status_code=404, detail="Warehouse is archived")
            raise HTTPException(status_code=404, detail="Warehouse not found")
        return warehouse

    @staticmethod
    def list_warehouses(db: Session = Depends(get_db)):
        warehouses = db.query(Warehouse).filter(Warehouse.is_active == True).all()
        return warehouses

    @staticmethod
    def get_warehouses_by_location(location_id: int, db: Session = Depends(get_db)):
        """
        Fetch all warehouses in a given location.
        """
        return db.query(Warehouse).filter(Warehouse.location_id == location_id,
                                          Warehouse.is_active == True).all()

    # === for pending approvals use ===
    @staticmethod
    def direct_create(new_value: dict, db: Session = Depends(get_db)):
        """
        Directly creates a location without approval checks.
        """
        new_value = WarehouseCreate(**new_value)  # Convert dictionary to ProjectCreate model
        warehouse = db.query(Warehouse).filter(Warehouse.name == new_value.name).first()
        if warehouse:
            raise HTTPException(status_code=400, detail="Warehouse already exist")

        new_warehouse = Warehouse(**dict(new_value))
        new_warehouse.is_approved = True
        new_warehouse.is_active = True
        new_warehouse.created_by = new_value.created_by
        new_warehouse.created_at = datetime.now(UTC)

        db.add(new_warehouse)
        db.commit()
        db.refresh(new_warehouse)

    @staticmethod
    def direct_update(new_value: dict, entity_id: int, db: Session = Depends(get_db)):
        warehouse = db.query(Warehouse).filter(Warehouse.id == entity_id).first()
        if not warehouse or not warehouse.is_active:
            raise HTTPException(status_code=404, detail="Warehouse not found")
        for key, value in new_value.items():
            setattr(warehouse, key, value)
        db.commit()
        db.refresh(warehouse)
        return warehouse

    @staticmethod
    def direct_soft_delete(entity_id: int, db: Session = Depends(get_db)):
        warehouse = db.query(Warehouse).filter(Warehouse.id == entity_id).first()
        warehouse.is_deleted = True
        warehouse.is_active = False
        db.commit()
        db.refresh(warehouse)

    @staticmethod
    def direct_archive(entity_id: int, db: Session = Depends(get_db)):
        warehouse = db.query(Warehouse).filter(Warehouse.id == entity_id).first()
        warehouse.is_archived = True
        warehouse.is_active = False

        db.commit()
        db.refresh(warehouse)

    @staticmethod
    def direct_restore(entity_id: int, db: Session = Depends(get_db)):
        warehouse = db.query(Warehouse).filter(Warehouse.id == entity_id).first()
        warehouse.is_deleted = False
        warehouse.is_archived = False
        warehouse.is_active = True

        db.commit()
        db.refresh(warehouse)
