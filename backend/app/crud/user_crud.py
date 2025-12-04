from sqlalchemy.orm import Session
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

    # Assign Role based on Email Pattern
    mappings = db.query(models.EmailRoleMapping).all()
    assigned_role = None

    for mapping in mappings:
        pattern = mapping.email_pattern
        # Handle exact match
        if pattern == user.email:
            assigned_role = mapping.role
            break
        # Handle simple suffix matching (e.g., "%@admin.com")
        elif pattern.startswith("%"):
            suffix = pattern[1:]
            if user.email.lower().endswith(suffix.lower()):
                assigned_role = mapping.role
                break
        # Can add more complex pattern matching if needed
    
    if assigned_role:
        db_user.roles.append(assigned_role)
    else:
        # Default to 'User' role if no mapping found
        default_role = db.query(models.Role).filter(models.Role.name == "User").first()
        if default_role:
            db_user.roles.append(default_role)
    
    db.commit()
    db.refresh(db_user)

    return db_user
