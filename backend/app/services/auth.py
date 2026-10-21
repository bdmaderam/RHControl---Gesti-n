import hashlib, hmac, base64

def hash_password(password: str) -> str:
    salt = b"rhcontrol-local-salt"
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 120000)
    return base64.b64encode(digest).decode()

def verify_password(password: str, stored: str) -> bool:
    return hmac.compare_digest(hash_password(password), stored)
