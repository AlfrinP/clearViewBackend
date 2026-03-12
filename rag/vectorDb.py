from langchain_mongodb import MongoDBAtlasVectorSearch
from models import embeddings
from env import MONGODB_COLLECTION, DB_NAME,ATLAS_VECTOR_SEARCH_INDEX_NAME, MONGODB_CONNECTION_STRING
from pymongo import MongoClient


client = MongoClient(MONGODB_CONNECTION_STRING)


COLLECTION = client[DB_NAME][MONGODB_COLLECTION]

vector_store = MongoDBAtlasVectorSearch(
    collection=COLLECTION,
    embedding=embeddings,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn="cosine"
)

# vector_store.create_vector_search_index(dimensions=768)