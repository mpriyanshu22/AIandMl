import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings and environment variables."""
    APP_NAME:str =os.getenv("APP_NAME")
    APP_VERSION:str =os.getenv("APP_VERSION")
    CHROMA_PERSIST_DIR:str =os.getenv("CHROMA_PERSIST_DIR")
    DEFAULT_TOP_K:int =os.getenv("DEFAULT_TOP_K")
    GEMINI_API_KEY:str =os.getenv("GEMINI_API_KEY")

settings = Settings()       
