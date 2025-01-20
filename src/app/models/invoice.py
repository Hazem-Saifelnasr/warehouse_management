# src/app/model/invoice.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from src.app.core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, index=True, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    invoice_type = Column(Enum("external", "internal", name="invoice_type"), nullable=False)  # External or Internal

    total_cost = Column(Float, nullable=False)  # Total amount for the invoice
    total_price = Column(Float, nullable=True)
    profit_margin = Column(Float, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))

    # Relationships
    project = relationship("Project", back_populates="invoice")
    invoice_items = relationship("InvoiceItem", back_populates="invoice")

    history_logs = relationship(
        "HistoryLog",
        primaryjoin="and_(HistoryLog.entity == 'invoice', foreign(HistoryLog.entity_id) == Invoice.id)",
        viewonly=True
    )


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)

    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)  # Price per unit (can be cost or selling price based on invoice type)
    total_price = Column(Float, nullable=False)  # Quantity * Unit Price

    # Relationships
    invoice = relationship("Invoice", back_populates="invoice_items")
    stock = relationship("Stock", back_populates="invoice_items")
