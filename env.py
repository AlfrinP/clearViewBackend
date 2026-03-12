from dotenv import load_dotenv
import os

load_dotenv(".env")
load_dotenv(".env.local", override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")
ATLAS_VECTOR_SEARCH_INDEX_NAME = os.getenv("ATLAS_VECTOR_SEARCH_INDEX_NAME")
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
DB_NAME = os.getenv("DB_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")
GROQ_TEMPERATURE = os.getenv("GROQ_TEMPERATURE")
GROQ_MAX_TOKENS = os.getenv("GROQ_MAX_TOKENS")