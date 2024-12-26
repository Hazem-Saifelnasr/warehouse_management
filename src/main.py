# src/main.py

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.database import Base, engine
from app.routers import base, users, items, stocks, locations, warehouses, projects, permissions, reports
from src.app.core.config import get_settings

app = FastAPI()

# Initialize Database Tables
Base.metadata.create_all(bind=engine)
# Remove Base.metadata.create_all for production
# Instead, ensure Alembic migrations are applied during deployment

# Include Routers
app.include_router(base.router, tags=["Health"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
app.include_router(locations.router, prefix="/locations", tags=["Locations"])
app.include_router(warehouses.router, prefix="/warehouses", tags=["Warehouses"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])

app.mount("/photos", StaticFiles(directory="src/assets/photos"), name="photos")
app.mount("/web", StaticFiles(directory="src/assets/templates"), name="web")

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run("src.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True, log_level="debug")
