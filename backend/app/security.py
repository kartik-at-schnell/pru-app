import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import user_crud
from app.models import user_models
from app.models.user_models import Role

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600 #mins

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# token funcs
class TokenData(BaseModel):
    email: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if email is None:
            return None 
    except JWTError:
        return None # invalid token
    return email

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db) #injecting the db session
) -> user_models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = decode_access_token(token)
    if email is None:
        #token decoding failed or email wasnt found in token
        raise credentials_exception

    user = user_crud.get_user_by_email(db, email=email)
    if user is None:
        #no user matches the email from the token
        raise credentials_exception
    if not user.is_active:
        #deny access to inactive users
        raise HTTPException(status_code=400, detail="Inactive user")

    #return the SQLAlchemy user obj
    return user

# func for RBAC
async def get_current_admin_user(
    current_user: user_models.User = Depends(get_current_user)
) -> user_models.User:

    # check if the users roles relationship contains a role named Admin
    is_admin = any(role.name == "Admin" for role in current_user.roles)

    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # 403 means "Forbidden", not just "Unauthorized"
            detail="Operation not permitted: Requires Admin privileges"
        )
    # If the check passes, return the user object
    return current_user
