import json
import logging
from typing import TypedDict

from env import TAVILY_API_KEY
from tavily import TavilyClient
from crewai.tools import tool

logger = logging.getLogger(__name__)


class WebSearchResult(TypedDict):
    title: str
    content: str
    url: str


def _get_tavily_client() -> TavilyClient | None:
    if not TAVILY_API_KEY:
        logger.warning("TAVILY_API_KEY is not set; web search will return no results.")
        return None
    if TavilyClient is None:
        logger.exception("tavily-python is not installed; web search unavailable.")
        return None
    return TavilyClient(api_key=TAVILY_API_KEY)


def tavily_web_search(query: str, max_results: int = 5) -> list[WebSearchResult]:
    client = _get_tavily_client()
    if client is None:
        return []

    try:
        logger.debug(
            "Running Tavily web search. query=%s max_results=%s",
            query,
            max_results,
        )
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # pragma: no cover - network/API failure path
        logger.exception("Tavily search failed for query=%s error=%s", query, exc)
        return []

    raw_results = response.get("results", []) if isinstance(response, dict) else []
    cleaned: list[WebSearchResult] = []
    for item in raw_results[:max_results]:
        if not isinstance(item, dict):
            continue
        cleaned.append(
            {
                "title": str(item.get("title", "")).strip(),
                "content": str(item.get("content", "")).strip(),
                "url": str(item.get("url", "")).strip(),
            }
        )

    logger.debug("Tavily web search returned %s result(s).", len(cleaned))
    return cleaned


@tool("tavily_web_search_tool")
def tavily_web_search_tool(query: str) -> str:
    """
    Search the web using Tavily and return top sources.

    Args:
        query: Claim or keywords that need external verification.
    """
    results = tavily_web_search(query=query, max_results=5)
    return json.dumps(results)
