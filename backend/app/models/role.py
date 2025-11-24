from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base               # use SAME Base as user_models
from .user_models import user_roles_table  # association table

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    users = relationship(
        "User",
        secondary=user_roles_table,
        back_populates="roles",
    )
