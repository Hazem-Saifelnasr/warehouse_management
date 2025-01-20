# src/app/services/item_service.py

import os
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, Depends
from src.app.core.database import get_db
from src.app.core.rbac import has_approval_privileges
from src.app.models import PendingApproval
from src.app.models.item import Item
from src.app.models.pending_approval import ApprovalStatus
from src.app.models.stock import Stock
from src.app.schemas.item import ItemCreate
from src.app.services.history_log_service import HistoryLogService
from src.app.services.pending_approval_service import PendingApprovalService


class ItemService:
    @staticmethod
    def create_item(item_data: ItemCreate, requester_id: int, db: Session = Depends(get_db)):
        # Step 1: Create the Item object
        existing_item = db.query(Item).filter(Item.item_code == item_data.item_code).first()
        if existing_item:
            raise HTTPException(status_code=400, detail="Item with this code already exists")

        # Step 2: Check if a pending approval for the same item_code already exists
        existing_request = db.query(PendingApproval).filter(
            PendingApproval.entity == "item",
            PendingApproval.action == "create",
            PendingApproval.approval_status == ApprovalStatus.PENDING,
            PendingApproval.new_value["item_code"].astext == item_data.item_code,
        ).first()

        if existing_request:
            raise HTTPException(status_code=400, detail="A pending approval request for this item code already exists")

        # Step 3: If user has approval privileges, create the item directly
        if has_approval_privileges(db, requester_id):
            new_item = Item(**dict(item_data))
            new_item.is_approved = True
            new_item.is_active = True
            new_item.created_by = requester_id
            new_item.created_at = datetime.now(UTC)

            db.add(new_item)  # Add the item to the session
            db.commit()
            db.refresh(new_item)  # Refresh to get the updated relationships

            HistoryLogService.log_action(db, "item", new_item.id, "create", requester_id)
            return new_item

        # Step 4: Add to pending approval
        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="item",
            entity_id=None,  # New item, no ID yet
            action="create",
            new_value_dict=item_data.model_dump(),
            requested_by=requester_id
        )

    @staticmethod
    def update_item(item_id: int, update_data: dict, requester_id: int, db: Session = Depends(get_db)):
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item or not item.is_active:
            raise HTTPException(status_code=404, detail="Item not found")

        if has_approval_privileges(db, requester_id):
            for key, value in update_data.items():
                setattr(item, key, value)
            item.updated_by = requester_id
            db.commit()
            db.refresh(item)

            HistoryLogService.log_action(db, "item", item_id, "update", requester_id)
            return item

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="item",
            entity_id=item_id,
            action="update",
            new_value_dict=update_data,
            requested_by=requester_id,
        )

    @staticmethod
    def delete_item_soft(item_id: int, requester_id: int, db: Session = Depends(get_db)):
        # Check if the item is referenced in stocks
        stock_count = db.query(Stock).filter(Stock.item_id == item_id).count()
        if stock_count > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete item. It is associated with existing stock."
            )

        item = db.query(Item).filter(Item.id == item_id).first()
        if not item or not item.is_active:
            raise HTTPException(status_code=404, detail="Item not found")

        if has_approval_privileges(db, requester_id):
            item.is_deleted = True
            item.is_active = False
            item.deleted_at = datetime.now(UTC)
            item.deleted_by = requester_id

            db.commit()
            db.refresh(item)
            HistoryLogService.log_action(db, "item", item_id, "soft_delete", requester_id)
            return {"detail": "Item deleted successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="item",
            action="delete",
            entity_id=item_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def delete_item_permanent(item_id: int, requester_id: int, db: Session = Depends(get_db)):
        # Check if the item is referenced in stocks
        stock_count = db.query(Stock).filter(Stock.item_id == item_id).count()
        if stock_count > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete item. It is associated with existing stock."
            )

        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        meta_data = {"id": item.id, "item_code": item.item_code, "name": item.name}
        if has_approval_privileges(db, requester_id):
            # Delete the photo file if it exists
            if item.photo and os.path.exists(os.path.join("src/assets", item.photo)):
                try:
                    os.remove(os.path.join("src/assets", item.photo))
                except Exception as e:
                    print(f"Error deleting file {item.photo}: {e}")

            db.delete(item)
            db.commit()
            # Log permanent deletion
            HistoryLogService.log_action(db, "item", item_id, "delete_permanent", requester_id, meta_data)

            return {"detail": "Item deleted permanently"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="item",
            action="delete_permanent",
            entity_id=item_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def archive_item(item_id: int, requester_id: int, db: Session = Depends(get_db)):
        # Check if the item is referenced in stocks
        stock_count = db.query(Stock).filter(Stock.item_id == item_id).count()
        if stock_count > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot archived item. It is associated with existing stock."
            )

        item = db.query(Item).filter(Item.id == item_id).first()
        if not item or not item.is_active:
            raise HTTPException(status_code=404, detail="Item not found")

        if item.is_deleted:
            raise HTTPException(status_code=400, detail="Item is already deleted")

        if item.is_archived:
            raise HTTPException(status_code=400, detail="Item is already archived")

        if has_approval_privileges(db, requester_id):
            item.is_archived = True
            item.is_active = False
            item.archived_at = datetime.now(UTC)
            item.archived_by = requester_id

            db.commit()
            db.refresh(item)  # Refresh to get updated relationships
            # Log archive action
            HistoryLogService.log_action(db, "item", item_id, "archive", requester_id)
            return {"detail": "Item archived successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="item",
            action="archive",
            entity_id=item_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def restore_item(item_id: int, requester_id: int, db: Session = Depends(get_db)):
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        if has_approval_privileges(db, requester_id):
            if item.is_approved:
                item.is_deleted = False
                item.is_archived = False
                item.is_active = True
            db.commit()
            # Log restore action
            HistoryLogService.log_action(db, "item", item_id, "restore", requester_id)
            return {"detail": "Item restored successfully"}

        return PendingApprovalService.submit_approval_request(
            db=db,
            entity="item",
            action="restore",
            entity_id=item_id,
            requested_by=requester_id,
            new_value_dict={},
        )

    @staticmethod
    def get_item(item_id: int, db: Session = Depends(get_db)):
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item or not item.is_active:
            if item.is_archived:
                raise HTTPException(status_code=404, detail="Item is archived")
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    @staticmethod
    def list_items(db: Session = Depends(get_db)):
        items = db.query(Item).filter(Item.is_active == True).all()
        return items

    @staticmethod
    def upload_item_photo(
            item_id: int,
            file: UploadFile,
            db: Session = Depends(get_db)
    ):
        """
        Upload a photo for a specific item and save it in the assets/photos directory.
        """
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item or not item.is_active:
            raise HTTPException(status_code=404, detail="Item not found")

        # Delete the photo file if it exists
        if item.photo and os.path.exists(os.path.join("src/assets", item.photo)):
            try:
                os.remove(os.path.join("src/assets", item.photo))
            except Exception as e:
                print(f"Error deleting file {item.photo}: {e}")

        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Must be an image.")

        # Ensure the directory exists
        directory = "src/assets/photos"
        os.makedirs(directory, exist_ok=True)

        # Save the file
        file_name = f"{item_id}_{file.filename}"
        file_path = os.path.join(directory, file_name)

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Update item with photo path
        item.photo = os.path.join("photos", file_name)
        db.commit()
        db.refresh(item)

        return {"detail": "Photo uploaded successfully"}

    # === for pending approvals use ===
    @staticmethod
    def direct_create(new_value: dict, db: Session = Depends(get_db)):
        """
        Directly creates an item without approval checks.
        """
        new_value = ItemCreate(**new_value)  # Convert dictionary to ItemCreate model
        item = db.query(Item).filter(Item.item_code == new_value.item_code).first()
        if item:
            raise HTTPException(status_code=400, detail="Item already exist")

        new_item = Item(**dict(new_value))
        new_item.is_approved = True
        new_item.is_active = True
        new_item.created_by = new_value.created_by
        new_item.created_at = datetime.now(UTC)

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

    @staticmethod
    def direct_update(new_value: dict, entity_id: int, db: Session = Depends(get_db)):
        item = db.query(Item).filter(Item.id == entity_id).first()
        if not item or not item.is_active:
            raise HTTPException(status_code=404, detail="Item not found")
        for key, value in new_value.items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def direct_soft_delete(entity_id: int, db: Session = Depends(get_db)):
        item = db.query(Item).filter(Item.id == entity_id).first()
        item.is_deleted = True
        item.is_active = False
        db.commit()
        db.refresh(item)

    @staticmethod
    def direct_archive(entity_id: int, db: Session = Depends(get_db)):
        item = db.query(Item).filter(Item.id == entity_id).first()
        item.is_archived = True
        item.is_active = False

        db.commit()
        db.refresh(item)

    @staticmethod
    def direct_restore(entity_id: int, db: Session = Depends(get_db)):
        item = db.query(Item).filter(Item.id == entity_id).first()
        item.is_deleted = False
        item.is_archived = False
        item.is_active = True

        db.commit()
        db.refresh(item)
