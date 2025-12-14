import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    QDRANT_URL: str = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()
