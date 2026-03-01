from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ============ User Registration ============
class UserRegister(BaseModel):
    """
    Schema for user registration request.
    Client sends this when creating a new account.
    """
    email: EmailStr  # Automatically validates email format
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "ecurePassword123"
            }
        }

class UserResponse(BaseModel):
    """
    Schema for user response (without password).
    Sent back after successful registration or when fetching user details.
    """
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows creating from SQLAlchemy models

# ============ User Login ============
class UserLogin(BaseModel):
    """
    Schema for login request.
    OAuth2 standard uses 'username' field, but we'll map it to email.
    """
    username: str  # FastAPI OAuth2PasswordRequestForm expects 'username'
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "user@example.com",
                "password": "SecurePassword123"
            }
        }

class Token(BaseModel):
    """
    Schema for JWT token response.
    Sent back after successful login.
    """
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

class TokenData(BaseModel):
    """
    Schema for data stored inside JWT token payload.
    Used when decoding/validating tokens.
    """
    email: Optional[str] = None