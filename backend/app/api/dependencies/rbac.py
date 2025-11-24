from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import user_crud

def get_current_user(
    x_user_email: str = Header(..., alias="X-User-Email"),
    db: Session = Depends(get_db)
):
    user = user_crud.get_user_by_email(db, email=x_user_email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_role(*roles):
    roles = {r.lower() for r in roles}  # normalize list
    
    def checker(user = Depends(get_current_user)):
        user_roles = {r.name.lower() for r in user.roles}

        print("=== RBAC DEBUG ===")
        print("User:", user.email)
        print("User Roles:", user_roles)
        print("Allowed Roles:", roles)
        print("==================")

        if not user_roles.intersection(roles):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        return user  # return user, not True

    return checker
