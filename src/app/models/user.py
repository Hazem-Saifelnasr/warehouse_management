# src/app/model/user.py
from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from src.app.core.database import Base
from src.app.models.pending_approval import ApprovalStatus


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    position = Column(String, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), index=True)
    direct_manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    role = Column(String)  # "admin" or "user"

    is_superuser = Column(Boolean, default=False)

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
    direct_manager = relationship("User", foreign_keys=[direct_manager_id], remote_side="User.id")
    permissions = relationship("Permission", back_populates="user")
    department = relationship("Department", foreign_keys=[department_id], back_populates="user")

    pending_approvals_requested = relationship("PendingApproval", foreign_keys="[PendingApproval.requested_by]",
                                               back_populates="requester")
    pending_approvals_approved = relationship("PendingApproval", foreign_keys="[PendingApproval.approved_by]",
                                              back_populates="approver")

    history_logs_requested = relationship("HistoryLog", foreign_keys="[HistoryLog.requested_by]",
                                          back_populates="requester")
    history_logs_approved = relationship("HistoryLog", foreign_keys="[HistoryLog.approved_by]",
                                         back_populates="approver")
