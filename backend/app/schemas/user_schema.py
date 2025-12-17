from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# role schema
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True

#user schema

# base schema with fields common to reading/creating
class UserBase(BaseModel):
    email: EmailStr # automatically validates email format
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True

# schema for a new user
class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    roles: List[Role] = []

    class Config:
        from_attributes = True #allows reading data from SQLAlchemy models

#token schema (for login)

class TokenData(BaseModel):
    email: Optional[str] = None

#response when a user logs in successfully
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ModulePermissions(BaseModel):
    module: str
    permissions: List[str]

class UserWithPermissions(User):
    permissions: List[ModulePermissions] = []
