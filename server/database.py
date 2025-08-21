import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment variable (kept for potential future use)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./barbot.db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Database models removed - no authentication required

# Create database tables if they don't exist
def create_tables():
    Base.metadata.create_all(bind=engine)


# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
