from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from src.app.core.security import decode_access_token
from src.app.models.permission import Permission
from sqlalchemy.orm import Session
from src.app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def rbac_check(request: Request, db: Session, token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    # Extract resource details from request
    path = request.url.path
    method = request.method.lower()

    # Check permissions for the user
    permissions = db.query(Permission).filter(Permission.user_id == user_id).all()
    for permission in permissions:
        if permission.entity in path and permission.access_type in method:
            return True

    raise HTTPException(status_code=403, detail="Access forbidden")
