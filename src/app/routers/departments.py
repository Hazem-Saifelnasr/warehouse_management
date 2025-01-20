# src/app/routers/departments.py

from typing import Union
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models.department import Department
from src.app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate
from src.app.schemas.pending_approval import PendingApprovalResponse
from src.app.services.department_service import DepartmentService

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="departments", access_type="read")  # Highlight: Added decorator
def departments_page(request: Request, db: Session = Depends(get_db), page: int = 1, size: int = 10):
    departments_query = db.query(Department).filter(Department.is_active == True)
    total_departments = departments_query.count()  # Total number of items
    offset = (page - 1) * size
    total_pages = (total_departments + size - 1) // size  # Calculate total pages
    departments = departments_query.offset(offset).limit(size).all()
    return templates.TemplateResponse("departments.html", {
        "request": request,
        "departments": departments,
        "page": page,
        "size": size,
        "total_pages": total_pages,
        "user_id": request.state.user_id,
        "user_role": request.state.role
    })


@router.post("/add", response_model=Union[DepartmentResponse, PendingApprovalResponse])
@rbac_check(entity="departments", access_type="create")
def create_department(request: Request, department: DepartmentCreate, db: Session = Depends(get_db)):
    return DepartmentService.create_department(department, request.state.user_id, db)


@router.get("/list", response_model=list[DepartmentResponse])
@rbac_check(entity="departments", access_type="read")
def list_departments(request: Request, db: Session = Depends(get_db)):
    return DepartmentService.list_departments(db)


@router.put("/{department_id}", response_model=Union[DepartmentResponse, PendingApprovalResponse])
@rbac_check(entity="departments", access_type="write")
def update_department(request: Request, department_id: int, update_data: DepartmentUpdate, db: Session = Depends(get_db)):
    return DepartmentService.update_department(department_id, update_data, request.state.user_id, db)


@router.delete("/{department_id}")
@rbac_check(entity="departments", access_type="delete")
def delete_department_soft(request: Request, department_id: int, db: Session = Depends(get_db)):
    return DepartmentService.delete_department_soft(department_id, request.state.user_id, db)


@router.delete("/permanent/{department_id}")
@rbac_check(entity="departments", access_type="delete")
def delete_department_permanent(request: Request, department_id: int, db: Session = Depends(get_db)):
    return DepartmentService.delete_department_permanent(department_id, request.state.user_id, db)


@router.post("/archive/{department_id}")
@rbac_check(entity="departments", access_type="archive")
def archive_department(request: Request, department_id: int, db: Session = Depends(get_db)):
    return DepartmentService.archive_department(department_id, request.state.user_id, db)


@router.post("/restore/{department_id}")
@rbac_check(entity="departments", access_type="restore")
def restore_department(request: Request, department_id: int, db: Session = Depends(get_db)):
    return DepartmentService.restore_department(department_id, request.state.user_id, db)


@router.get("/{department_id}", response_model=DepartmentResponse)
@rbac_check(entity="departments", access_type="read")
def get_department(request: Request, department_id: int, db: Session = Depends(get_db)):
    return DepartmentService.get_department(department_id, db)
