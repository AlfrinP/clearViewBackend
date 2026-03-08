from crewai_tools import MongoDBVectorSearchTool

rag_tool = MongoDBVectorSearchTool(
    connection_string="mongodb+srv://...",
    database_name="mydb",
    collection_name="docs",
)
