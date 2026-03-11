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
