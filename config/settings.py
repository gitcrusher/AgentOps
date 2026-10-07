import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq") # "gemini" or "groq"
# llama3-8b-8192 was decommissioned by Groq (caused HTTP 400 model_decommissioned),
# and llama-3.3-70b-versatile isn't available either. Picked from the live models list.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")  # 2.0-flash was retired
CONFIDENCE_THRESHOLD = 0.55

# LLM retry/timeout policy (AGENTS.md Section 2)
LLM_TIMEOUT_SECONDS = 15
LLM_RETRY_BACKOFF_SECONDS = 2

# MCP tool server call timeout
MCP_TOOL_TIMEOUT_SECONDS = 20
