# init_db.py
from database import engine, Base
from models import User  # Import all models here

def init_db():
    """
    Create all tables defined in models.py
    This only needs to be run once (or when you add new models)
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

if __name__ == "__main__":
    init_db()