# FILE: test_bcrypt.py
from passlib.context import CryptContext
import bcrypt # Import bcrypt directly too, just to see if it loads

print("--- Starting bcrypt test ---")

try:
    # 1. Check if bcrypt library loads directly
    print(f"bcrypt library loaded: {bcrypt}")
    # Try accessing something simple from bcrypt
    salt = bcrypt.gensalt()
    print(f"bcrypt gensalt() worked. Salt: {salt[:10]}...") # Print first 10 chars of salt

    # 2. Test passlib with bcrypt
    print("Initializing passlib CryptContext...")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    print("CryptContext initialized successfully.")

    # 3. Try hashing a password
    print("Hashing password 'testpassword'...")
    hashed_pw = pwd_context.hash("testpassword")
    print(f"Password hashed successfully: {hashed_pw[:20]}...") # Print start of hash

    # 4. Try verifying the password
    print("Verifying password...")
    is_valid = pwd_context.verify("testpassword", hashed_pw)
    print(f"Password verified successfully: {is_valid}")

    print("--- Test finished successfully ---")

except Exception as e:
    print("\n!!! TEST FAILED !!!")
    print(f"An error occurred: {type(e).__name__}")
    print(f"Error details: {e}")
    import traceback
    traceback.print_exc() # Print the full traceback