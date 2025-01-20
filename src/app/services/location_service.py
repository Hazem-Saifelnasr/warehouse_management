# src/app/services/location_service.py

from datetime import datetime, UTC
from fastapi import HTTPException, Depends
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.core.rbac import has_approval_privileges
from src.app.models import PendingApproval, ApprovalStatus
from src.app.models.location import Location
from src.app.schemas.location import LocationCreate
from src.app.schemas.project import ProjectResponse
from src.app.schemas.warehouse import WarehouseResponse
from src.app.services.history_log_service import HistoryLogService
from src.app.services.pending_approval_service import PendingApprovalService


class LocationService:
    @staticmethod
    def create_location(location: LocationCreate, requester_id: int, db: Session = Depends(get_db)):
        # Step 1: Create the Location object
        existing_location = db.query(Location).filter(Location.name == location.name).first()
        if existing_location:
            raise HTTPException(status_code=400, detail="Location with this name already exists")

        # Step 2: Check if a pending approval for the same name already exists
        existing_request = db.query(PendingApproval).filter(
            PendingApproval.entity == "location",
            PendingApproval.action == "create",
            PendingApproval.approval_status == ApprovalStatus.PENDING,
            PendingApproval.new_value.cast(JSONB)["name"].astext == location.name,
        ).first()

        if existing_request:
            raise HTTPException(status_code=400,
                                detail="A pending approval request for this location name already exists")

        # Step 3: If user has approval privileges, create the item directly
        if has_approval_privileges(db, requester_id):
            new_location = Location(**dict(location))
            new_location.is_approved = True
            new_location.is_active = True
            new_location.created_by = requester_id
            new_location.created_at = datetime.now(UTC)

            # new_location = Location(**dict(location))
            db.add(new_location)  # Add the location to the session
            db.commit()
            db.refresh(new_location)  # Refresh to get the updated relationships

            HistoryLogService.log_action(db, "location", new_location.id, "create", requester_id)
            return new_location

        # Step 4: Add to pending approval
        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="location",
            entity_id=None,  # New location, no ID yet
            action="create",
            new_value_dict=location.model_dump(),
            requested_by=requester_id
        )

    @staticmethod
    def update_location(location_id: int, update_data: dict, requester_id: int, db: Session = Depends(get_db)):
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location or not location.is_active:
            raise HTTPException(status_code=404, detail="Location not found")

        if has_approval_privileges(db, requester_id):
            for key, value in update_data.items():
                setattr(location, key, value)
            location.updated_by = requester_id
            db.commit()
            db.refresh(location)

            HistoryLogService.log_action(db, "location", location_id, "update", requester_id)
            return location

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="location",
            entity_id=location_id,
            action="update",
            new_value_dict=update_data,
            requested_by=requester_id,
        )

    @staticmethod
    def delete_location_soft(location_id: int, requester_id: int, db: Session = Depends(get_db)):
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location or not location.is_active:
            raise HTTPException(status_code=404, detail="Location not found")

        if has_approval_privileges(db, requester_id):
            location.is_deleted = True
            location.is_active = False
            location.deleted_at = datetime.now(UTC)
            location.deleted_by = requester_id

            db.commit()
            db.refresh(location)
            HistoryLogService.log_action(db, "location", location_id, "soft_delete", requester_id)
            return {"detail": "Location deleted successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="location",
            action="delete",
            entity_id=location_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def delete_location_permanent(location_id: int, requester_id: int, db: Session = Depends(get_db)):
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")

        meta_data = {"id": location.id, "name": location.name}
        if has_approval_privileges(db, requester_id):
            db.delete(location)
            db.commit()

            # Log permanent deletion
            HistoryLogService.log_action(db, "location", location_id, "delete_permanent", requester_id, meta_data)

            return {"detail": "Location deleted permanently"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="location",
            action="delete_permanent",
            entity_id=location_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def archive_location(location_id: int, requester_id: int, db: Session = Depends(get_db)):
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location or not location.is_active:
            raise HTTPException(status_code=404, detail="Location not found")

        if location.is_deleted:
            raise HTTPException(status_code=400, detail="Location is already deleted")

        if location.is_archived:
            raise HTTPException(status_code=400, detail="Location is already archived")

        if has_approval_privileges(db, requester_id):
            location.is_archived = True
            location.is_active = False
            location.archived_at = datetime.now(UTC)
            location.archived_by = requester_id

            db.commit()
            db.refresh(location)  # Refresh to get updated relationships
            # Log archive action
            HistoryLogService.log_action(db, "location", location_id, "archive", requester_id)
            return {"detail": "Location archived successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="location",
            action="archive",
            entity_id=location_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def restore_location(location_id: int, requester_id: int, db: Session = Depends(get_db)):
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            raise HTTPException(status_code=404, detail="Warehouse not found")

        if has_approval_privileges(db, requester_id):
            if location.is_approved:
                location.is_deleted = False
                location.is_archived = False
                location.is_active = True
            db.commit()
            # Log restore action
            HistoryLogService.log_action(db, "location", location_id, "restore", requester_id)
            return {"detail": "Location restored successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="location",
            action="restore",
            entity_id=location_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def get_location(location_id: int, db: Session = Depends(get_db)):
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location or not location.is_active:
            if location.is_archived:
                raise HTTPException(status_code=404, detail="Location is archived")
            raise HTTPException(status_code=404, detail="Location not found")
        return location

    @staticmethod
    def list_locations(db: Session = Depends(get_db)):
        locations = db.query(Location).filter(Location.is_active == True).all()
        return locations

    @staticmethod
    def get_warehouses_and_projects(location_id: int, db: Session = Depends(get_db)):
        """
        Get all warehouses and projects in a specific location.
        """
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location or not location.is_active:
            raise HTTPException(status_code=404, detail="Location not found")

        warehouses = location.warehouses
        projects = location.projects

        return {
            "warehouses": [WarehouseResponse.model_validate(warehouse) for warehouse in warehouses],
            "projects": [ProjectResponse.model_validate(project) for project in projects]
        }

    # === for pending approvals use ===
    @staticmethod
    def direct_create(new_value: dict, db: Session = Depends(get_db)):
        """
        Directly creates a location without approval checks.
        """
        new_value = LocationCreate(**new_value)  # Convert dictionary to LocationCreate model
        location = db.query(Location).filter(Location.name == new_value.name).first()
        if location:
            raise HTTPException(status_code=400, detail="Location already exist")

        new_location = Location(**dict(new_value))
        new_location.is_approved = True
        new_location.is_active = True
        new_location.created_by = new_value.created_by
        new_location.created_at = datetime.now(UTC)

        db.add(new_location)
        db.commit()
        db.refresh(new_location)

    @staticmethod
    def direct_update(new_value: dict, entity_id: int, db: Session = Depends(get_db)):
        location = db.query(Location).filter(Location.id == entity_id).first()
        if not location or not location.is_active:
            raise HTTPException(status_code=404, detail="Location not found")
        for key, value in new_value.items():
            setattr(location, key, value)
        db.commit()
        db.refresh(location)
        return location

    @staticmethod
    def direct_soft_delete(entity_id: int, db: Session = Depends(get_db)):
        location = db.query(Location).filter(Location.id == entity_id).first()
        location.is_deleted = True
        location.is_active = False
        db.commit()
        db.refresh(location)

    @staticmethod
    def direct_archive(entity_id: int, db: Session = Depends(get_db)):
        location = db.query(Location).filter(Location.id == entity_id).first()
        location.is_archived = True
        location.is_active = False

        db.commit()
        db.refresh(location)

    @staticmethod
    def direct_restore(entity_id: int, db: Session = Depends(get_db)):
        location = db.query(Location).filter(Location.id == entity_id).first()
        location.is_deleted = False
        location.is_archived = False
        location.is_active = True

        db.commit()
        db.refresh(location)
