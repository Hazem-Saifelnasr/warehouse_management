# src/app/model/location.py

from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.app.core.database import Base
from src.app.models.pending_approval import ApprovalStatus


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

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
    warehouse = relationship("Warehouse", back_populates="location")
    project = relationship("Project", back_populates="location")
    pending_approval = relationship(
        "PendingApproval",
        primaryjoin="and_(PendingApproval.entity == 'location', foreign(PendingApproval.entity_id) == Location.id)",
        viewonly=True
    )
    history_logs = relationship(
        "HistoryLog",
        primaryjoin="and_(HistoryLog.entity == 'location', foreign(HistoryLog.entity_id) == Location.id)",
        viewonly=True
    )
