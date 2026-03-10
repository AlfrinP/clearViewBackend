from crewai_tools import TavilySearchTool

from env import TAVILY_API_KEY

web_scraping_tool = TavilySearchTool(api_key=TAVILY_API_KEY, max_results=5)
