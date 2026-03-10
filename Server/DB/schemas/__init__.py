from contextlib import contextmanager
from sqlmodel import Session
from ..database import engine

def get_db():
    """
    FastAPI dependency for database sessions.
    FastAPI handles the generator lifecycle.
    """
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Standard context manager for database sessions.
    Used in scripts and manual session management.
    """
    db = Session(engine)
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
