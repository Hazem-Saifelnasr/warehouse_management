# src/app/model/warehouse.py

from datetime import datetime, UTC
from sqlalchemy import Column, String, Integer, ForeignKey, Float, Text, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from src.app.core.database import Base
from src.app.models.pending_approval import ApprovalStatus


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    capacity = Column(Float, nullable=True)  # Capacity of the warehouse (optional)
    description = Column(Text, nullable=True)  # Additional description

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
    location = relationship("Location", back_populates="warehouse")
    stocks = relationship("Stock", back_populates="warehouse")
    pending_approval = relationship(
        "PendingApproval",
        primaryjoin="and_(PendingApproval.entity == 'warehouse', foreign(PendingApproval.entity_id) == Warehouse.id)",
        viewonly=True
    )
    history_logs = relationship(
        "HistoryLog",
        primaryjoin="and_(HistoryLog.entity == 'warehouse', foreign(HistoryLog.entity_id) == Warehouse.id)",
        viewonly=True
    )
