from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch

from models import embeddings
from env import (
    ATLAS_VECTOR_SEARCH_INDEX_NAME,
    DB_NAME,
    MONGODB_COLLECTION,
    MONGODB_CONNECTION_STRING,
)

if not all(
    [
        MONGODB_CONNECTION_STRING,
        DB_NAME,
        MONGODB_COLLECTION,
        ATLAS_VECTOR_SEARCH_INDEX_NAME,
    ]
):
    raise RuntimeError(
        "MongoDB Atlas RAG is not configured. Set MONGODB_CONNECTION_STRING, "
        "DB_NAME, MONGODB_COLLECTION, and ATLAS_VECTOR_SEARCH_INDEX_NAME."
    )

client = MongoClient(MONGODB_CONNECTION_STRING)
collection = client[DB_NAME][MONGODB_COLLECTION]

vectorstore = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine",
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
