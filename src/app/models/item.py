# src/app/model/item.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from src.app.core.database import Base
from src.app.models.pending_approval import ApprovalStatus


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String, unique=True, index=True, nullable=False)  # Midas-specific code
    name = Column(String, index=True, nullable=False)
    unified_code = Column(String, nullable=True)
    description = Column(String)
    photo = Column(String)
    unit_of_measure = Column(String, nullable=False)  # e.g., "pcs", "m", "kg"

    category = Column(String, nullable=True)  # Main category of the item
    subcategory = Column(String, nullable=True)  # Subcategory of the item
    brand = Column(String, nullable=True)  # Brand or manufacturer
    model = Column(String, nullable=True)  # Model number or name
    serial_number = Column(String, nullable=True)  # Serial number (if applicable)

    bar_code = Column(String, nullable=True)
    qr_code = Column(String, nullable=True)
    remarks = Column(String, nullable=True)

    # Approval and archiving
    is_approved = Column(Boolean, default=False)
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    is_archived = Column(Boolean, default=False)
    archived_at = Column(DateTime, nullable=True)
    archived_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Soft delete
    is_deleted = Column(Boolean, default=False)

    is_active = Column(Boolean, default=False)

    # Audit fields
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, onupdate=datetime.now(UTC))
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    stocks = relationship("Stock", back_populates="item")  # Connects to the Stock table
    pending_approval = relationship(
        "PendingApproval",
        primaryjoin="and_(PendingApproval.entity == 'item', foreign(PendingApproval.entity_id) == Item.id)",
        viewonly=True
    )
    history_logs = relationship(
        "HistoryLog",
        primaryjoin="and_(HistoryLog.entity == 'item', foreign(HistoryLog.entity_id) == Item.id)",
        viewonly=True
    )

    def soft_delete(self):
        self.is_active = False
        self.is_deleted = True

    def restore(self):
        self.is_active = True
        self.is_deleted = False
        self.is_archived = False

    def archive(self):
        self.is_archived = True

    def active(self):
        self.is_active = True

    def inactive(self):
        self.is_active = False

# class Item(Base):
#     __tablename__ = "items"  # Name of the table in the database
#
#     # Core fields
#     item_id = Column(Integer, primary_key=True, autoincrement=True)
#     item_code = Column(String(50), unique=True, nullable=False)  # Unique item code
#     name = Column(String(255), nullable=False)  # Item name or description
#     midas_code = Column(String(50), nullable=True)  # Unified code for related items
#     category = Column(String(100), nullable=True)  # Main category of the item
#     subcategory = Column(String(100), nullable=True)  # Subcategory of the item
#     brand = Column(String(100), nullable=True)  # Brand or manufacturer
#     model = Column(String(100), nullable=True)  # Model number or name

#     # Attachments
#     manual_url = Column(String(255), nullable=True)  # URL for the product manual
#     certificate_url = Column(String(255), nullable=True)  # URL for compliance or origin certificates
