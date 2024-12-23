# src/app/services/item_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.app.models.item import Item
from src.app.schemas.item import ItemCreate
from src.app.models.warehouse import Warehouse
from src.app.models.project import Project


class ItemService:
    @staticmethod
    def create_item(db: Session, item_data: ItemCreate):
        # Step 1: Create the Item object
        new_item = Item(
            item_code=item_data.item_code,
            description=item_data.description,
            photo=item_data.photo,
            total_qty=item_data.total_qty,
            location_id=item_data.location_id
        )
        db.add(new_item)  # Add the item to the session
        db.flush()        # Flush to assign the ID and persist it in the session

        # Step 2: Associate the item with warehouses
        if item_data.warehouse_ids:
            warehouses = db.query(Warehouse).filter(Warehouse.id.in_(item_data.warehouse_ids)).all()
            new_item.warehouses.extend(warehouses)

        # Step 3: Associate the item with projects
        if item_data.project_ids:
            projects = db.query(Project).filter(Project.id.in_(item_data.project_ids)).all()
            new_item.projects.extend(projects)

        # Step 4: Commit and refresh
        db.commit()
        db.refresh(new_item)  # Refresh to get the updated relationships
        return new_item

    @staticmethod
    def get_item(db: Session, item_id: int):
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    @staticmethod
    def update_item(db: Session, item_id: int, update_data: dict):
        # Step 1: Fetch the item
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Step 2: Handle scalar fields
        scalar_fields = {"item_code", "description", "photo", "total_qty", "location_id"}
        for key, value in update_data.items():
            if key in scalar_fields:
                setattr(item, key, value)

        # Step 3: Update associations with warehouses
        if "warehouse_ids" in update_data and update_data["warehouse_ids"] is not None:
            warehouses = db.query(Warehouse).filter(Warehouse.id.in_(update_data["warehouse_ids"])).all()
            item.warehouses = warehouses  # Replace existing warehouses with the new list

        # Step 4: Update associations with projects
        if "project_ids" in update_data and update_data["project_ids"] is not None:
            projects = db.query(Project).filter(Project.id.in_(update_data["project_ids"])).all()
            item.projects = projects  # Replace existing projects with the new list

        # Step 5: Commit the changes
        db.commit()
        db.refresh(item) # Refresh to get updated relationships
        return item

    @staticmethod
    def delete_item(db: Session, item_id: int):
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        db.delete(item)
        db.commit()
        return {"detail": "Item deleted successfully"}

    @staticmethod
    def get_items_by_location(db: Session, location_id: int):
        items = db.query(Item).filter(Item.location_id == location_id).all()
        if not items:
            raise HTTPException(status_code=404, detail="No items found for this location.")
        return items

    @staticmethod
    def get_items_by_warehouse(db: Session, warehouse_id: int):
        items = db.query(Item).join(Item.warehouses).filter(Item.warehouses.any(id=warehouse_id)).all()
        if not items:
            raise HTTPException(status_code=404, detail="No items found for this warehouse.")
        return items

    @staticmethod
    def get_items_by_project(db: Session, project_id: int):
        items = db.query(Item).join(Item.projects).filter(Item.projects.any(id=project_id)).all()
        if not items:
            raise HTTPException(status_code=404, detail="No items found for this project.")
        return items

    @staticmethod
    def list_items(db: Session):
        items = db.query(Item).all()
        return items
