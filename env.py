from dotenv import load_dotenv
import os

# Load base env first
load_dotenv(".env")
# Then overlay local developer overrides (if present)
load_dotenv(".env.local", override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")
ATLAS_VECTOR_SEARCH_INDEX_NAME = os.getenv("ATLAS_VECTOR_SEARCH_INDEX_NAME")
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
DB_NAME = os.getenv("DB_NAME")

GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.2"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "1024"))

RAG_SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.75"))

# Optional toggle for local smoke testing without API keys.
MOCK_PIPELINE = os.getenv("MOCK_PIPELINE", "false").lower() == "true"
