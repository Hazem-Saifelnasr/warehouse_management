# src/app/model/permission.py

from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, Index, Enum
import enum
from sqlalchemy.orm import relationship
from src.app.core.database import Base


class AccessType(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    CREATE = "create"
    MANAGE = "manage"
    ASSIGN = "assign"
    EXPORT = "export"
    APPROVE = "approve"
    REVOKE = "revoke"
    ARCHIVE = "archive"
    RESTORE = "restore"
    SHARE = "share"
    EXECUTE = "execute"
    ALL = "*"


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    entity = Column(String, nullable=False)  # e.g., "project", "warehouse", "location", or "*"
    entity_id = Column(String, nullable=False)  # e.g., entity ID or "*"
    access_type = Column(Enum(AccessType), nullable=False)  # e.g., "read", "write", "delete", "manage", or "*"

    user = relationship("User", back_populates="permissions")

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("entity IN ('project', 'warehouse', 'location', 'item', '*')", name="valid_entity"),
        Index("ix_permission_user_entity", "user_id", "entity", "entity_id"),
    )

    # Comprehensive List of Access Types:
    # Read-Only Permissions:
    # read: Allows viewing or reading data without making any modifications.

    # Write Permissions:
    # write: Allows modifying existing data.
    # create: Allows adding new data (specific to creating entities).

    # Delete Permissions:
    # delete: Allows removing entities.

    # Administrative Permissions:
    # manage: Full access to manage entities, often encompassing read, write, and delete.
    # assign: Specific to assigning permissions to other users.

    # Specialized Permissions (Entity-Specific):
    # export: Allows exporting data (e.g., generating reports).
    # approve: Allows approving actions or data (e.g., approving a project or workflow).
    # revoke: Allows revoking permissions or actions.

    # Custom Permissions (As Needed):
    # archive: Allows archiving entities (soft delete or inactive state).
    # restore: Allows restoring archived entities.
    # share: Allows sharing entities with others.
    # execute: For running specific workflows, processes, or commands.
