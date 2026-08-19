import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ..core.config import settings

logger = logging.getLogger(__name__)

def create_db_engine():
    connect_args = {}
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    try:
        test_engine = create_engine(
            db_url,
            connect_args=connect_args,
            pool_pre_ping=True,
        )
        # Test connection
        with test_engine.connect() as conn:
            pass
        return test_engine
    except Exception as e:
        logger.warning(f"PostgreSQL server unreachable ({e}). Falling back to SQLite database.")
        sqlite_url = "sqlite:///./civic_ai_dev.db"
        return create_engine(sqlite_url, connect_args={"check_same_thread": False}, pool_pre_ping=True)

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables from SQLAlchemy metadata."""
    from .base import Base
    from ..models.user import User  # noqa: F401
    from ..models.incident import Incident  # noqa: F401
    from ..models.verification import Verification  # noqa: F401
    from ..models.notification import Notification  # noqa: F401
    from ..models.department import Department  # noqa: F401
    from ..models.point_transaction import PointTransaction  # noqa: F401
    from ..models.sos_event import SOSEvent  # noqa: F401
    from ..models.risk_assessment import RiskAssessment  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified and initialized successfully.")
        db = SessionLocal()
        return db
    except Exception as e:
        logger.warning(f"Could not initialize DB tables: {e}")
        return None

