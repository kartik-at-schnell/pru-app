import os
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import user_crud
from app.models import user_models
from app.models.user_models import Role, EmailRoleMapping

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1080 #mins

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# pre hashing with SHA256 then bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prehash_password(password: str) -> str:

    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def hash_password(password: str) -> str:
    prehashed = _prehash_password(password)
    return pwd_context.hash(prehashed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    prehashed = _prehash_password(plain_password)
    return pwd_context.verify(prehashed, hashed_password)

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
    token: Optional[str] = Depends(oauth2_scheme),
    email: Optional[str] = Query(None), # Optional email query param
    db: Session = Depends(get_db) #injecting the db session
) -> user_models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    target_email = None

    # Priority: Email Query Param ONLY
    # Token is completely ignored as per request.
    if email:
        target_email = email
    # Removed mandatory email check to allow anonymous/default user role

    # 3. Check if User exists in DB
    user = None
    if target_email:
        user = user_crud.get_user_by_email(db, email=target_email)
    
    if user:
        if not user.is_active:
             raise HTTPException(status_code=400, detail="Inactive user")
        return user

    # 4. User NOT found in DB -> Fallback Logic (Virtual/Transient User)
    
    # Create a transient User object (not saved to DB yet)
    # We use the target_email and set is_active=True for now (or strictly control this)
    transient_user = user_models.User(
        email=target_email or "anonymous@user",
        is_active=True, 
        roles=[]
    )

    # 5. Check EmailRoleMapping
    # We look for a mapping that matches the target_email
    mappings = db.query(EmailRoleMapping).all()
    mapping_found = False

    if target_email:
        for mapping in mappings:
            pattern = mapping.email_pattern
            # Exact match
            if pattern == target_email:
                transient_user.roles.append(mapping.role)
                mapping_found = True
            # Suffix match (e.g. "%@admin.com")
            elif pattern.startswith("%"):
                suffix = pattern[1:]
                if target_email.lower().endswith(suffix.lower()):
                    transient_user.roles.append(mapping.role)
                    mapping_found = True
    
    # 6. If NO mapping found, assign default "User" role
    if not mapping_found:
        default_role = db.query(Role).filter(Role.name == "User").first()
        if default_role:
            transient_user.roles.append(default_role)

    # 7. Persist the user to generate an ID
    # Must provide a password hash constraint
    # Using a pre-computed or dummy hash to avoid 'password too long' bcryt errors in some envs
    transient_user.hashed_password = "dummy_safe_hash_value"
    
    try:
        db.add(transient_user)
        db.commit()
        db.refresh(transient_user)
    except Exception:
        db.rollback()
        # Fallback: User might have been created by another request concurrently
        # or earlier check failed for some reason.
        existing_user = user_crud.get_user_by_email(db, email=target_email)
        if existing_user:
            return existing_user
        else:
             # Real error 
             raise HTTPException(status_code=500, detail="Failed to create/retrieve user record")
    
    return transient_user

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
