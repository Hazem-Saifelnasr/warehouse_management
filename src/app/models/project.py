# src/app/model/project.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.app.core.database import Base
from src.app.models.associations import project_items


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, unique=True)
    location_id = Column(Integer, ForeignKey('locations.id'))

    location = relationship("Location", back_populates="projects")
    items = relationship("Item", secondary=project_items, back_populates="projects")
