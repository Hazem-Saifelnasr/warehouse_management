# src/app/routers/base.py

from fastapi import APIRouter, Depends
from src.app.core.config import get_settings, Settings

router = APIRouter()


@router.get("/")
def health_check(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "status": "ok",
        "message": "server is running"
    }
