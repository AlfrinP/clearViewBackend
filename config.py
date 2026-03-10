import os


GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "1024"))

RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.75"))

# Optional toggle for local smoke testing without API keys.
MOCK_PIPELINE = os.getenv("MOCK_PIPELINE", "false").lower() == "true"
