import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set in environment variables")
    raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")

# Model Selection
SMALL_MODEL = os.getenv("SMALL_MODEL", "gpt-3.5-turbo")
BIG_MODEL = os.getenv("BIG_MODEL", "gpt-4-turbo")

# Memory Settings
MAX_MEMORY_EPISODES = int(os.getenv("MAX_MEMORY_EPISODES", "3"))
ENABLE_SUMMARIZATION = os.getenv("ENABLE_SUMMARIZATION", "True").lower() == "true"

# Content Settings
DEFAULT_EPISODE_LENGTHS = {
    "Short": 500,
    "Medium": 1000,
    "Long": 1500
}

# Cache Settings
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "True").lower() == "true"
CACHE_EXPIRY = int(os.getenv("CACHE_EXPIRY", "3600"))  # 1 hour default

# Verify configuration
logger.info(f"Using API Key: {OPENAI_API_KEY[:5]}*****")
logger.info(f"Small Model: {SMALL_MODEL}")
logger.info(f"Big Model: {BIG_MODEL}")
logger.info(f"Memory Settings: Max Episodes={MAX_MEMORY_EPISODES}, Summarization={ENABLE_SUMMARIZATION}")