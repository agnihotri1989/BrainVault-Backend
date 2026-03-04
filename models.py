# models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """
    User model - represents the 'users' table in PostgreSQL
    
    Table structure:
    - id: Primary key (auto-incrementing integer)
    - email: User's email (unique, cannot be null)
    - hashed_password: Bcrypt-hashed password (cannot be null)
    - created_at: Timestamp when user registered
    """
    
    __tablename__ = "users"  # Table name in PostgreSQL

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        """String representation for debugging"""
        return f"<User(id={self.id}, email={self.email})>"