# src/app/routers/projects.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.models.project import Project
from src.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # Check for duplicate project name within the same location
    if db.query(Project).filter(Project.project_name == project.project_name,
                                Project.location_id == project.location_id).first():
        raise HTTPException(status_code=400, detail="Project with this name already exists in the specified location")

    new_project = Project(**dict(project))
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, update_data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"detail": "Project deleted successfully"}


@router.get("/", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects


@router.get("/location/{location_id}", response_model=list[ProjectResponse])
def get_projects_by_location(location_id: int, db: Session = Depends(get_db)):
    """
    Fetch all projects for a given location.
    """
    return db.query(Project).filter(Project.location_id == location_id).all()
