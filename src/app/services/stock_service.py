# src/app/services/stock_service.py

from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from src.app.core.database import get_db
from src.app.models.item import Item
from src.app.models.location import Location
from src.app.models.project import Project
from src.app.models.stock import Stock
from src.app.models.warehouse import Warehouse
from src.app.schemas.stock import StockCreate, StockDeduct, StockTransfer
from src.app.services.history_log_service import HistoryLogService


class StockService:
    @staticmethod
    def validate_references(db: Session, item_id: int = None, warehouse_id: int = None, project_id: int = None,
                            location_id: int = None):
        # Validate item existence
        if not db.query(Item).filter(Item.id == item_id).first():
            raise HTTPException(status_code=404, detail="Item not found")

        # Validate warehouse, project, or location existence
        if warehouse_id and not db.query(Warehouse).filter(Warehouse.id == warehouse_id).first():
            raise HTTPException(status_code=404, detail="Warehouse not found")
        if project_id and not db.query(Project).filter(Project.id == project_id).first():
            raise HTTPException(status_code=404, detail="Project not found")
        if location_id and not db.query(Location).filter(Location.id == location_id).first():
            raise HTTPException(status_code=404, detail="Location not found")

    @staticmethod
    def add_stock(stock_data: StockCreate, requester_id: int, db: Session = Depends(get_db)):
        StockService.validate_references(db, stock_data.item_id, stock_data.warehouse_id, stock_data.project_id)

        # Validate input
        if stock_data.project_id and stock_data.warehouse_id:
            raise HTTPException(status_code=400, detail="Specify either project_id or warehouse_id, not both.")
        if not stock_data.quantity or stock_data.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")
        if not (stock_data.project_id or stock_data.warehouse_id):
            raise HTTPException(status_code=400, detail="Specify either project_id or warehouse_id.")

        # Check if stock already exists
        stock = db.query(Stock).filter(
            Stock.item_id == stock_data.item_id,
            Stock.project_id == stock_data.project_id,
            Stock.warehouse_id == stock_data.warehouse_id,
        ).first()

        metadata = {
            "item_id": stock_data.item_id,
            "previous_qty": stock.quantity if stock else 0,
            "added_qty": stock_data.quantity,
            "project_id":  getattr(stock_data, "project_id", "N/A"),
            "warehouse_id": getattr(stock_data, "warehouse_id", "N/A")
        }

        if stock:
            # Update cost_price using weighted average
            stock.cost_price = ((stock.quantity * stock.cost_price) +
                                (stock_data.quantity * stock_data.cost_price)) / (stock.quantity + stock_data.quantity)

            # Update selling price directly if it differs
            if stock_data.selling_price is not None:
                stock.selling_price = stock_data.selling_price

            # Update stock quantity
            stock.quantity += stock_data.quantity

            HistoryLogService.log_action(db, "stock", stock.item_id, "add", requester_id, metadata)
            return stock
        else:
            new_stock = Stock(**dict(stock_data))
            db.add(new_stock)

            db.commit()
            HistoryLogService.log_action(db, "stock", new_stock.item_id, "add", requester_id, metadata)
            return new_stock

    @staticmethod
    def deduct_stock(stock_data: StockDeduct, requester_id: int, db: Session = Depends(get_db)):
        StockService.validate_references(db, stock_data.item_id, stock_data.warehouse_id, stock_data.project_id)
        # Validate input
        if stock_data.project_id and stock_data.warehouse_id:
            raise HTTPException(status_code=400, detail="Specify either project_id or warehouse_id, not both.")
        if not (stock_data.project_id or stock_data.warehouse_id):
            raise HTTPException(status_code=400, detail="Specify either project_id or warehouse_id.")
        if stock_data.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")

        # Aggregate stock across all entries for the given project or warehouse
        stock_query = db.query(Stock).filter(
            Stock.item_id == stock_data.item_id,
            Stock.project_id == stock_data.project_id,
            Stock.warehouse_id == stock_data.warehouse_id,
        )

        total_stock = stock_query.with_entities(func.sum(Stock.quantity)).scalar() or 0

        if total_stock < stock_data.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock.")

        # Deduct stock from entries in order
        stocks = stock_query.order_by(Stock.updated_at).all()
        remaining_quantity = stock_data.quantity
        updated_stocks = []

        for stock in stocks:
            if stock.quantity >= remaining_quantity:
                stock.quantity -= remaining_quantity
                if stock.quantity == 0:
                    db.delete(stock)
                else:
                    updated_stocks.append(stock)
                break
            else:
                remaining_quantity -= stock.quantity
                db.delete(stock)

        db.commit()

        metadata = {
            "item_id": stock_data.item_id,
            "previous_qty": stock_query.first().quantity,
            "deducted_qty": stock_data.quantity,
            "project_id": getattr(stock_data, "project_id", "N/A"),
            "warehouse_id": getattr(stock_data, "warehouse_id", "N/A")
        }

        HistoryLogService.log_action(db, "stock", stock_data.item_id, "deduct", requester_id, metadata)
        return updated_stocks

    @staticmethod
    def transfer_stock(stock_data: StockTransfer, requester_id: int, db: Session = Depends(get_db)):
        StockService.validate_references(db, stock_data.item_id, stock_data.from_warehouse_id, stock_data.from_project_id)
        StockService.validate_references(db, stock_data.item_id, stock_data.to_warehouse_id, stock_data.to_project_id)

        if not stock_data.quantity or stock_data.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")

        # Validate source
        if not (stock_data.from_project_id or stock_data.from_warehouse_id):
            raise HTTPException(status_code=400, detail="A source (location, project, or warehouse) must be specified.")

        # Validate destination
        if not (stock_data.to_project_id or stock_data.to_warehouse_id):
            raise HTTPException(status_code=400,
                                detail="A destination (location, project, or warehouse) must be specified.")

        # Check if stock already exists
        stock = db.query(Stock).filter(
            Stock.item_id == stock_data.item_id,
            Stock.project_id == stock_data.from_project_id,
            Stock.warehouse_id == stock_data.from_warehouse_id,
        ).first()

        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")

        if stock_data.from_project_id:
            stock_dict = stock_data.model_dump()
            stock_dict["project_id"] = stock_data.from_project_id
            stock_dict["warehouse_id"] = None
            del stock_dict["from_project_id"]  # Remove the field dynamically
            del stock_dict["from_warehouse_id"]  # Remove the field dynamically
            stock_data_deduct = StockDeduct(**stock_dict)
        else:
            stock_dict = stock_data.model_dump()
            stock_dict["warehouse_id"] = stock_data.from_warehouse_id
            stock_dict["project_id"] = None
            del stock_dict["from_project_id"]  # Remove the field dynamically
            del stock_dict["from_warehouse_id"]  # Remove the field dynamically
            stock_data_deduct = StockDeduct(**stock_dict)

        if stock_data.to_project_id:
            stock_dict = stock_data.model_dump()
            stock_dict["project_id"] = stock_data.to_project_id
            stock_dict["warehouse_id"] = None
            stock_dict["cost_price"] = stock.cost_price
            del stock_dict["from_project_id"]  # Remove the field dynamically
            del stock_dict["from_warehouse_id"]  # Remove the field dynamically
            stock_data_add = StockCreate(**stock_dict)
        else:
            stock_dict = stock_data.model_dump()
            stock_dict["warehouse_id"] = stock_data.to_warehouse_id
            stock_dict["project_id"] = None
            stock_dict["cost_price"] = stock.cost_price
            del stock_dict["from_project_id"]  # Remove the field dynamically
            del stock_dict["from_warehouse_id"]  # Remove the field dynamically
            stock_data_add = StockCreate(**stock_dict)

        # Remove stock from the source
        StockService.deduct_stock(stock_data_deduct, requester_id, db)

        # Add stock to the destination
        added_stock = StockService.add_stock(stock_data_add, requester_id, db)

        metadata = {
            "item_id": stock.item_id,
            "previous_qty": stock.quantity,
            "added_qty": stock_data.quantity,
            "from_project_id": getattr(stock_data_deduct, "project_id", "N/A"),
            "from_warehouse_id": getattr(stock_data_deduct, "warehouse_id", "N/A"),
            "to_project_id": getattr(stock_data_add, "project_id", "N/A"),
            "to_warehouse_id": getattr(stock_data_add, "warehouse_id", "N/A"),
        }

        HistoryLogService.log_action(db, "stock", stock_data.item_id, "transfer", requester_id, metadata)
        return added_stock

    @staticmethod
    def get_stock_by_location_or_project_or_warehouse(
        db: Session,
        location_id: int = None,
        project_id: int = None,
        warehouse_id: int = None
    ):
        """
        Fetch stock by location, project, or warehouse.

        Args:
            db (Session): The database session.
            location_id (int): The location ID (optional).
            project_id (int): The project ID (optional).
            warehouse_id (int): The warehouse ID (optional).

        Returns:
            List[Stock]: List of stock entries filtered by the criteria.
        """
        query = db.query(Stock)

        if location_id:
            # Combine results from both sources
            query = query.filter(
                or_(
                    Stock.warehouse_id.in_(
                        db.query(Warehouse.id).filter(Warehouse.location_id == location_id)
                    ),
                    Stock.project_id.in_(
                        db.query(Project.id).filter(Project.location_id == location_id)
                    )
                )
            )

        elif project_id:
            query = query.filter(Stock.project_id == project_id)
        elif warehouse_id:
            query = query.filter(Stock.warehouse_id == warehouse_id)

        return query.all()

    @staticmethod
    def get_stock_of_item_by_location_or_project_or_warehouse(
        db: Session,
        item_id: int,
        location_id: int = None,
        project_id: int = None,
        warehouse_id: int = None
    ):
        """
        Fetch the stock of a specific item filtered by location, project, or warehouse.

        Args:
            db (Session): The database session.
            item_id (int): The ID of the item.
            location_id (int): The location ID (optional).
            project_id (int): The project ID (optional).
            warehouse_id (int): The warehouse ID (optional).

        Returns:
            Stock: The stock entry for the specified item and criteria.
        """
        StockService.validate_references(db, item_id, warehouse_id, project_id, location_id)

        query = db.query(Stock).filter(Stock.item_id == item_id)

        if location_id:
            # Combine results from both sources
            query = query.filter(
                or_(
                    Stock.warehouse_id.in_(
                        db.query(Warehouse.id).filter(Warehouse.location_id == location_id)
                    ),
                    Stock.project_id.in_(
                        db.query(Project.id).filter(Project.location_id == location_id)
                    )
                )
            )
        elif project_id:
            query = query.filter(Stock.project_id == project_id)
        elif warehouse_id:
            query = query.filter(Stock.warehouse_id == warehouse_id)

        stock = query.all()

        if not stock:
            raise HTTPException(status_code=404, detail="No stock found for the specified criteria")

        return stock

    @staticmethod
    def get_item_location_and_qty(
        db: Session,
        item_id: int
    ):
        """
        Fetch all locations and quantities of a specific item across warehouses and projects.

        Args:
            db (Session): The database session.
            item_id (int): The ID of the item.

        Returns:
            List[Dict]: List of dictionaries containing location, warehouse/project, and quantity.
        """
        # Validate the item exists
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # Query stocks for warehouses and projects
        warehouse_data = (
            db.query(
                Location.name.label("location"),
                Warehouse.name.label("warehouse"),
                Stock.quantity.label("quantity")
            )
            .join(Warehouse, Stock.warehouse_id == Warehouse.id)
            .join(Location, Warehouse.location_id == Location.id)
            .filter(Stock.item_id == item_id)
            .all()
        )

        project_data = (
            db.query(
                Location.name.label("location"),
                Project.name.label("project"),
                Stock.quantity.label("quantity")
            )
            .join(Project, Stock.project_id == Project.id)
            .join(Location, Project.location_id == Location.id)
            .filter(Stock.item_id == item_id)
            .all()
        )

        # Combine results
        results = []
        for data in warehouse_data:
            results.append({
                "location": data.location,
                "type": "warehouse",
                "name": data.warehouse,
                "quantity": data.quantity
            })

        for data in project_data:
            results.append({
                "location": data.location,
                "type": "project",
                "name": data.project,
                "quantity": data.quantity
            })

        return results

    @staticmethod
    def get_total_stock_by_item(db: Session, item_id: int):
        StockService.validate_references(db, item_id)
        item = db.query(Item).filter(Item.id == item_id).first()
        return {
            "item_code": item.item_code,
            "item_description": item.description,
            "total_quantity": db.query(func.sum(Stock.quantity)).filter(Stock.item_id == item_id).scalar(),
            "unit_of_measure": item.unit_of_measure
        }
