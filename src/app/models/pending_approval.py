# src/app/models/pending_approval.py
import json
from typing import Dict, Any

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.app.core.database import Base
from datetime import datetime, UTC
import enum


class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PendingApproval(Base):
    __tablename__ = "pending_approvals"

    id = Column(Integer, primary_key=True, index=True)
    entity = Column(String, nullable=False)  # Entity type (e.g., 'location', 'department')
    entity_id = Column(Integer, nullable=True)  # ID of the referenced entity
    action = Column(String, nullable=False)
    new_value = Column(JSONB, nullable=False)  # Stores the proposed new value as JSONB

    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Requested by
    requested_at = Column(DateTime, default=datetime.now(UTC))

    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)

    # Relationships
    requester = relationship("User", foreign_keys=[requested_by], back_populates="pending_approvals_requested")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="pending_approvals_approved")

    # Relationships with dynamic primary join
    department = relationship(
        "Department",
        primaryjoin="and_(PendingApproval.entity == 'department', PendingApproval.entity_id == Department.id)",
        foreign_keys="[PendingApproval.entity_id]",
        viewonly=True,
    )

    item = relationship(
        "Item",
        primaryjoin="and_(PendingApproval.entity == 'item', PendingApproval.entity_id == Item.id)",
        foreign_keys="[PendingApproval.entity_id]",
        viewonly=True,
    )

    stocks = relationship(
        "Stock",
        primaryjoin="and_(PendingApproval.entity == 'stocks', PendingApproval.entity_id == Stock.id)",
        foreign_keys="[PendingApproval.entity_id]",
        viewonly=True,
    )

    project = relationship(
        "Project",
        primaryjoin="and_(PendingApproval.entity == 'project', PendingApproval.entity_id == Project.id)",
        foreign_keys="[PendingApproval.entity_id]",
        viewonly=True,
    )

    warehouse = relationship(
        "Warehouse",
        primaryjoin="and_(PendingApproval.entity == 'warehouse', PendingApproval.entity_id == Warehouse.id)",
        foreign_keys="[PendingApproval.entity_id]",
        viewonly=True,
    )

    location = relationship(
        "Location",
        primaryjoin="and_(PendingApproval.entity == 'location', PendingApproval.entity_id == Location.id)",
        foreign_keys="[PendingApproval.entity_id]",
        viewonly=True,
    )

    # Unique constraint for actions other than "create"
    __table_args__ = (
        UniqueConstraint('entity', 'entity_id', 'action', name='uq_entity_entityid_action'),
    )

    # # Automatic serialization/deserialization of new_value
    # @property
    # def new_value_dict(self):
    #     """Deserialize the new_value string to a Python dict."""
    #     return json.loads(self.new_value)
    #
    # @new_value_dict.setter
    # def new_value_dict(self, value):
    #     """Serialize a Python dict to a JSON string."""
    #     self.new_value = json.dumps(value)
