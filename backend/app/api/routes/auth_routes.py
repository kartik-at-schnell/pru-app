from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.crud import user_crud
from app.security import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user
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

@router.get("/getUserRoleandPermission_byemail", response_model=user_schema.UserWithPermissions)
def get_current_user_profile(
    email: str | None = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches the currently logged-in user's profile, 
    including a flattened list of all their permissions.
    Optionally accepts an email to fetch a specific user's profile (Admin use case).
    """
    target_user = current_user
    if email:
        # TODO: Add check if current_user is Admin before allowing this
        user_by_email = user_crud.get_user_by_email(db, email=email)
        if user_by_email:
            target_user = user_by_email
        else:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with email {email} not found"
            )

    # Group permissions by module
    permissions_by_module = {}
    
    for role in target_user.roles:
        for perm in role.permissions:
            module_name = perm.module.name if perm.module else "Other"
            if module_name not in permissions_by_module:
                permissions_by_module[module_name] = set()
            permissions_by_module[module_name].add(perm.permission_name)
            
    # Convert to list of ModulePermissions
    module_permissions_list = []
    for module, slugs in permissions_by_module.items():
        module_permissions_list.append(
            user_schema.ModulePermissions(module=module, permissions=list(slugs))
        )

    # Create response object
    user_response = user_schema.UserWithPermissions.model_validate(target_user)
    user_response.permissions = module_permissions_list
    
    return user_response
