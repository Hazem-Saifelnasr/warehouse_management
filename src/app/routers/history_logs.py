# src/app/routers/history_logs.py

from fastapi import APIRouter, Request, Depends
from sqlalchemy import case, String, cast, func
from sqlalchemy.orm import Session, aliased
from src.app.core.database import get_db
from src.app.core.rbac import rbac_check
from src.app.models import HistoryLog, Item, Project, Warehouse, Location, User, Department, Invoice
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")


@router.get("/", response_class=HTMLResponse)
@rbac_check(entity="history_logs", access_type="manage")  # Highlight: Added decorator
def history_logs_page(request: Request, db: Session = Depends(get_db), page: int = 1, size: int = 10):
    """
    List all locations with pagination.
    """
    total_logs = db.query(HistoryLog).count()  # Total number of logs
    offset = (page - 1) * size

    # Create aliases for the User model
    Requester = aliased(User)
    Approver = aliased(User)

    # Query history logs with resolved entity and usernames
    history_logs_query = (db.query(
        HistoryLog.id,
        HistoryLog.entity,
        HistoryLog.entity_metadata,
        HistoryLog.action,
        HistoryLog.details,
        HistoryLog.request_at,
        HistoryLog.approval_at,
        HistoryLog.entity_id,
        Requester.username.label("requester_name"),  # Use requester relationship
        Approver.username.label("approver_name"),  # Use approver relationship
        case((
            HistoryLog.entity == "item",
            func.coalesce(Item.item_code, HistoryLog.entity_metadata['item_code'].astext)),
            (HistoryLog.entity == "user", func.coalesce(User.username, HistoryLog.entity_metadata['username'].astext)),
            (HistoryLog.entity == "project", func.coalesce(Project.name, HistoryLog.entity_metadata['name'].astext)),
            (HistoryLog.entity == "warehouse",
             func.coalesce(Warehouse.name, HistoryLog.entity_metadata['name'].astext)),
            (HistoryLog.entity == "location", func.coalesce(Location.name, HistoryLog.entity_metadata['name'].astext)),
            (HistoryLog.entity == "department",
             func.coalesce(Department.name, HistoryLog.entity_metadata['name'].astext)),
            (HistoryLog.entity == "invoice",
             func.coalesce(Invoice.number, HistoryLog.entity_metadata['number'].astext)),
            else_=cast(HistoryLog.entity_id, String),
        ).label("entity_display_name")  # Dynamically resolve entity name
    )
          .distinct(HistoryLog.id)  # Ensure unique HistoryLog.id entries
          .outerjoin(Requester, HistoryLog.requested_by == Requester.id)  # Resolve requester
          .outerjoin(Approver, HistoryLog.approved_by == Approver.id)  # Resolve approver
          .outerjoin(Item, (HistoryLog.entity == "item") & (HistoryLog.entity_id == Item.id))
          .outerjoin(Project, (HistoryLog.entity == "project") & (HistoryLog.entity_id == Project.id))
          .outerjoin(Warehouse,
                     (HistoryLog.entity == "warehouse") & (HistoryLog.entity_id == Warehouse.id))
          .outerjoin(Location,
                     (HistoryLog.entity == "location") & (HistoryLog.entity_id == Location.id))
          .outerjoin(Department,
                     (HistoryLog.entity == "department") & (HistoryLog.entity_id == Department.id))
          .outerjoin(Invoice, (HistoryLog.entity == "invoice") & (HistoryLog.entity_id == Invoice.id))
          .offset(offset)
          .limit(size))

    history_logs = history_logs_query.all()

    return templates.TemplateResponse("history_logs.html", {
        "request": request,
        "history_logs": history_logs,
        "page": page,
        "size": size,
        "total_pages": (total_logs + size - 1) // size,  # Calculate total pages
        "user_id": request.state.user_id,
        "user_role": request.state.role
    })
