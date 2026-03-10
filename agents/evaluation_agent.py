from crewai import Agent

from models import crew_llm

evaluation_agent = Agent(
    role="Evidence Evaluation Specialist",
    goal="Assess whether retrieved internal evidence is sufficient to classify the claim without web search.",
    backstory="A fact-verification analyst who quantifies evidence strength and uncertainty.",
    llm=crew_llm,
    allow_delegation=False,
    verbose=False,
)
