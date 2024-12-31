# src/app/routers/projects.py

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models.project import Project
from src.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.models.location import Location


router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="projects", access_type="read")  # Highlight: Added decorator
def projects_page(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).options(joinedload(Project.location)).all()
    locations = db.query(Location).all()
    return templates.TemplateResponse("projects.html", {
        "request": request,
        "projects": projects,
        "locations": locations,
    })


@router.post("/add", response_model=ProjectResponse)
@rbac_check(entity="projects", access_type="create")  # Highlight: Added decorator
def create_project(request: Request, project: ProjectCreate, db: Session = Depends(get_db)):
    # Check for duplicate project name within the same location
    if db.query(Project).filter(Project.project_name == project.project_name,
                                Project.location_id == project.location_id).first():
        raise HTTPException(status_code=400, detail="Project with this name already exists in the specified location")

    new_project = Project(**dict(project))
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("/list", response_model=list[ProjectResponse])
@rbac_check(entity="projects", access_type="read")  # Highlight: Added decorator
def list_projects(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
@rbac_check(entity="projects", access_type="read")  # Highlight: Added decorator
def get_project(request: Request, project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
@rbac_check(entity="projects", access_type="write")  # Highlight: Added decorator
def update_project(request: Request, project_id: int, update_data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
@rbac_check(entity="projects", access_type="delete")  # Highlight: Added decorator
def delete_project(request: Request, project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"detail": "Project deleted successfully"}


@router.get("/location/{location_id}", response_model=list[ProjectResponse])
@rbac_check(entity="projects", access_type="read")  # Highlight: Added decorator
def get_projects_by_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    """
    Fetch all projects for a given location.
    """
    return db.query(Project).filter(Project.location_id == location_id).all()
