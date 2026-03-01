# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment variable
# Format: postgresql://user:password@host:port/database_name
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://brainvault_user:brainvault123@db:5432/brainvault"
)

# Create the SQLAlchemy engine
# This manages the connection to PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    echo=True  # Log all SQL queries (useful for debugging, disable in production)
)

# SessionLocal: Factory for creating database sessions
# Each request will get its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: All models will inherit from this
Base = declarative_base()


# Dependency: Get a database session for each request
def get_db():
    """
    Creates a new database session for each request.
    Automatically closes the session after the request is done.
    """
    db = SessionLocal()
    try:
        yield db  # Provide the session to the endpoint
    finally:
        db.close()  # Always close the session, even if an error occurs