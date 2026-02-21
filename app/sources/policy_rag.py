"""Internal Policy RAG - retrieve from vector store."""
from app.core.config import SOURCE_WEIGHTS
from app.pipeline.vector_store import vector_store


def retrieve_policy_context(query: str, k: int = 5) -> list[dict]:
    """
    Retrieve policy documents from vector store.
    Returns list of {title, snippet, url, domain, trust_score} for consistency with web_rag.
    """
    docs = vector_store.similarity_search(query, k=k)
    results = []
    for doc in docs:
        results.append({
            "title": doc.metadata.get("source", "Policy Document"),
            "snippet": doc.page_content,
            "url": None,
            "domain": "gov_policy",
            "trust_score": SOURCE_WEIGHTS.get("gov_policy", 1.0),
        })
    return results
