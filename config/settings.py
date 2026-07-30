import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq") # "gemini" or "groq"
GROQ_MODEL = "llama-3.1-8b-instant"
GEMINI_MODEL = "gemini-2.0-flash"
CONFIDENCE_THRESHOLD = 0.55
