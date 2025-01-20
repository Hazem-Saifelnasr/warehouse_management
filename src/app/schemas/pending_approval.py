# src/app/schemas/pending_approval.py

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Text


class PendingApprovalCreate(BaseModel):
    entity: str
    entity_id: Optional[int] = None
    action: str
    new_value: dict
    requested_by: int
    requested_at: datetime

    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_status: str


class PendingApprovalResponse(BaseModel):
    id: int
    entity: str
    entity_id: Optional[int] = None
    action: str
    new_value: dict
    requested_by: int

