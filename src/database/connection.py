from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings
from src.database.models import Base
from src.utils.logger import logger

# Create SQLAlchemy engine (configured for SQLite multithreading support)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Session factory for DB transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes database tables based on ORM models."""
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schemas initialized successfully.")