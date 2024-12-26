# src/app/model/item.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.app.core.database import Base


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    photo = Column(String)
    unit_of_measure = Column(String, nullable=False)  # e.g., "pcs", "m", "kg"

    # Relationships
    stocks = relationship("Stock", back_populates="item")  # Connects to the Stock table
