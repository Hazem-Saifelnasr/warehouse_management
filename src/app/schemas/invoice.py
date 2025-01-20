# src/app/schemas/invoice.py

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class InvoiceCreate(BaseModel):
    project_id: int
    invoice_type: str

    total_cost: float
    total_price: Optional[float] = None
    profit_margin: Optional[float] = None

    created_by: int
    created_at: datetime


class InvoiceResponse(BaseModel):
    id: int
    project_id: int
    invoice_type: str

    total_cost: float


class InvoiceItemCreate(BaseModel):
    invoice_id: int
    stock_id: int

    quantity: float
    unit_price: float
    total_price: float


class InvoiceItemResponse(BaseModel):
    id: int
    invoice_id: int
    stock_id: int

    quantity: float
    unit_price: float
    total_price: float
