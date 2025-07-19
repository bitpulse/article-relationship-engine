# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
    
    # Model settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    GPT_MODEL = "gpt-3.5-turbo"  # Use gpt-4-turbo-preview for better results
    
    # Search settings
    MAX_SEARCH_RESULTS = 10
    SIMILARITY_THRESHOLD = 0.3  # Lower threshold for better matching
    CONTEXT_SEARCH_DEPTH = 5
    
    # Cache settings
    CACHE_DIR = "./cache"
    CACHE_EXPIRY = 3600  # 1 hour

if not Config.OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in .env file")