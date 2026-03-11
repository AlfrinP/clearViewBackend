import logging
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from rag.rag_store import retriever

logger = logging.getLogger(__name__)


class RAGToolInput(BaseModel):
    query: str = Field(..., description="Query or claim to retrieve evidence for.")


class RAGTool(BaseTool):
    name: str = "rag_retriever"
    description: str = (
        "Retrieve relevant evidence passages from the internal MongoDB Atlas "
        "vector knowledge base."
    )
    args_schema: Type[BaseModel] = RAGToolInput

    def _run(self, query: str) -> str:
        docs = retriever.get_relevant_documents(query)
        if not docs:
            logger.info("RAG retrieval returned 0 docs for query=%r", query)
            return "No relevant internal evidence found."

        logger.info("RAG retrieval returned %d docs for query=%r", len(docs), query)
        for idx, doc in enumerate(docs, start=1):
            source = doc.metadata.get("source", "unknown")
            snippet = doc.page_content.replace("\n", " ").strip()[:300]
            logger.info("RAG hit %d | source=%s | snippet=%s", idx, source, snippet)

        return "\n\n".join(doc.page_content for doc in docs)


rag_tool = RAGTool()
