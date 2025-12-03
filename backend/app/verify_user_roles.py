import requests
from app.database import SessionLocal
from app.models import user_models
from app.security import create_access_token, hash_password
import uuid

BASE_URL = "http://127.0.0.1:8000"

def verify_user_roles():
    db = SessionLocal()
    try:
        # 1. Create a test user
        email = f"test_roles_{uuid.uuid4()}@example.com"
        password = "password123"
        hashed_password = hash_password(password)
        
        user = user_models.User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            first_name="Role",
            last_name="Tester"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user {email} with ID {user.id}")

        # 2. Get Admin Token (assuming we have a way to get one, or we mock it)
        # For simplicity, let's create a temporary Admin user
        admin_email = f"admin_{uuid.uuid4()}@example.com"
        admin_user = user_models.User(
            email=admin_email,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        
        # Assign Admin role (ID 1)
        admin_role = db.query(user_models.Role).filter(user_models.Role.name == "Admin").first()
        if admin_role:
            admin_user.roles.append(admin_role)
            db.commit()
        
        admin_token = create_access_token(data={"sub": admin_email})
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 3. Assign Roles to User (ID 2 and 3)
        # Assuming Roles: 2=Supervisor/Manager, 3=User exist from seed
        role_ids = [2, 3]
        print(f"Assigning roles {role_ids} to user {user.id}...")
        
        payload = {"role_ids": role_ids}
        response = requests.post(f"{BASE_URL}/admin/users/{user.id}/roles", json=payload, headers=headers)
        
        if response.status_code == 200:
            print("PASS: Roles assigned successfully.")
            print(response.json())
        else:
            print(f"FAIL: Failed to assign roles. Status: {response.status_code}, Body: {response.text}")
            return

        # 4. Verify via /auth/me (login as the test user)
        user_token = create_access_token(data={"sub": email})
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        print("Verifying roles via /auth/me...")
        me_response = requests.get(f"{BASE_URL}/auth/me", headers=user_headers)
        if me_response.status_code == 200:
            data = me_response.json()
            assigned_roles = [r['name'] for r in data['roles']] # Assuming roles is list of objects
            # Or if roles is list of strings, adjust accordingly. 
            # In user_schema.py: roles: List[Role] = [] where Role has name.
            
            print(f"User roles: {assigned_roles}")
            if "Supervisor/Manager" in assigned_roles and "User" in assigned_roles:
                print("PASS: User has both assigned roles.")
            else:
                print("FAIL: User missing expected roles.")
        else:
             print(f"FAIL: Could not fetch profile. Status: {me_response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        # Cleanup
        try:
            # Delete test users
            if 'user' in locals() and user.id:
                db.query(user_models.User).filter(user_models.User.id == user.id).delete()
            if 'admin_user' in locals() and admin_user.id:
                 db.query(user_models.User).filter(user_models.User.id == admin_user.id).delete()
            db.commit()
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")
        db.close()

if __name__ == "__main__":
    verify_user_roles()
