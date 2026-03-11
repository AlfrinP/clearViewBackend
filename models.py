from langchain_huggingface import HuggingFaceEmbeddings
from crewai import LLM

from env import GROQ_API_KEY, GROQ_MAX_TOKENS, GROQ_MODEL, GROQ_TEMPERATURE

# llm = ChatGroq(
#     model=GROQ_MODEL,
#     api_key=GROQ_API_KEY,
#     temperature=GROQ_TEMPERATURE,
#     max_tokens=GROQ_MAX_TOKENS,
# )

crew_llm = LLM(
    model=f"groq/{GROQ_MODEL}",
    api_key=GROQ_API_KEY,
    temperature=GROQ_TEMPERATURE,
    max_tokens=GROQ_MAX_TOKENS,
)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
