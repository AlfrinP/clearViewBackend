from langchain_groq import ChatGroq

from app.core.config import (
    LLM_MODEL,
    MODEL_MAX_RETRIES,
    MODEL_MAX_TOKENS,
    MODEL_TEMPERATURE,
    MODEL_TIMEOUT,
)

llm = ChatGroq(
    model=LLM_MODEL,
    temperature=MODEL_TEMPERATURE,
    max_tokens=MODEL_MAX_TOKENS,
    timeout=MODEL_TIMEOUT,
    max_retries=MODEL_MAX_RETRIES,
)

