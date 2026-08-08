from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import Settings

engine = create_engine(Settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastaAPI dependency for database session.3"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
