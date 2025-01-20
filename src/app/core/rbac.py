# src/app/core/rbac.py

from fastapi import HTTPException, Request
from functools import wraps
from fastapi.security import OAuth2PasswordBearer
from src.app.models.user import User
from src.app.models.permission import Permission
from sqlalchemy.orm import Session
from functools import lru_cache

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


method_map = {
    "read": {"get"},
    "write": {"post", "put", "patch"},
    "delete": {"delete"},
    "create": {"post"},
    "manage": {"get", "post", "put", "patch", "delete"},
    "assign": {"post", "put"},
    "export": {"get"},
    "approve": {"post", "put"},
    "revoke": {"post", "put"},
    "archive": {"post", "put"},
    "restore": {"post", "put"},
    "share": {"post", "put"},
    "execute": {"post", "put", "patch"},
    "*": {"get", "post", "put", "patch", "delete"},
}

# def rbac_check(entity: str, access_type: str):
#     def decorator(request: Request, db: Session = Depends(get_db)):
#         user = request.state.user  # Extract user details from middleware
#         if user.get("role") == "admin":
#             return  # Admins have all permissions
#
#         user_id = user.get("id")
#         permissions = db.query(Permission).filter(Permission.user_id == user_id).all()
#
#         # Check if user has the required permissions
#         for permission in permissions:
#             if (permission.entity == entity or permission.entity == "*") and \
#                (permission.access_type == access_type or permission.access_type == "*"):
#                 return
#
#         # If no matching permission is found
#         raise HTTPException(status_code=403, detail="Permission denied")
#
#     return decorator
# # Example of uses
# @router.get("/items", dependencies=[Depends(rbac_check("item", "read"))])
# async def list_items():
#     return {"message": "Items listed"}
#
# @router.post("/items", dependencies=[Depends(rbac_check("item", "write"))])
# async def create_item():
#     return {"message": "Item created"}
#
# @router.delete("/items/{item_id}", dependencies=[Depends(rbac_check("item", "delete"))])
# async def delete_item(item_id: int):
#     return {"message": f"Item {item_id} deleted"}


def rbac_check(entity: str, access_type: str):
    """
    Decorator for Role-Based Access Control (RBAC) checks.

    Args:
        entity (str): The entity type (e.g., "item", "stock").
        access_type (str): The access type (e.g., "read", "write", "delete").

    Returns:
        Callable: Decorator function.
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            check_permissions(*args, **kwargs)  # Call permissions check
            return await func(*args, **kwargs)  # Await the wrapped async function

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            check_permissions(*args, **kwargs)  # Call permissions check
            return func(*args, **kwargs)  # Call the wrapped sync function

        # Return the appropriate wrapper based on whether the function is async
        if callable(func) and hasattr(func, "__code__") and func.__code__.co_flags & 0x080:
            return async_wrapper
        return sync_wrapper

    def check_permissions(*args, **kwargs):
        # Extract `request` and `db` from args or kwargs
        request: Request = kwargs.get("request") or next(
            (arg for arg in args if isinstance(arg, Request)), None
        )
        db: Session = kwargs.get("db") or next(
            (arg for arg in args if isinstance(arg, Session)), None
        )

        if not request or not db:
            raise HTTPException(status_code=500, detail="Invalid decorator usage")

        # Check if the user is authenticated
        user = getattr(request.state, "user", None)
        role = getattr(request.state, "role", None)
        user_id = getattr(request.state, "user_id", None)

        if not user or not role or not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Check if the user is an admin
        if role == "admin":
            return

        # Extract resource details from request
        path = request.url.path.strip("/").split("/")  # Split the path into segments
        entity = path[0] if len(path) > 0 else "*"  # First segment is the entity
        entity_id = path[1] if len(path) > 1 and path[1].isdigit() else "*"  # Second is the ID
        method = request.method.lower()  # HTTP method (e.g., GET -> read)

        # Use has_permission to check access
        if has_permission(db, user_id, entity, entity_id, method):
            return  # Valid permission found

        # If no valid permission is found
        raise HTTPException(status_code=403, detail="Permission denied")
    return decorator
# # Example of use
# @rbac_check(entity="item", access_type="read")


# #  Role-Based Access Control (RBAC)
# async def rbac_check(request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
#     try:
#         # Decode the user ID from the token
#         payload = decode_access_token(token)
#         username = payload.get("sub")
#         if not username:
#             raise HTTPException(status_code=401, detail="Invalid token: missing username")
#
#         # Query the database for the user
#         user = db.query(User).filter(User.username == username).first()
#         if not user:
#             raise HTTPException(status_code=401, detail="User not found")
#
#         # Retrieve user ID from the database
#         user_id = user.id
#
#         # Extract resource details from request
#         path = request.url.path.strip("/").split("/")  # Split the path into segments
#         entity = path[0] if len(path) > 0 else "*"  # First segment is the entity
#         entity_id = path[1] if len(path) > 1 and path[1].isdigit() else "*"  # Second is the ID
#         method = request.method.lower()  # HTTP method (e.g., GET -> read)
#
#         # Use has_permission to check access
#         if not has_permission(db, user_id, entity, entity_id, method):
#             raise HTTPException(status_code=403, detail="Permission denied")
#
#     except ValueError as e:
#         raise HTTPException(status_code=401, detail="Could not validate token") from e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal server error")


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
        if (
                (permission.entity in {entity, "*"} and entity not in ["users", "departments", "permissions",
                                                                       "pending_approvals", "history_logs",
                                                                       "restore"]) and
                permission.entity_id in {str(entity_id), "*"} and
                (
                    permission.access_type == "*" or
                    access_type in method_map.get(permission.access_type, set())
                )
        ):
            return True

    # Raise exception if no matching permission found
    return False


def has_approval_privileges(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user.is_superuser or user.role == "admin" or user.direct_manager_id is None:
        return True
    return False
