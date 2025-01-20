# src/app/routers/pending_approvals.py

from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models.pending_approval import PendingApproval, ApprovalStatus
from src.app.services.pending_approval_service import PendingApprovalService

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="pending_approvals", access_type="manage")  # Highlight: Added decorator
def pending_approvals_page(request: Request, db: Session = Depends(get_db), page: int = 1, size: int = 10):
    total_pending = db.query(PendingApproval).filter(PendingApproval.approval_status ==
                                                     ApprovalStatus.PENDING).count()  # Total number of items

    offset = (page - 1) * size
    pending_approvals = db.query(PendingApproval).filter(PendingApproval.approval_status ==
                                                         ApprovalStatus.PENDING).offset(offset).limit(size).all()

    return templates.TemplateResponse("pending_approvals.html", {
        "request": request,
        "pending_approvals": pending_approvals,
        "page": page,
        "size": size,
        "total_pages": (total_pending + size - 1) // size,  # Calculate total pages
        "user_id": request.state.user_id,
        "user_role": request.state.role
    })


@router.post("/{approval_id}/approve")
@rbac_check(entity="pending_approvals", access_type="approve")  # Highlight: Added decorator
def approval_request(request: Request, approval_id: int, db: Session = Depends(get_db)):
    return PendingApprovalService.approval_request(db, approval_id, request.state.user_id, action="approve")


@router.post("/{approval_id}/reject")
@rbac_check(entity="pending_approvals", access_type="approve")  # Highlight: Added decorator
def reject_request(request: Request, approval_id: int, db: Session = Depends(get_db)):
    return PendingApprovalService.approval_request(db, approval_id, request.state.user_id, action="reject")
