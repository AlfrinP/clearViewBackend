from langchain.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from env import MONGODB_COLLECTION, ATLAS_VECTOR_SEARCH_INDEX_NAME, MONGO_URI, MONGO_DB_NAME

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

client = MongoClient(MONGO_URI)
collection = client[MONGO_DB_NAME][MONGODB_COLLECTION]

vector_store = MongoDBAtlasVectorSearch(
    embedding=embeddings,
    collection=collection,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
)

