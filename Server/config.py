import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

settings = Settings()
