from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from config import GROQ_MAX_TOKENS, GROQ_MODEL, GROQ_TEMPERATURE
from env import GROQ_API_KEY

llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=GROQ_TEMPERATURE,
    max_tokens=GROQ_MAX_TOKENS,
)

crew_llm = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=GROQ_TEMPERATURE,
    max_tokens=GROQ_MAX_TOKENS,
)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
