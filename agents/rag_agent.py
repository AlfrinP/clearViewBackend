from crewai import Agent, Task
from tools.rag_tool import rag_tool

agent = Agent(
    role="RAG Agent",
    goal="Answer using MongoDB vector search",
    backstory="Knowledge retrieval specialist",
    tools=[rag_tool],
    verbose=True,
)

task = Task(
    description="Find relevant content for 'indexing guidance'",
    expected_output="A concise answer citing the most relevant matches",
    agent=agent,
)
