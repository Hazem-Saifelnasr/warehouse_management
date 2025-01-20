# src/app/schemas/stock.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StockCreate(BaseModel):
    item_id: int  # ID of the item being added or updated
    project_id: Optional[int] = None  # Project ID if stock is tied to a project
    warehouse_id: Optional[int] = None  # Warehouse ID (if applicable)
    quantity: float  # Quantity of the item

    cost_price: float
    selling_price: float
    boq_code: Optional[str] = None

    # Supplier information
    supplier_name: Optional[str] = None  # Supplier name
    supplier_code: Optional[str] = None  # Supplier-specific code
    supplier_contact: Optional[str] = None  # Supplier contact details

    # Origin information
    country_of_origin: Optional[str] = None  # Country where the item was manufactured
    import_date: Optional[datetime] = None   # Date when the item was imported
    export_date: Optional[datetime] = None   # Date when the item was exported

    # Additional information

    expiry_date: Optional[datetime] = None  # Expiration date (if applicable)
    production_date: Optional[datetime] = None  # Production date

    # Pricing and cost
    currency: Optional[str] = None  # Currency used (e.g., USD, EUR)
    discount_rate: Optional[float] = None  # Discount rate

    # Physical properties
    stock_condition: Optional[str] = None  # Condition (e.g., new, used, damaged)
    color: Optional[str] = None  # Item color
    size: Optional[str] = None  # Item size or dimensions
    weight: Optional[float] = None  # Item weight
    material: Optional[str] = None  # Material the item is made of
    barcode: Optional[str] = None  # Barcode

    # Warranty and maintenance
    warranty_period: Optional[int] = None  # Warranty period in months
    remarks: Optional[str] = None  # Additional notes or comments

    # Approval and archiving
    is_approved: Optional[bool] = False
    approval_status: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None

    # Audit fields
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None


class StockDeduct(BaseModel):
    """
    Schema for deduction a stock entry.
    """
    item_id: int  # ID of the item being deducted
    project_id: Optional[int] = None  # Project ID if stock is tied to a project
    warehouse_id: Optional[int] = None  # Warehouse ID (if applicable)
    quantity: float  # Quantity of the item

    selling_price: float
    boq_code: Optional[str] = None

    # Approval and archiving
    is_approved: Optional[bool] = False
    approval_status: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None

    # Audit fields
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None


class StockTransfer(BaseModel):
    """
    Schema for deduction a stock entry.
    """
    item_id: int  # ID of the item being deducted
    from_project_id: Optional[int] = None  # Project ID if stock is tied to a project
    to_project_id: Optional[int] = None  # Project ID if stock is tied to a project
    from_warehouse_id: Optional[int] = None  # Warehouse ID (if applicable)
    to_warehouse_id: Optional[int] = None  # Warehouse ID (if applicable)
    quantity: float  # Quantity of the item

    selling_price: float
    boq_code: Optional[str] = None

    # Approval and archiving
    is_approved: Optional[bool] = False
    approval_status: Optional[str] = None
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None

    # Audit fields
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None


class StockResponse(BaseModel):
    """
    Schema for returning stock data in API responses.
    """
    id: int  # Unique ID of the stock entry
    item_id: int  # ID of the item
    project_id: Optional[int] = None  # Project ID if stock is tied to a project
    warehouse_id: Optional[int] = None  # Warehouse ID (if applicable)

    quantity: float  # Quantity of the item
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    boq_code: Optional[str] = None

    class Config:
        from_attributes = True  # Ensures ORM compatibility for SQLAlchemy models
