# src/app/model/associations.py

from sqlalchemy import Table, Column, Integer, ForeignKey
from src.app.core.database import Base

# Association Table for Warehouse and Items
warehouse_items = Table(
    'warehouse_items',
    Base.metadata,
    Column('warehouse_id', Integer, ForeignKey('warehouses.id'), primary_key=True),
    Column('item_id', Integer, ForeignKey('items.id'), primary_key=True)
)


# Association Table for Projects and Items
project_items = Table(
    'project_items',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('item_id', Integer, ForeignKey('items.id'), primary_key=True)
)