# src/app/services/item_service.py
import os

from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from src.app.models.item import Item
from src.app.models.stock import Stock
from src.app.schemas.item import ItemCreate


class ItemService:
    @staticmethod
    def create_item(db: Session, item_data: ItemCreate):
        # Step 1: Create the Item object
        if db.query(Item).filter(Item.item_code == item_data.item_code,).first():
            raise HTTPException(status_code=400, detail="Item code already exists")

        new_item = Item(
            item_code=item_data.item_code,
            description=item_data.description,
            photo=item_data.photo,
            unit_of_measure=item_data.unit_of_measure
        )
        db.add(new_item)  # Add the item to the session
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
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        for key, value in update_data.items():
            setattr(item, key, value)

        db.commit()
        db.refresh(item)  # Refresh to get updated relationships
        return item

    @staticmethod
    def delete_item(db: Session, item_id: int):
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

        # Delete the photo file if it exists
        if item.photo and os.path.exists(os.path.join("src/assets", item.photo)):
            try:
                os.remove(os.path.join("src/assets", item.photo))
            except Exception as e:
                print(f"Error deleting file {item.photo}: {e}")

        db.delete(item)
        db.commit()
        return {"detail": "Item deleted successfully"}

    @staticmethod
    def list_items(db: Session):
        return db.query(Item).all()

    @staticmethod
    def upload_item_photo(
            db: Session,
            item_id: int,
            file: UploadFile
    ):
        """
        Upload a photo for a specific item and save it in the assets/photos directory.
        """
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
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
