# src/app/model/stock.py

from datetime import datetime, UTC
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship, validates
from src.app.core.database import Base
from src.app.models.pending_approval import ApprovalStatus


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)  # Links to Item
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # Null if tied to a location
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)  # Null if tied to a location
    quantity = Column(Float, nullable=False, default=0)  # Allows decimal quantities
    cost_price = Column(Float, nullable=False)  # Price at the time of purchase
    selling_price = Column(Float, nullable=False)  # Selling price for external invoice
    boq_code = Column(String, nullable=True, index=True)  # BOQ-specific code for project items

    # Supplier information
    supplier_name = Column(String, nullable=True)  # Supplier name
    supplier_code = Column(String, nullable=True)  # Supplier-specific code
    supplier_contact = Column(String, nullable=True)  # Supplier contact details

    # Origin information
    country_of_origin = Column(String, nullable=True)  # Country where the item was manufactured
    import_date = Column(DateTime, nullable=True)  # Date when the item was imported
    export_date = Column(DateTime, nullable=True)  # Date when the item was exported

    # Additional information
    expiry_date = Column(DateTime, nullable=True)  # Expiration date (if applicable)
    production_date = Column(DateTime, nullable=True)  # Production date

    # Pricing and cost
    currency = Column(String, nullable=True)  # Currency used (e.g., USD, EUR)
    discount_rate = Column(Float, nullable=True)  # Discount rate

    # Physical properties
    stock_condition = Column(String, nullable=True)  # Condition (e.g., new, used, damaged)
    color = Column(String, nullable=True)  # Item color
    size = Column(String, nullable=True)  # Item size or dimensions
    weight = Column(Float, nullable=True)  # Item weight
    material = Column(String, nullable=True)  # Material the item is made of
    barcode = Column(String, nullable=True)  # Barcode

    # Warranty and maintenance
    warranty_period = Column(Integer, nullable=True)  # Warranty period in months
    remarks = Column(Text, nullable=True)  # Additional notes or comments

    # Approval and archiving
    is_approved = Column(Boolean, default=False)
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=datetime.now(UTC))
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    updated_at = Column(DateTime, onupdate=datetime.now(UTC))
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    item = relationship("Item", back_populates="stocks")
    project = relationship("Project", back_populates="stocks")
    warehouse = relationship("Warehouse", back_populates="stocks")
    invoice_items = relationship("InvoiceItem", back_populates="stock")
    pending_approval = relationship(
        "PendingApproval",
        primaryjoin="and_(PendingApproval.entity == 'stock', foreign(PendingApproval.entity_id) == Stock.id)",
        viewonly=True
    )
    history_logs = relationship(
        "HistoryLog",
        primaryjoin="and_(HistoryLog.entity == 'stock', foreign(HistoryLog.entity_id) == Stock.id)",
        viewonly=True
    )

    @validates("warehouse_id", "project_id")
    def validate_exclusive_relationship(self, key, value):
        if self.warehouse_id and self.project_id:
            raise ValueError("Stock cannot be tied to both warehouse and project simultaneously.")
        return value

