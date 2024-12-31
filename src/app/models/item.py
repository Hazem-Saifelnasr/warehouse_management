# src/app/model/item.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from src.app.core.database import Base


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    photo = Column(String)
    unit_of_measure = Column(String, nullable=False)  # e.g., "pcs", "m", "kg"

    # # Soft delete and archive fields
    # is_deleted = Column(Boolean, default=False)
    # is_archived = Column(Boolean, default=False)
    # is_approved = Column(Boolean, default=False)

    # Relationships
    stocks = relationship("Stock", back_populates="item")  # Connects to the Stock table

# # Update Queries to Exclude Deleted and Archived Items
# def get_all_items(db: Session):
#     return db.query(Item).filter(Item.is_deleted == False, Item.is_archived == False).all()
#
#
# @router.delete("/{item_id}/soft-delete", response_model=ItemResponse)
# def soft_delete_item(item_id: int, db: Session = Depends(get_db)):
#     item = db.query(Item).filter(Item.id == item_id).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#
#     item.is_deleted = True
#     db.commit()
#     return {"detail": "Item soft deleted successfully"}
#
# @router.post("/{item_id}/archive", response_model=ItemResponse)
# def archive_item(item_id: int, db: Session = Depends(get_db)):
#     item = db.query(Item).filter(Item.id == item_id).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#
#     item.is_archived = True
#     db.commit()
#     return {"detail": "Item archived successfully"}
#
# @router.post("/{item_id}/restore", response_model=ItemResponse)
# def restore_item(item_id: int, db: Session = Depends(get_db)):
#     item = db.query(Item).filter(Item.id == item_id).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#
#     item.is_deleted = False
#     item.is_archived = False
#     db.commit()
#     return {"detail": "Item restored successfully"}
#
# @router.post("/{item_id}/approve", response_model=ItemResponse)
# def approve_item(item_id: int, db: Session = Depends(get_db)):
#     item = db.query(Item).filter(Item.id == item_id).first()
#     if not item:
#         raise HTTPException(status_code=404, detail="Item not found")
#
#     item.is_approved = True  # Add an `is_approved` field in your model if necessary
#     db.commit()
#     return {"detail": "Item approved successfully"}
#
# function softDeleteItem(itemId) {
#     if (confirm("Are you sure you want to delete this item?")) {
#         fetch(`/items/${itemId}/soft-delete`, { method: "DELETE" })
#             .then(response => {
#                 if (response.ok) {
#                     alert("Item deleted successfully!");
#                     window.location.reload();
#                 } else {
#                     alert("Failed to delete item.");
#                 }
#             });
#     }
# }
#
# function archiveItem(itemId) {
#     fetch(`/items/${itemId}/archive`, { method: "POST" })
#         .then(response => {
#             if (response.ok) {
#                 alert("Item archived successfully!");
#                 window.location.reload();
#             } else {
#                 alert("Failed to archive item.");
#             }
#         });
# }
#
# function restoreItem(itemId) {
#     fetch(`/items/${itemId}/restore`, { method: "POST" })
#         .then(response => {
#             if (response.ok) {
#                 alert("Item restored successfully!");
#                 window.location.reload();
#             } else {
#                 alert("Failed to restore item.");
#             }
#         });
# }
#
# function approveItem(itemId) {
#     fetch(`/items/${itemId}/approve`, { method: "POST" })
#         .then(response => {
#             if (response.ok) {
#                 alert("Item approved successfully!");
#                 window.location.reload();
#             } else {
#                 alert("Failed to approve item.");
#             }
#         });
# }

