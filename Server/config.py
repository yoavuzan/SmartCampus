import os
from dotenv import load_dotenv

# Load .env file (only if it exists and not already loaded)
if os.path.exists(".env"):
    load_dotenv()

class Settings:
    # Use os.getenv with fallbacks to handle environment variables from Docker
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-default-secret-key-for-dev")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")

settings = Settings()
