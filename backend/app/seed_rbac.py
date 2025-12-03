from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import user_models

def seed_data():
    db = SessionLocal()
    try:
        # Permissions
        permissions_data = [
            {"id": 50, "slug": "users.create"},
            {"id": 51, "slug": "users.view"},
            {"id": 52, "slug": "users.delete"},
            {"id": 53, "slug": "reports.view"},
            {"id": 54, "slug": "settings.edit"},
        ]

        permissions = {}
        for p_data in permissions_data:
            perm = db.query(user_models.Permission).filter_by(slug=p_data["slug"]).first()
            if not perm:
                perm = user_models.Permission(**p_data)
                db.add(perm)
                print(f"Created permission: {perm.slug}")
            else:
                print(f"Permission already exists: {perm.slug}")
            permissions[p_data["id"]] = perm
        
        db.commit()

        # Roles
        roles_data = [
            {"id": 1, "name": "Admin"},
            {"id": 2, "name": "Supervisor/Manager"},
            {"id": 3, "name": "User"},
        ]

        for r_data in roles_data:
            role = db.query(user_models.Role).filter_by(name=r_data["name"]).first()
            if not role:
                role = user_models.Role(**r_data)
                db.add(role)
                print(f"Created role: {role.name}")
            else:
                print(f"Role already exists: {role.name}")
            
            # Assign permissions
            if r_data["id"] == 1: # Admin
                role.permissions = list(permissions.values())
            elif r_data["id"] == 2: # Supervisor
                role.permissions = [p for pid, p in permissions.items() if pid != 52] # No delete
            elif r_data["id"] == 3: # User
                role.permissions = [permissions[53]] # Only reports.view (assumption)
            
        db.commit()
        print("Seeding complete.")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
