from crewai import Agent

from models import crew_llm
from tools.web_scraping_tool import web_scraping_tool

web_search_agent = Agent(
    role="Web Search Verification Specialist",
    goal="Collect high-quality external sources to validate claims when internal evidence is weak.",
    backstory="An OSINT researcher focused on trusted and recent corroborating references.",
    llm=crew_llm,
    tools=[web_scraping_tool],
    allow_delegation=False,
    verbose=False,
)
