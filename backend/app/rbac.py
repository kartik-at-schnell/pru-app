from fastapi import Depends, HTTPException, status
from app.models import user_models
from app.security import get_current_user

class PermissionChecker:
    def __init__(self, permission_slug: str):
        self.permission_slug = permission_slug

    def __call__(self, current_user: user_models.User = Depends(get_current_user)) -> user_models.User:
        # Check if user has the required permission through any of their roles
        has_perm = False
        for role in current_user.roles:
            for permission in role.permissions:
                if permission.slug == self.permission_slug:
                    has_perm = True
                    break
            if has_perm:
                break
        
        # Admin role bypass (optional, but good for "superuser" access)
        # Based on the user request, Role 1 (Admin) gets everything.
        # We can check for role name "Admin" or if the role has the permission.
        # The screenshot implies Admin role has all permissions assigned in the DB, 
        # so the loop above should cover it if the data is set up correctly.
        # However, explicitly allowing "Admin" role is a safe fallback.
        if not has_perm:
             for role in current_user.roles:
                if role.name == "Admin":
                    has_perm = True
                    break

        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted: Requires '{self.permission_slug}' permission"
            )
        
        return current_user

def has_permission(slug: str):
    return PermissionChecker(slug)
