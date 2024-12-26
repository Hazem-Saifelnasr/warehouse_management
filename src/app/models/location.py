# src/app/model/location.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.app.core.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    warehouses = relationship("Warehouse", back_populates="location")
    projects = relationship("Project", back_populates="location")
