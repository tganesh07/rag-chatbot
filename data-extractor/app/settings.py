import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"

class Settings:
    # LLM Configuration
    # Options: 'gemini', 'openai'
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
    
    # Model Names
    # Gemini: 'gemini-2.5-flash'
    # OpenAI: 'gpt-4o', 'gpt-3.5-turbo'
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    
    # Embedding Configuration
    # Using Local Sentence Transformers by default
    EMBEDDING_PROVIDER = "local"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Data Configuration
    # Users can set DATA_PATH env var to watch a different directory
    DATA_PATH = Path(os.getenv("DATA_PATH", DEFAULT_DATA_DIR))
    
    # Vector DB Configuration
    CHROMA_PERSIST_DIR = BASE_DIR / "chroma_db"
    
    # Watchdog Configuration
    WATCH_POLLING_INTERVAL = 2  # seconds

    @classmethod
    def validate(cls):
        """Simple validation to check if necessary keys are present based on provider."""
        if cls.LLM_PROVIDER == "gemini" and not cls.GOOGLE_API_KEY:
            return False, "Missing GOOGLE_API_KEY. Please set it in .env or environment variables."
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            return False, "Missing OPENAI_API_KEY. Please set it in .env or environment variables."
        if not cls.DATA_PATH.exists():
            try:
                os.makedirs(cls.DATA_PATH, exist_ok=True)
            except Exception as e:
                return False, f"Data path {cls.DATA_PATH} does not exist and could not be created: {e}"
        return True, "Configuration valid."

settings = Settings()
