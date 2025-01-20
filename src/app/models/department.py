# src/app/model/department.py
from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from src.app.core.database import Base
from src.app.models.pending_approval import ApprovalStatus


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    manager = Column(Integer, ForeignKey("users.id"), nullable=True)
    deputy_manager = Column(Integer, ForeignKey("users.id"), nullable=True)

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
    user = relationship("User", foreign_keys="[User.department_id]", back_populates="department")
    pending_approval = relationship(
        "PendingApproval",
        primaryjoin="and_(PendingApproval.entity == 'department', foreign(PendingApproval.entity_id) == Department.id)",
        viewonly=True
    )
    history_logs = relationship(
        "HistoryLog",
        primaryjoin="and_(HistoryLog.entity == 'department', foreign(HistoryLog.entity_id) == Department.id)",
        viewonly=True
    )
