import logging
from functools import lru_cache
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from rag.rag_store import retriever

logger = logging.getLogger(__name__)
MAX_PASSAGE_CHARS = 300


class RAGToolInput(BaseModel):
    query: str = Field(..., description="Query or claim to retrieve evidence for.")


class RAGTool(BaseTool):
    name: str = "rag_retriever"
    description: str = (
        "Retrieve relevant evidence passages from the internal MongoDB Atlas "
        "vector knowledge base."
    )
    args_schema: Type[BaseModel] = RAGToolInput

    @staticmethod
    @lru_cache(maxsize=100)
    def _retrieve(query: str):
        return tuple(retriever.get_relevant_documents(query))

    def _run(self, query: str) -> str:
        docs = list(self._retrieve(query))
        if not docs:
            logger.info("RAG retrieval returned 0 docs for query=%r", query)
            return "No relevant internal evidence found."

        logger.info("RAG retrieval returned %d docs for query=%r", len(docs), query)
        for idx, doc in enumerate(docs, start=1):
            source = doc.metadata.get("source", "unknown")
            snippet = doc.page_content.replace("\n", " ").strip()[:300]
            logger.info("RAG hit %d | source=%s | snippet=%s", idx, source, snippet)

        compact_passages = []
        for doc in docs:
            source = str(doc.metadata.get("source", "unknown")).strip()
            passage = doc.page_content.replace("\n", " ").strip()[:MAX_PASSAGE_CHARS]
            compact_passages.append(f"source={source} | passage={passage}")
        return "\n\n".join(compact_passages)


rag_tool = RAGTool()
