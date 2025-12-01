from http.client import HTTPException
from sqlalchemy.orm import Session

from app.models.user_models import Role, User
from .. import models 
from ..schemas import user_schema 
# from app.utils.hash_password import hash_password
from typing import Optional

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: user_schema.UserCreate) -> models.User:
    # hashed_pass = hash_password(user.password)
    
    # new user database obj    
    db_user = models.User(
        email=user.email,
        hashed_password=user.password,
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        is_active=True # default new users to active
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_roles_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User not found")
    return [r.name for r in user.roles]


# def assign_role(db: Session, email: str, role_name: str):
#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         raise HTTPException(404, "User not found")

#     role = db.query(Role).filter(Role.name == role_name).first()
#     if not role:
#         raise HTTPException(404, "Role not found")

#     if role in user.roles:
#         raise HTTPException(400, "User already has role")

#     user.roles.append(role)
#     db.commit()
#     return user


# def remove_role(db: Session, email: str, role_name: str):
#     user = db.query(User).filter(User.email == email).first()
#     role = db.query(Role).filter(Role.name == role_name).first()

#     if not user or not role:
#         raise HTTPException(404, "Not found")

#     if role not in user.roles:
#         raise HTTPException(400, "User does not have this role")

#     user.roles.remove(role)
#     db.commit()

# def create_role(db: Session, payload: user_schema.RoleCreate):
#     role = Role(**payload.dict())
#     db.add(role)
#     db.commit()
#     db.refresh(role)
#     return role


# def update_role(db: Session, role_id: int, payload: RoleUpdate):
#     role = db.query(Role).get(role_id)
#     if not role:
#         raise HTTPException(404, "Role not found")

#     for k, v in payload.dict(exclude_unset=True).items():
#         setattr(role, k, v)

#     db.commit()
#     return role


# def delete_role(db: Session, role_id: int):
#     role = db.query(Role).get(role_id)
#     if not role:
#         raise HTTPException(404, "Role not found")

#     db.delete(role)
#     db.commit()

