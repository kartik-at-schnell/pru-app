from sqlalchemy.orm import Session
from .. import models 
from ..schemas import user_schema 
from ..security import hash_password 

def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: user_schema.UserCreate) -> models.User:
    hashed_pass = hash_password(user.password)
    
    # new user database obj    
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_pass,
        first_name=user.first_name,
        middle_name=user.middle_name,
        last_name=user.last_name,
        is_active=True # default new users to active
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
