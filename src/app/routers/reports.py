import pandas as pd
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.item import Item

router = APIRouter()

@router.get("/export")
def export_inventory_report(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    data = [
        {
            "Item Code": item.item_code,
            "Description": item.description,
            "Photo": item.photo,
            "Quantity": item.total_qty,
            "Location ID": item.location_id,
        }
        for item in items
    ]

    df = pd.DataFrame(data)
    file_path = "reports/inventory_report.xlsx"
    df.to_excel(file_path, index=False)
    return {"detail": f"Report generated at {file_path}"}
