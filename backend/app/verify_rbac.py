import requests
from app.database import SessionLocal
from app.models import user_models
from app.security import create_access_token, hash_password
import uuid

BASE_URL = "http://127.0.0.1:8000"

def verify_rbac():
    db = SessionLocal()
    try:
        # Create a test user
        email = f"test_rbac_{uuid.uuid4()}@example.com"
        password = "password123"
        hashed_password = hash_password(password)
        
        user = user_models.User(
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"Created test user: {email}")

        # Assign 'User' role (id=3) - assumes seeded
        role_user = db.query(user_models.Role).filter(user_models.Role.name == "User").first()
        if role_user:
            user.roles.append(role_user)
            db.commit()
        else:
            print("Role 'User' not found. Please run seed_rbac.py first.")
            return

        # Generate token
        token = create_access_token(data={"sub": email})
        headers = {"Authorization": f"Bearer {token}"}

        # Test 1: Access /test-rbac (requires 'users.view')
        # User role has 'reports.view' only (from seed)
        print("Test 1: Accessing /test-rbac with 'User' role (should fail)...")
        response = requests.get(f"{BASE_URL}/test-rbac", headers=headers)
        if response.status_code == 403:
            print("PASS: Access denied as expected.")
        else:
            print(f"FAIL: Expected 403, got {response.status_code}. Body: {response.text}")

        # Test 2: Assign 'Admin' role (id=1) - has all permissions
        print("Assigning 'Admin' role...")
        role_admin = db.query(user_models.Role).filter(user_models.Role.name == "Admin").first()
        user.roles = [role_admin] # Replace roles
        db.commit()

        # Test 3: Access /test-rbac (requires 'users.view')
        print("Test 3: Accessing /test-rbac with 'Admin' role (should succeed)...")
        response = requests.get(f"{BASE_URL}/test-rbac", headers=headers)
        if response.status_code == 200:
            print("PASS: Access granted.")
        else:
            print(f"FAIL: Expected 200, got {response.status_code}. Body: {response.text}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        # Cleanup
        try:
            if 'user' in locals() and user.id:
                # Re-fetch user to ensure it's attached to session
                user_to_delete = db.query(user_models.User).filter(user_models.User.id == user.id).first()
                if user_to_delete:
                    db.delete(user_to_delete)
                    db.commit()
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")
        db.close()


if __name__ == "__main__":
    verify_rbac()
