from typing import List, Optional
from pydantic import BaseModel

class ModuleBase(BaseModel):
    name: str

class ModuleCreate(ModuleBase):
    pass

class Module(ModuleBase):
    id: int

    class Config:
        from_attributes = True

class PermissionBase(BaseModel):
    slug: str
    module_id: Optional[int] = None

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int
    module: Optional[Module] = None

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    permissions: List[int] = [] # List of permission IDs

class RoleUpdate(RoleBase):
    permissions: Optional[List[int]] = None

class Role(RoleBase):
    id: int
    permissions: List[Permission] = []

    class Config:
        from_attributes = True

class UserRoleAssignment(BaseModel):
    role_ids: List[int]
