# src/app/model/project.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.app.core.database import Base


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, unique=True, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

    location = relationship("Location", back_populates="projects")
    stocks = relationship("Stock", back_populates="project")
