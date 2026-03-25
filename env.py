import os
from dotenv import load_dotenv
import getpass

load_dotenv()


def get_env_variable(
    key: str, default=None, cast_type=None, required=False, secret=False
):
    """
    Fetch environment variable with optional casting and fallback.
    Prompts user if secret and not found.
    """
    value = os.getenv(key, default)

    if value is None and required:
        if secret:
            value = getpass.getpass(f"Enter {key}: ")
            os.environ[key] = value
        else:
            raise ValueError(f"Missing required environment variable: {key}")

    if value is not None and cast_type:
        try:
            value = cast_type(value)
        except ValueError:
            raise ValueError(f"Invalid type for {key}, expected {cast_type}")

    return value


# ---- API KEYS ----
HUGGINGFACEHUB_API_TOKEN = get_env_variable(
    "HUGGINGFACEHUB_API_TOKEN", required=True, secret=True
)

GROQ_API_KEY = get_env_variable("GROQ_API_KEY", required=True, secret=True)

TAVILY_API_KEY = get_env_variable("TAVILY_API_KEY", required=True, secret=True)


# ---- MODEL CONFIG ----
LLM_MODEL = get_env_variable("LLM_MODEL", default="llama3-70b-8192")

MODEL_TEMPERATURE = get_env_variable("MODEL_TEMPERATURE", default=0.7, cast_type=float)

MODEL_MAX_TOKENS = get_env_variable("MODEL_MAX_TOKENS", default=1024, cast_type=int)

MODEL_MAX_RETRIES = get_env_variable("MODEL_MAX_RETRIES", default=3, cast_type=int)

MODEL_TIMEOUT = get_env_variable("MODEL_TIMEOUT", default=60, cast_type=int)


# ---- DATABASE CONFIG ----
MONGODB_COLLECTION = get_env_variable("MONGODB_COLLECTION", default="documents")

ATLAS_VECTOR_SEARCH_INDEX_NAME = get_env_variable(
    "ATLAS_VECTOR_SEARCH_INDEX_NAME", default="vector_index"
)


# ---- DEBUG PRINT (optional) ----
if __name__ == "__main__":
    print("Configuration Loaded Successfully")
