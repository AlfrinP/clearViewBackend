from crewai import Agent, Task
from tools import web_scraping_tool

researcher = Agent(
    role="Market Researcher",
    goal="Find information about the latest AI trends",
    backstory="An expert market researcher specializing in technology.",
    tools=[web_scraping_tool],
    verbose=True,
)

# Create a task for the agent
research_task = Task(
    description="Search for the top 3 AI trends in 2024.",
    expected_output="A JSON report summarizing the top 3 AI trends found.",
    agent=researcher,
)
