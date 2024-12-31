# src/app/schemas/project.py

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    project_name: str
    location_id: int


class ProjectResponse(BaseModel):
    id: int
    project_name: str
    location_id: int

    class Config:
        from_attributes = True  # Enable ORM compatibility


class ProjectUpdate(BaseModel):
    project_name: str
    location_id: int
