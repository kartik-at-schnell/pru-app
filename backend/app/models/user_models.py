from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base  # import Base from our base.py

user_roles_table = Table(
    'user_roles',
    Base.metadata,
    Column('user_email', String(255), ForeignKey('users.email'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# user table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False) 
    first_name = Column(String(100), nullable=True)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    roles = relationship(
        "Role",
        secondary=user_roles_table,
        primaryjoin="User.email==user_roles.c.user_email",
        secondaryjoin="Role.id==user_roles.c.role_id",
        back_populates="users"
    )
    azure_ad_object_id = Column(String(255), nullable=True)

role_permissions_table = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# role table
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    # relationship to users
    users = relationship(
        "User",
        secondary=user_roles_table,
        primaryjoin="Role.id==user_roles.c.role_id",
        secondaryjoin="User.email==user_roles.c.user_email",
        back_populates="roles"
    )
    # relationship to permissions
    permissions = relationship("Permission", secondary=role_permissions_table, back_populates="roles")


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)

    permissions = relationship("Permission", back_populates="module")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    permission = Column(String(100), unique=True, index=True, nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=True)

    module = relationship("Module", back_populates="permissions")
    roles = relationship("Role", secondary=role_permissions_table, back_populates="permissions")


class EmailRoleMapping(Base):
    __tablename__ = "email_role_mappings"

    id = Column(Integer, primary_key=True, index=True)
    email_pattern = Column(String(255), unique=True, index=True, nullable=False) # e.g., "%@admin.com"
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    description = Column(String(255), nullable=True)

    role = relationship("Role")


