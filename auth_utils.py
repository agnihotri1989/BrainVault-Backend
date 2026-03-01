from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    
    Args:
        plain_password: The user's password in plain text (e.g., "MySecret123")
    
    Returns:
        A bcrypt hash string (e.g., "$2b$12$KIXx8vF3...")
    
    Example:
        >>> hash_password("MySecret123")
        '$2b$12$KIXx8vF3yT9Ks...'
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches a bcrypt hash.
    
    Args:
        plain_password: The password the user is trying to login with
        hashed_password: The stored hash from the database
    
    Returns:
        True if passwords match, False otherwise
    
    Example:
        >>> stored_hash = "$2b$12$KIXx8vF3yT9Ks..."
        >>> verify_password("MySecret123", stored_hash)
        True
        >>> verify_password("WrongPassword", stored_hash)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)