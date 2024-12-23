import uvicorn
from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import base, users, items, locations, warehouses, projects, permissions, reports

app = FastAPI()

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

# Include Routers
app.include_router(base.router, tags=["Health"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(locations.router, prefix="/locations", tags=["Locations"])
app.include_router(warehouses.router, prefix="/warehouses", tags=["Warehouses"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="localhost", port=8000, reload=True, log_level="debug")
