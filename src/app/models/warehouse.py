# src/app/model/warehouse.py

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.app.core.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))

    location = relationship("Location", back_populates="warehouses")
    items = relationship("Item", secondary="warehouse_items", back_populates="warehouses")
