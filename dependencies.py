from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from database import get_db
from models import User
from jwt_utils import verify_access_token

# OAuth2PasswordBearer: Extracts token from Authorization header
# tokenUrl: Tells FastAPI where to get tokens (used in auto-generated docs)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.
    
    This function:
    1. Extracts JWT token from Authorization header (done by oauth2_scheme)
    2. Verifies the token and extracts email
    3. Fetches user from database
    4. Returns User object (or raises 401 error)
    
    Usage in endpoints:
        @app.get("/api/notes")
        def get_notes(current_user: User = Depends(get_current_user)):
            # current_user is automatically provided
            print(current_user.email)
    
    Args:
        token: JWT token extracted from "Authorization: Bearer <token>" header
        db: Database session
    
    Returns:
        User object from database
    
    Raises:
        HTTPException 401: If token is invalid/expired or user doesn't exist
    """
    
    # Define the exception to raise if authentication fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify token and extract email
        email = verify_access_token(token)
        
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise credentials_exception
    
    return user