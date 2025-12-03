import requests
from app.database import SessionLocal
from app.models import user_models
from app.security import create_access_token, hash_password
import uuid

BASE_URL = "http://127.0.0.1:8000"

def verify_profile():
    db = SessionLocal()
    try:
        # Create a test user
        email = f"test_profile_{uuid.uuid4()}@example.com"
        password = "password123"
        hashed_password = hash_password(password)
        
        user = user_models.User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            first_name="Test",
            last_name="User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Assign 'User' role (id=3)
        role_user = db.query(user_models.Role).filter(user_models.Role.name == "User").first()
        if role_user:
            user.roles.append(role_user)
            db.commit()
        
        # Generate token
        token = create_access_token(data={"sub": email})
        headers = {"Authorization": f"Bearer {token}"}

        # Test /auth/me
        print("Testing /auth/me...")
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"PASS: Got profile: {data}")
            
            # Check fields
            if data["email"] == email:
                print("PASS: Email matches.")
            else:
                print(f"FAIL: Email mismatch. Got {data['email']}")
                
            if "permissions" in data:
                print(f"PASS: Permissions field present: {data['permissions']}")
                if "reports.view" in data["permissions"]:
                     print("PASS: 'reports.view' found in permissions.")
                else:
                     print("FAIL: 'reports.view' NOT found.")
            else:
                print("FAIL: Permissions field missing.")
                
            if "roles" in data:
                 print(f"PASS: Roles field present: {data['roles']}")
            else:
                 print("FAIL: Roles field missing.")

        else:
            print(f"FAIL: Expected 200, got {response.status_code}. Body: {response.text}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        # Cleanup
        try:
            if 'user' in locals() and user.id:
                user_to_delete = db.query(user_models.User).filter(user_models.User.id == user.id).first()
                if user_to_delete:
                    db.delete(user_to_delete)
                    db.commit()
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")
        db.close()

if __name__ == "__main__":
    verify_profile()
