from langchain_groq import ChatGroq
from env import LLM_MODEL, MODEL_TEMPERATURE, MODEL_MAX_TOKENS, MODEL_MAX_RETRIES, MODEL_TIMEOUT

llm = ChatGroq(
    model=LLM_MODEL,
    temperature=MODEL_TEMPERATURE,
    max_tokens=MODEL_MAX_TOKENS,
    reasoning_format="parsed",
    timeout=MODEL_TIMEOUT,
    max_retries=MODEL_MAX_RETRIES,
)
