from crewai import Agent

from models import crew_llm
from tools.web_search import tavily_web_search_tool

web_search_agent = Agent(
    role="Web Research Specialist",
    goal=(
        "Search the internet for reliable information related "
        "to news claims."
    ),
    backstory="An investigative journalist skilled at finding trustworthy sources.",
    llm=crew_llm,
    tools=[tavily_web_search_tool],
    allow_delegation=False,
    verbose=False,
)
