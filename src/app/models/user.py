# src/app/model/user.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.app.core.database import Base
from src.app.models.permission import Permission


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # "admin" or "user"

    permissions = relationship("Permission", back_populates="user")
