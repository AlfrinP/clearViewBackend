from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

from env import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", api_key=GOOGLE_API_KEY)

crew_llm = ChatGoogleGenerativeAI(model="gemini-3-flash", api_key=GOOGLE_API_KEY)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
