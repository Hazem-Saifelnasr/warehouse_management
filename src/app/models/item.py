# src/app/model/item.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.app.core.database import Base
from src.app.models.associations import warehouse_items, project_items


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String, unique=True, index=True)
    description = Column(String)
    photo = Column(String)
    total_qty = Column(Integer)
    location_id = Column(Integer, ForeignKey('locations.id'))

    location = relationship("Location", back_populates="items")
    warehouses = relationship("Warehouse", secondary=warehouse_items, back_populates="items")
    projects = relationship("Project", secondary=project_items, back_populates="items")
