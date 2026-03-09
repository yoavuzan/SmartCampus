from contextlib import contextmanager
from sqlmodel import Session
from ..database import engine

@contextmanager
def get_db():
    """
    Context manager for database sessions.
    Works for both FastAPI 'Depends' and standard 'with' statements.
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
