# src/app/model/stock.py

from datetime import datetime, UTC
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, validates
from src.app.core.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)  # Links to Item
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # Null if tied to a location
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)  # Null if tied to a location
    quantity = Column(Float, nullable=False, default=0)  # Allows decimal quantities
    last_updated = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    item = relationship("Item", back_populates="stocks")
    project = relationship("Project", back_populates="stocks")
    warehouse = relationship("Warehouse", back_populates="stocks")

    @validates("warehouse_id", "project_id")
    def validate_exclusive_relationship(self, key, value):
        if self.warehouse_id and self.project_id:
            raise ValueError("Stock cannot be tied to both warehouse and project simultaneously.")
        return value
