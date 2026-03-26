from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from pymongo import MongoClient

from app.core.config import (
    ATLAS_VECTOR_SEARCH_INDEX_NAME,
    MONGO_DB_NAME,
    MONGO_URI,
    MONGODB_COLLECTION,
)


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


@lru_cache(maxsize=1)
def get_vector_store() -> MongoDBAtlasVectorSearch:
    client = MongoClient(MONGO_URI)
    collection = client[MONGO_DB_NAME][MONGODB_COLLECTION]
    return MongoDBAtlasVectorSearch(
        embedding=get_embeddings(),
        collection=collection,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
        relevance_score_fn="cosine",
    )
