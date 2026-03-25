from langchain.tools import tool
from rag import vector_store
from langchain_tavily import TavilySearchResults


@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


@tool
def web_search(query: str):
    """Search the web for information."""
    search = TavilySearchResults(
        max_results=5,
        topic="general",
    )
    return search.invoke({"query": query})
