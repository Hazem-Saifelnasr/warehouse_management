# src/app/models/history_log.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.app.core.database import Base


class HistoryLog(Base):
    __tablename__ = "history_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=True)
    entity_metadata = Column(JSONB, nullable=True)  # Store metadata as JSON
    action = Column(String, nullable=False)
    details = Column(Text, nullable=True)

    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_at = Column(DateTime, nullable=True)

    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_at = Column(DateTime, nullable=True)

    # Relationships
    requester = relationship("User", foreign_keys=[requested_by], back_populates="history_logs_requested")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="history_logs_approved")

    item = relationship(
        "Item",
        primaryjoin="and_(HistoryLog.entity == 'item', foreign(HistoryLog.entity_id) == Item.id)",
        viewonly=True
    )
    location = relationship(
        "Location",
        primaryjoin="and_(HistoryLog.entity == 'location', foreign(HistoryLog.entity_id) == Location.id)",
        viewonly=True
    )
    department = relationship(
        "Department",
        primaryjoin="and_(HistoryLog.entity == 'department', foreign(HistoryLog.entity_id) == Department.id)",
        viewonly=True
    )
    stocks = relationship(
        "Stock",
        primaryjoin="and_(HistoryLog.entity == 'stock', foreign(HistoryLog.entity_id) == Stock.id)",
        viewonly=True
    )
    project = relationship(
        "Project",
        primaryjoin="and_(HistoryLog.entity == 'project', foreign(HistoryLog.entity_id) == Project.id)",
        viewonly=True
    )
    warehouse = relationship(
        "Warehouse",
        primaryjoin="and_(HistoryLog.entity == 'warehouse', foreign(HistoryLog.entity_id) == Warehouse.id)",
        viewonly=True
    )
    invoice = relationship(
        "Invoice",
        primaryjoin="and_(HistoryLog.entity == 'invoice', foreign(HistoryLog.entity_id) == Invoice.id)",
        viewonly=True
    )
