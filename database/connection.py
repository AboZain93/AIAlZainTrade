"""
Database Connection and Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from contextlib import asynccontextmanager

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# SQLAlchemy setup
engine = None
SessionLocal = None
Base = declarative_base()

async def init_database():
    """Initialize database connection and tables"""
    global engine, SessionLocal
    
    try:
        # Create engine
        if settings.database_url.startswith("sqlite"):
            engine = create_engine(
                settings.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=settings.database_echo
            )
        else:
            engine = create_engine(
                settings.database_url,
                echo=settings.database_echo
            )
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        from .models import UserModel, TradeModel, SignalModel, SettingsModel
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def close_database():
    """Close database connections"""
    global engine
    if engine:
        engine.dispose()
        logger.info("Database connections closed")

def get_db_session() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

@asynccontextmanager
async def get_async_db_session():
    """Async context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()

class DatabaseManager:
    """Database operations manager"""
    
    @staticmethod
    def create_session() -> Session:
        """Create a new database session"""
        return SessionLocal()
    
    @staticmethod
    def execute_query(query: str, params: dict = None):
        """Execute raw SQL query"""
        with get_db_session() as db:
            if params:
                result = db.execute(query, params)
            else:
                result = db.execute(query)
            db.commit()
            return result.fetchall()
    
    @staticmethod
    def get_table_info(table_name: str):
        """Get table information"""
        query = f"PRAGMA table_info({table_name})" if settings.database_url.startswith("sqlite") else f"DESCRIBE {table_name}"
        return DatabaseManager.execute_query(query)