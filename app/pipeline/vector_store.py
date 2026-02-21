"""MongoDB Atlas Vector Search client."""

from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient

from app.env import (
    ATLAS_VECTOR_SEARCH_INDEX_NAME,
    DB_NAME,
    MONGODB_COLLECTION,
    MONGODB_CONNECTION_STRING,
)
from app.models.llm import embeddings

_client = MongoClient(MONGODB_CONNECTION_STRING)
_collection = _client[DB_NAME][MONGODB_COLLECTION]

vector_store = MongoDBAtlasVectorSearch(
    collection=_collection,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
)
