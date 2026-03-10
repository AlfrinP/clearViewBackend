from crewai import Agent
from models import crew_llm

input_agent = Agent(
    role="News Input Processing Specialist",
    goal="Extract key claims, entities, and verifiable statements from user-submitted news content.",
    backstory="An NLP analyst who transforms noisy articles into concise fact-checkable claim units.",
    llm=crew_llm,
    allow_delegation=False,
    verbose=False,
)
