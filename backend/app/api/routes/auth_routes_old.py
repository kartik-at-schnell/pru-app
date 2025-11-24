from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.crud import user_crud
from app.security import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
# from app.utils.hash_password import verify_password, hash_password
from app.schemas import user_schema

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=user_schema.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = user_crud.get_user_by_email(db, email=form_data.username) # form_data uses username, so username = email
    if not user or user.hashed_password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
def register_new_user(
    user_in: user_schema.UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = user_crud.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    new_user = user_crud.create_user(db=db, user=user_in)
    return new_user
