# src/app/services/stock_service.py

from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.app.models.item import Item
from src.app.models.location import Location
from src.app.models.project import Project
from src.app.models.stock import Stock
from src.app.models.warehouse import Warehouse


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
    def add_stock(db: Session, item_id: int, project_id: int = None, warehouse_id: int = None,
                  quantity: float = 0, ):
        """
        Add stock for an item in a specific project or warehouse.

        Args:
            db (Session): The database session.
            item_id (int): The ID of the item.
            project_id (int): The project ID (optional).
            warehouse_id (int): The warehouse ID (optional).
            quantity (float): The quantity to add.

        Returns:
            Stock: The updated or new stock entry.

        Raises:
            HTTPException: If both or neither of project_id and warehouse_id are provided, or if quantity is invalid.
        """
        StockService.validate_references(db, item_id, warehouse_id, project_id)

        # Validate input
        if project_id and warehouse_id:
            raise HTTPException(status_code=400, detail="Specify either project_id or warehouse_id, not both.")
        if not quantity or quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")
        if not (project_id or warehouse_id):
            raise HTTPException(status_code=400, detail="Specify either project_id or warehouse_id.")

        # Check if stock already exists
        stock = db.query(Stock).filter(
            Stock.item_id == item_id,
            Stock.project_id == project_id,
            Stock.warehouse_id == warehouse_id,
        ).first()

        if stock:
            stock.quantity += quantity
        else:
            stock = Stock(
                item_id=item_id,
                project_id=project_id,
                warehouse_id=warehouse_id,
                quantity=quantity,
            )
            db.add(stock)

        db.commit()
        return stock

    @staticmethod
    def deduct_stock(db: Session, item_id: int, project_id: int = None,
                     warehouse_id: int = None, quantity: float = 0,):
        """
        Deduct stock quantity for a specific item in a project or warehouse.

        Args:
            db (Session): The database session.
            item_id (int): The ID of the item.
            project_id (int): The project ID (optional).
            warehouse_id (int): The warehouse ID (optional).
            quantity (float): The quantity to deduct.

        Returns:
            Stock: The updated stock entry.

        Raises:
            HTTPException: If stock is insufficient or entry not found.
        """
        StockService.validate_references(db, item_id, warehouse_id, project_id)
        # Validate input
        if project_id and warehouse_id:
            raise HTTPException(status_code=400, detail="Specify either project_id or warehouse_id, not both.")
        if not (project_id or warehouse_id):
            raise HTTPException(status_code=400, detail="Specify either project_id or warehouse_id.")
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")

        # Aggregate stock across all entries for the given project or warehouse
        stock_query = db.query(Stock).filter(
            Stock.item_id == item_id,
            Stock.project_id == project_id,
            Stock.warehouse_id == warehouse_id,
        )

        total_stock = stock_query.with_entities(func.sum(Stock.quantity)).scalar() or 0

        if total_stock < quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock.")

        # Deduct stock from entries in order
        stocks = stock_query.order_by(Stock.last_updated).all()
        remaining_quantity = quantity
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

        return updated_stocks

    @staticmethod
    def transfer_stock(db: Session, item_id: int,
                       from_project_id: int = None, to_project_id: int = None,
                       from_warehouse_id: int = None, to_warehouse_id: int = None,
                       quantity: float = 0):
        """
        Transfers stock of an item from a source to a destination.

        Args:
            db (Session): Database session.
            item_id (int): ID of the item to transfer.
            from_project_id (int): Source project ID.
            to_project_id (int): Destination project ID.
            from_warehouse_id (int): Source warehouse ID.
            to_warehouse_id (int): Destination warehouse ID.
            quantity (float): Quantity to transfer.
        """
        StockService.validate_references(db, item_id, from_warehouse_id, from_project_id)
        StockService.validate_references(db, item_id, to_warehouse_id, to_project_id)

        if not quantity or quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")

        # Validate source
        if not (from_project_id or from_warehouse_id):
            raise HTTPException(status_code=400, detail="A source (location, project, or warehouse) must be specified.")

        # Validate destination
        if not (to_project_id or to_warehouse_id):
            raise HTTPException(status_code=400,
                                detail="A destination (location, project, or warehouse) must be specified.")

        # Remove stock from the source
        StockService.deduct_stock(db, item_id=item_id,
                                  project_id=from_project_id,
                                  warehouse_id=from_warehouse_id,
                                  quantity=quantity)

        # Add stock to the destination
        return StockService.add_stock(db, item_id=item_id,
                                      project_id=to_project_id,
                                      warehouse_id=to_warehouse_id,
                                      quantity=quantity)

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
                Project.project_name.label("project"),
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
