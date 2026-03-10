from crewai import Agent

from models import crew_llm

decision_agent = Agent(
    role="Final Decision Specialist",
    goal="Produce a final fake-news classification and confidence grounded only in collected evidence.",
    backstory="A senior misinformation analyst who issues transparent verdicts with calibrated confidence.",
    llm=crew_llm,
    allow_delegation=False,
    verbose=False,
)
