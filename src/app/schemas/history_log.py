# src/app/schemas/history_log.py

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Text


class HistoryLogCreate(BaseModel):
    id: int
    entity: str
    entity_id: Optional[int] = None
    entity_metadata: dict
    action: int
    details: Optional[Text] = None
    timestamp: Optional[datetime] = None

    requested_by: Optional[int] = None
    request_at: Optional[datetime] = None

    approved_by: Optional[int] = None
    approval_date: Optional[datetime] = None


class HistoryLogResponse(BaseModel):
    id: int
    entity: str
    entity_id: Optional[int] = None
    entity_metadata: dict
    action: int
    details: Optional[Text] = None
    timestamp: Optional[datetime] = None

    requested_by: Optional[int] = None
    request_at: Optional[datetime] = None

    approved_by: Optional[int] = None
    approval_date: Optional[datetime] = None
