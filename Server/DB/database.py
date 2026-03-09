import os
from sqlmodel import create_engine

# Get the path to the Server directory
DB_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_DIR = os.path.dirname(DB_DIR)
sqlite_file_path = os.path.join(SERVER_DIR, "database.db")

sqlite_url = f"sqlite:///{sqlite_file_path}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
