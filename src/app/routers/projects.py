# src/app/routers/projects.py

from typing import Union
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session, joinedload
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models.project import Project
from src.app.schemas.pending_approval import PendingApprovalResponse
from src.app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from src.app.models.location import Location
from src.app.services.project_service import ProjectService

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="projects", access_type="read")  
def projects_page(request: Request, db: Session = Depends(get_db), page: int = 1, size: int = 10):
    projects_query = db.query(Project).options(joinedload(Project.location)).filter(Project.is_active == True)
    total_projects = projects_query.count()  # Total number of items
    offset = (page - 1) * size
    total_pages = (total_projects + size - 1) // size  # Calculate total pages
    projects = projects_query.offset(offset).limit(size).all()
    locations = db.query(Location).filter(Location.is_active == True).all()
    return templates.TemplateResponse("projects.html", {
        "request": request,
        "projects": projects,
        "locations": locations,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "user_id": request.state.user_id,
        "user_role": request.state.role
    })


@router.post("/add", response_model=Union[ProjectResponse, PendingApprovalResponse])
@rbac_check(entity="projects", access_type="create")  
def create_project(request: Request, project: ProjectCreate, db: Session = Depends(get_db)):
    return ProjectService.create_project(project, request.state.user_id, db)


@router.get("/list", response_model=list[ProjectResponse])
@rbac_check(entity="projects", access_type="read")
def list_projects(request: Request, db: Session = Depends(get_db)):
    return ProjectService.list_projects(db)


@router.put("/{project_id}", response_model=Union[ProjectResponse, PendingApprovalResponse])
@rbac_check(entity="projects", access_type="write")
def update_project(request: Request, project_id: int, update_data: ProjectUpdate, db: Session = Depends(get_db)):
    return ProjectService.update_project(project_id, update_data, request.state.user_id, db)


@router.delete("/{project_id}")
@rbac_check(entity="projects", access_type="delete")
def delete_project_soft(request: Request, project_id: int, db: Session = Depends(get_db)):
    return ProjectService.delete_project_soft(project_id, request.state.user_id, db)


@router.delete("/permanent/{project_id}")
@rbac_check(entity="projects", access_type="delete")
def delete_project_permanent(request: Request, project_id: int, db: Session = Depends(get_db)):
    return ProjectService.delete_project_permanent(project_id, request.state.user_id, db)


@router.post("/archive/{project_id}")
@rbac_check(entity="projects", access_type="archive")
def archive_project(request: Request, project_id: int, db: Session = Depends(get_db)):
    return ProjectService.archive_project(project_id, request.state.user_id, db)


@router.post("/restore/{project_id}")
@rbac_check(entity="projects", access_type="restore")
def restore_project(request: Request, project_id: int, db: Session = Depends(get_db)):
    return ProjectService.restore_project(project_id, request.state.user_id, db)


@router.get("/{project_id}", response_model=ProjectResponse)
@rbac_check(entity="projects", access_type="read")
def get_project(request: Request, project_id: int, db: Session = Depends(get_db)):
    return ProjectService.get_project(project_id, db)


@router.get("/location/{location_id}", response_model=list[ProjectResponse])
@rbac_check(entity="projects", access_type="read")  
def get_projects_by_location(request: Request, location_id: int, db: Session = Depends(get_db)):
    return ProjectService.get_projects_by_location(location_id, db)
