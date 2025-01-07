# src/main.py

import uvicorn
from fastapi import FastAPI, Request, APIRouter
from fastapi.staticfiles import StaticFiles
from src.app.core.database import Base, engine
from src.app.routers import base, users, items, stocks, locations, warehouses, projects, permissions, reports
from src.app.core.config import get_settings
from src.app.core.rbac import rbac_check
from starlette.responses import RedirectResponse
from src.app.core.security import decode_access_token
from src.app.routers import login

app = FastAPI()
settings = get_settings()

# # Initialize Database Tables
# Base.metadata.create_all(bind=engine)
# # Remove Base.metadata.create_all for production
# # Instead, ensure Alembic migrations are applied during deployment

# # Include Routers
# router = APIRouter(prefix="/v1")
# router.include_router(base.router, tags=["Health"])
# router.include_router(users.router, prefix="/users", tags=["Users"])
# router.include_router(items.router, prefix="/items", tags=["Items"])
# router.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
# router.include_router(locations.router, prefix="/locations", tags=["Locations"])
# router.include_router(warehouses.router, prefix="/warehouses", tags=["Warehouses"])
# router.include_router(projects.router, prefix="/projects", tags=["Projects"])
# router.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
# router.include_router(reports.router, prefix="/reports", tags=["reports"])
# app.include_router(router)

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

# Mount Static Files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
app.mount("/reports/files", StaticFiles(directory="src/assets/reports"), name="reports")
app.mount("/photos", StaticFiles(directory="src/assets/photos"), name="item_photos")


@app.middleware("http")
async def restrict_unauthenticated_access(request: Request, call_next):
    session_token = request.cookies.get("session_token")

    if not session_token:
        if not request.url.path.startswith("/login"):
            return RedirectResponse("/login", status_code=307)

    try:
        payload = decode_access_token(session_token)
        request.state.user = payload["sub"]  # Pass user info to subsequent requests
        request.state.role = payload["role"]  # Save role in request state
        request.state.user_id = payload["id"]  # Save id in request state

        # Check if the user has permission for the requested route
    except Exception as e:
        if not request.url.path.startswith("/login"):
            return RedirectResponse(url="/login", status_code=307)
    return await call_next(request)

# Include Web Router
app.include_router(login.router, tags=["Log In"])

if __name__ == "__main__":
    uvicorn.run("src.main:app", host=settings.APP_HOST, port=settings.APP_PORT)
