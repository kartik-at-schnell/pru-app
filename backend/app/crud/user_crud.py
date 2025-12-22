from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models 
from ..schemas import user_schema 
# from app.utils.hash_password import hash_password
from typing import Optional

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(func.lower(models.User.email) == email.lower()).first()

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

    # Assign Role based on Email Pattern
    mappings = db.query(models.EmailRoleMapping).all()
    assigned_role = None

    for mapping in mappings:
        pattern = mapping.email_pattern
        # Handle exact match (case insensitive)
        if pattern.lower() == user.email.lower():
            db_user.roles.append(mapping.role)
        # Handle simple suffix matching (e.g., "%@admin.com")
        elif pattern.startswith("%"):
            suffix = pattern[1:]
            if user.email.lower().endswith(suffix.lower()):
                db_user.roles.append(mapping.role)
    
    # Default to 'User' role if no roles assigned
    if not db_user.roles:
        default_role = db.query(models.Role).filter(models.Role.name == "User").first()
        if default_role:
            db_user.roles.append(default_role)
    
    db.commit()
    db.refresh(db_user)

    return db_user
