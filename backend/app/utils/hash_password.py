import hashlib
from passlib.context import CryptContext

# bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # pre-hash with SHA-256 (fixed 32-byte digest
    sha256_digest = hashlib.sha256(password.encode("utf-8")).digest()
    # bcrypt the digest
    return pwd_context.hash(sha256_digest)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    sha256_digest = hashlib.sha256(plain_password.encode("utf-8")).digest()
    return pwd_context.verify(sha256_digest, hashed_password)
