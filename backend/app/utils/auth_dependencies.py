from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_models import User

def get_current_user(
    x_user_email: str = Header(None, alias="X-User-Email"),
    db: Session = Depends(get_db),
):
    """
    TEMP implementation: find user by email from header.
    No Azure AD involved.
    """
    if not x_user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Email header",
        )

    user = db.query(User).filter(User.email == x_user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def require_roles(allowed_roles: list[str]):
    """
    Dependency factory: ensures current user has at least one of allowed_roles.
    """
    def checker(current_user: User = Depends(get_current_user)):
        user_role_names = {r.name for r in current_user.roles}

        if not user_role_names.intersection(set(allowed_roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )

        return current_user

    return checker
