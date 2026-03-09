import os
from sqlmodel import create_engine, SQLModel
from .schemas.Student import Student

# Get the path to the Server directory (one level up from this file)
DB_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.dirname(DB_DIR)
sqlite_file_path = os.path.join(SERVER_DIR, "database.db")

sqlite_url = f"sqlite:///{sqlite_file_path}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # RUN the seed script to populate the database with initial data
    from .seed import seed_db
    seed_db()
