import json
import logging
import re
from typing import TypedDict

from env import TAVILY_API_KEY
from tavily import TavilyClient
from crewai.tools import tool

logger = logging.getLogger(__name__)
MAX_SOURCE_COUNT = 3
MAX_CONTENT_CHARS = 400


class WebSearchResult(TypedDict):
    title: str
    content: str
    url: str


def _clean_content(text: str) -> str:
    text = text.replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    # Remove repeated boilerplate that bloats tokens.
    for token in ["Advertisement", "By Category", "[...]", "## By Category"]:
        text = text.replace(token, "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _get_tavily_client() -> TavilyClient | None:
    if not TAVILY_API_KEY:
        logger.warning("TAVILY_API_KEY is not set; web search will return no results.")
        return None
    if TavilyClient is None:
        logger.exception("tavily-python is not installed; web search unavailable.")
        return None
    return TavilyClient(api_key=TAVILY_API_KEY)


def tavily_web_search(query: str, max_results: int = MAX_SOURCE_COUNT) -> list[WebSearchResult]:
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
    seen_keys: set[tuple[str, str]] = set()
    for item in raw_results:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        key = (title.lower(), url.lower())
        if key in seen_keys:
            continue
        seen_keys.add(key)

        content = _clean_content(str(item.get("content", "")))
        cleaned.append(
            {"title": title, "content": content[:MAX_CONTENT_CHARS], "url": url}
        )
        if len(cleaned) >= max_results:
            break

    logger.debug("Tavily web search returned %s result(s).", len(cleaned))
    return cleaned


@tool("tavily_web_search_tool")
def tavily_web_search_tool(query: str) -> str:
    """
    Search the web using Tavily and return top sources.

    Args:
        query: Claim or keywords that need external verification.
    """
    results = tavily_web_search(query=query, max_results=MAX_SOURCE_COUNT)
    return json.dumps(results)
