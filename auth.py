from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserRegister, UserResponse, Token
from auth_utils import hash_password, verify_password
from jwt_utils import create_access_token

# Create router for auth endpoints
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Steps:
    1. Check if email already exists
    2. Hash the password
    3. Create user in database
    4. Return user details (without password)
    """
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_pwd = hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pwd
    )
    
    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Get the auto-generated ID
    
    return new_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login user and return JWT token.
    
    Steps:
    1. Find user by email
    2. Verify password
    3. Create JWT token
    4. Return token
    
    Note: OAuth2PasswordRequestForm uses 'username' field, but we treat it as email.
    """
    
    # Find user by email (form_data.username contains the email)
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}