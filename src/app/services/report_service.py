# src/app/routers/reports.py
import os
import re
from datetime import datetime

import pandas as pd
from fastapi import HTTPException, Depends
from sqlalchemy import func, or_, case
from sqlalchemy.orm import Session
from src.app.core.database import get_db
from src.app.models.item import Item
from src.app.models.project import Project
from src.app.models.stock import Stock
from src.app.models.warehouse import Warehouse
from src.app.models.location import Location


class ReportService:
    @staticmethod
    def list_reports():
        """
        Generate a list of reports based on files in a directory.

        Returns:
            list[dict]: List of reports with name, generated timestamp, and download URL.
        """
        base_url = "src/assets/reports/"

        reports = []
        if not os.path.exists(base_url):
            print(f"Directory {base_url} does not exist.")
            return reports

        for file_name in os.listdir(base_url):
            file_path = os.path.join(base_url, file_name)
            if os.path.isfile(file_path):
                generated_time = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat() + "Z"
                reports.append({
                    "name": file_name,
                    "generated_at": generated_time,
                    "file_name": file_name,
                })

        return reports

    @staticmethod
    def generate_report(db: Session = Depends(get_db)):
        # Generate a sample report
        ReportService.generate_stock_report(db)
        return {"message": "Report generated successfully."}

    @staticmethod
    def entity_report(entity_type: str, db: Session = Depends(get_db)):

        if entity_type not in ["item", "stock", "location", "warehouse", "project"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid entity type. Must be 'item', 'stock', 'location', 'warehouse', or 'project'.")

        # Map entity type to the respective table model
        entity_model_map = {
            "item": Item,
            "stock": Stock,
            "location": Location,
            "warehouse": Warehouse,
            "project": Project,
        }

        # Get the appropriate model for the entity type
        model = entity_model_map[entity_type]

        # Retrieve column names dynamically
        column_names = [column.name for column in model.__table__.columns]

        # Query all rows from the table
        query = db.query(model).all()

        # Format the data dynamically based on column names
        data = [
            {column: getattr(row, column) for column in column_names}
            for row in query
        ]

        # Sanitize location name for the file path
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', entity_type)

        df = pd.DataFrame(data)
        file_path = f"src/assets/reports/{sanitized_name}s_report.xlsx"
        df.to_excel(file_path, index=False)
        return {"detail": f"Report generated at {file_path}", "data": data}

    @staticmethod
    def get_stock_by_item(item_id: int, db: Session = Depends(get_db)):
        """
        Get stock summary for a specific item across all locations, warehouses, and projects.
        """
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        stocks = db.query(
            func.coalesce(Warehouse.name, "N/A").label("warehouse"),
            func.coalesce(Project.project_name, "N/A").label("project"),
            func.sum(Stock.quantity).label("total_quantity")
        ).outerjoin(Warehouse, Stock.warehouse_id == Warehouse.id).outerjoin(
            Project, Stock.project_id == Project.id).filter(
            Stock.item_id == item_id).group_by(Warehouse.name, Project.project_name).all()

        data = [
            {
                "Warehouse": stock.warehouse,
                "Project": stock.project,
                "Total Quantity": stock.total_quantity,
            }
            for stock in stocks
        ]

        # Sanitize location name for the file path
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', item.item_code)

        df = pd.DataFrame(data)
        file_path = f"src/assets/reports/item_{sanitized_name}_stock_report.xlsx"
        df.to_excel(file_path, index=False)
        return {
            "detail": f"Report generated at {file_path}",
            "data": {
                "item": {
                    "item_code": item.item_code,
                    "description": item.description,
                    "unit_of_measure": item.unit_of_measure},
                "stocks": data
            }
        }

    @staticmethod
    def get_stock_by_entity_type(entity_type: str, db: Session = Depends(get_db)):
        """
        Get stock summary for a specific entity type (location, warehouse, or project).

        Args:
            entity_type (str): The type of entity ("location", "warehouse", "project").
            db (Session): The database session.

        Returns:
            dict: Stock summary grouped by entity type.
        """
        if entity_type not in ["location", "warehouse", "project"]:
            raise HTTPException(status_code=400, detail="Invalid entity type.")

        query = db.query(
            Item.item_code,
            Item.description,
            Item.unit_of_measure,
            func.sum(Stock.quantity).label("total_quantity"),
            case(
                (Stock.warehouse_id.isnot(None), "Warehouse"),
                (Stock.project_id.isnot(None), "Project"),
                else_="Unknown",
            ).label("entity_type"),
            case(
                (Stock.warehouse_id.isnot(None), Warehouse.name),
                (Stock.project_id.isnot(None), Project.project_name),
                else_="Unknown",
            ).label("entity_name"),
        ).join(Stock, Stock.item_id == Item.id, isouter=True
               ).join(Warehouse, Stock.warehouse_id == Warehouse.id, isouter=True
                      ).join(Project, Stock.project_id == Project.id, isouter=True)

        if entity_type == "location":
            query = query.filter(
                or_(
                    Warehouse.location_id.isnot(None),
                    Project.location_id.isnot(None)
                )
            )
        elif entity_type == "warehouse":
            query = query.filter(Stock.warehouse_id.isnot(None))
        elif entity_type == "project":
            query = query.filter(Stock.project_id.isnot(None))

        query = query.group_by(
            Item.item_code, Item.description, Item.unit_of_measure, Warehouse.name, Project.project_name,
            Stock.warehouse_id, Stock.project_id
        )

        stocks = query.all()

        if not stocks:
            raise HTTPException(status_code=404, detail="No stock found for the specified entity type.")

        # Prepare response data
        data = [
            {
                "Item Code": stock.item_code,
                "Description": stock.description,
                "Unit of Measure": stock.unit_of_measure,
                "Total Quantity": stock.total_quantity,
                "Entity Type": stock.entity_type,
                "Entity Name": stock.entity_name
            }
            for stock in stocks
        ]

        # Sanitize location name for the file path
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', entity_type)

        # Save report to Excel
        file_path = f"src/assets/reports/{sanitized_name}s_stock_report.xlsx"
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)

        return {"detail": f"Report generated at {file_path}", "data": data}

    @staticmethod
    def get_stock_by_entity_and_id(entity_type: str, entity_id: int, db: Session = Depends(get_db)):
        """
        Get stock for a specific entity type and entity ID.

        Args:
            entity_type (str): The type of entity ("location", "warehouse", "project").
            entity_id (int): The ID of the entity.
            db (Session): The database session.

        Returns:
            dict: Stock details grouped by item.
        """
        if entity_type not in ["location", "warehouse", "project"]:
            raise HTTPException(status_code=400, detail="Invalid entity type.")

        entity_name = ""

        query = db.query(Stock)
        item = db.query(Item)

        if entity_type == "location":
            # Combine results from both sources
            query = query.filter(
                or_(
                    Stock.warehouse_id.in_(
                        db.query(Warehouse.id).filter(Warehouse.location_id == entity_id)
                    ),
                    Stock.project_id.in_(
                        db.query(Project.id).filter(Project.location_id == entity_id)
                    )
                )
            )
            entity_name = db.query(Location).filter(Location.id == entity_id).first().name
        elif entity_type == "warehouse":
            query = query.filter(Stock.warehouse_id == entity_id)
            entity_name = db.query(Warehouse).filter(Warehouse.id == entity_id).first().name
        elif entity_type == "project":
            query = query.filter(Stock.project_id == entity_id)
            entity_name = db.query(Project).filter(Project.id == entity_id).first().project_name
        stocks = query.all()

        if not stocks:
            raise HTTPException(status_code=404, detail="No stock found for the specified entity.")

        data = [
            {
                "Item Code": item.filter(Item.id == stock.item_id).first().item_code,
                "Description": item.filter(Item.id == stock.item_id).first().description,
                "Quantity": stock.quantity,
                "Location": db.query(Warehouse.name if stock.warehouse_id else Project.project_name)
                .filter(
                    Warehouse.id == stock.warehouse_id if stock.warehouse_id else Project.id == stock.project_id
                )
                .scalar(),
            }
            for stock in stocks
        ]

        # Sanitize location name for the file path
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '_', entity_name)

        # Generate the report
        df = pd.DataFrame(data)
        file_path = f"src/assets/reports/{sanitized_name}_stock_report.xlsx"
        df.to_excel(file_path, index=False)
        return {"detail": f"Report generated at {file_path}", "data": data}

    @staticmethod
    def generate_stock_report(db: Session):
        stocks = db.query(Stock).all()
        data = [
            {
                "Item ID": stock.item_id,
                "Quantity": stock.quantity,
                "Warehouse": stock.warehouse_id,
                "Project": stock.project_id,
            }
            for stock in stocks
        ]
        df = pd.DataFrame(data)
        file_path = "src/assets/reports/Stock_Report.xlsx"
        df.to_excel(file_path, index=False)

    @staticmethod
    def delete_report(data: dict):
        # Parse the file path from the path
        file_path = f"src/assets/reports/{os.path.basename(data["file_name"])}"

        # Check if the file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Report not found")

        # Delete the file
        try:
            os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

        return {"detail": "Report deleted successfully"}
