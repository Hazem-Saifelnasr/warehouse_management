# src/app/core/rbac.py

from fastapi import HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from src.app.core.security import decode_access_token
from src.app.models.user import User
from src.app.models.permission import Permission
from sqlalchemy.orm import Session
from functools import lru_cache
from src.app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


#  Role-Based Access Control (RBAC)
async def rbac_check(request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        # Decode the user ID from the token
        payload = decode_access_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token: missing username")

        # Query the database for the user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # Retrieve user ID from the database
        user_id = user.id

        # Extract resource details from request
        path = request.url.path.strip("/").split("/")  # Split the path into segments
        entity = path[0] if len(path) > 0 else "*"  # First segment is the entity
        entity_id = path[1] if len(path) > 1 and path[1].isdigit() else "*"  # Second is the ID
        method = request.method.lower()  # HTTP method (e.g., GET -> read)

        # Use has_permission to check access
        if not has_permission(db, user_id, entity, entity_id, method):
            raise HTTPException(status_code=403, detail="Permission denied")

    except ValueError as e:
        raise HTTPException(status_code=401, detail="Could not validate token") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@lru_cache
def get_permissions_for_user(user_id: int, db: Session):
    """
    Cache user permissions to improve performance in high-traffic environments.
    """
    return db.query(Permission).filter(Permission.user_id == user_id).all()


def has_permission(db: Session, user_id: int, entity: str, entity_id: str, access_type: str) -> bool:
    # Query the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Admins have all permissions
    if user.role == "admin":
        return True

    # Query permissions for the user
    permissions = get_permissions_for_user(user_id, db)
    for permission in permissions:
        # Check if permission matches exactly or with wildcards
        if (permission.entity in {entity, "*"} and
            permission.entity_id in {str(entity_id), "*"} and
                (permission.access_type == "*" or access_type in permission.access_type.split(","))):
            return True

    # Raise exception if no matching permission found
    return False
