from crewai_tools import MongoDBVectorSearchTool

from env import (
    ATLAS_VECTOR_SEARCH_INDEX_NAME,
    DB_NAME,
    MONGODB_COLLECTION,
    MONGODB_CONNECTION_STRING,
)

rag_tool = MongoDBVectorSearchTool(
    connection_string=MONGODB_CONNECTION_STRING,
    database_name=DB_NAME,
    collection_name=MONGODB_COLLECTION,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
)
