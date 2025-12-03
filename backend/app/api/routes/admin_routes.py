from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import user_models
from app.schemas import rbac_schema
from app.security import get_current_admin_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin_user)]
)

# --- Roles ---

@router.get("/roles", response_model=List[rbac_schema.Role])
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(user_models.Role).all()
    return roles

@router.post("/roles", response_model=rbac_schema.Role)
def create_role(role_in: rbac_schema.RoleCreate, db: Session = Depends(get_db)):
    # Check if role exists
    existing_role = db.query(user_models.Role).filter(user_models.Role.name == role_in.name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    new_role = user_models.Role(
        name=role_in.name
    )
    
    # Add permissions
    if role_in.permissions:
        permissions = db.query(user_models.Permission).filter(user_models.Permission.id.in_(role_in.permissions)).all()
        new_role.permissions = permissions
        
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

@router.put("/roles/{role_id}", response_model=rbac_schema.Role)
def update_role(role_id: int, role_in: rbac_schema.RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(user_models.Role).filter(user_models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role_in.name:
        role.name = role_in.name
        
    if role_in.permissions is not None:
        permissions = db.query(user_models.Permission).filter(user_models.Permission.id.in_(role_in.permissions)).all()
        role.permissions = permissions
        
    db.commit()
    db.refresh(role)
    return role

# --- Permissions ---

@router.get("/permissions", response_model=List[rbac_schema.Permission])
def get_permissions(db: Session = Depends(get_db)):
    permissions = db.query(user_models.Permission).all()
    return permissions

@router.post("/permissions", response_model=rbac_schema.Permission)
def create_permission(perm_in: rbac_schema.PermissionCreate, db: Session = Depends(get_db)):
    existing_perm = db.query(user_models.Permission).filter(user_models.Permission.slug == perm_in.slug).first()
    if existing_perm:
        raise HTTPException(status_code=400, detail="Permission already exists")
        
    new_perm = user_models.Permission(
        slug=perm_in.slug
    )
    db.add(new_perm)
    db.commit()
    db.refresh(new_perm)
    return new_perm

# --- User Roles ---

@router.post("/users/{user_id}/roles")
def assign_roles_to_user(
    user_id: int, 
    role_assignment: rbac_schema.UserRoleAssignment, 
    db: Session = Depends(get_db)
):
    # Fetch user
    user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Fetch roles
    roles = db.query(user_models.Role).filter(user_models.Role.id.in_(role_assignment.role_ids)).all()
    
    # Validate that all role IDs were found
    if len(roles) != len(role_assignment.role_ids):
        found_ids = [role.id for role in roles]
        missing_ids = set(role_assignment.role_ids) - set(found_ids)
        raise HTTPException(status_code=400, detail=f"Roles not found: {missing_ids}")
        
    # Assign roles (replace existing)
    user.roles = roles
    db.commit()
    
    return {"message": "Roles assigned successfully", "user_id": user_id, "role_ids": [r.id for r in user.roles]}
