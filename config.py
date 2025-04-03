import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please check your .env file.")

# Model Selection
SMALL_MODEL = "gpt-3.5-turbo"
BIG_MODEL = "gpt-4-turbo"  # or whatever the correct big model is

# Debugging Print (Remove after verifying)
print(f"Using API Key: {OPENAI_API_KEY[:10]}********")
print(f"Small Model: {SMALL_MODEL}")
print(f"Big Model: {BIG_MODEL}")
