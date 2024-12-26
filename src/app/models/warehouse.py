# src/app/model/warehouse.py

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.app.core.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

    location = relationship("Location", back_populates="warehouses")
    stocks = relationship("Stock", back_populates="warehouse")
