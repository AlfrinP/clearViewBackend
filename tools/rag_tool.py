from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from rag.rag_store import retriever


class RAGToolInput(BaseModel):
    query: str = Field(..., description="Query or claim to retrieve evidence for.")


class RAGTool(BaseTool):
    name: str = "rag_retriever"
    description: str = (
        "Retrieve relevant evidence passages from the internal FAISS knowledge base."
    )
    args_schema: Type[BaseModel] = RAGToolInput

    def _run(self, query: str) -> str:
        docs = retriever.get_relevant_documents(query)
        if not docs:
            return "No relevant internal evidence found."
        return "\n\n".join(doc.page_content for doc in docs)


rag_tool = RAGTool()
