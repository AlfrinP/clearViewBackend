from crewai import Agent

from models import crew_llm
from tools.rag_tool import rag_tool

rag_agent = Agent(
    role="RAG Retrieval Specialist",
    goal="Retrieve the most relevant evidence from the internal vector knowledge base for each extracted claim.",
    backstory="A retrieval engineer who prioritizes precision, provenance, and semantic similarity signals.",
    llm=crew_llm,
    tools=[rag_tool],
    allow_delegation=False,
    verbose=False,
)
