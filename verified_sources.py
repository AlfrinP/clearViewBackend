"""
Verified source APIs for fact-checking and news verification.
One async function per source; each returns JSON-friendly data or raises on failure.
"""

import os
from typing import Any

import httpx

# ---------------------------------------------------------------------------
# NewsAPI — https://newsapi.org/docs
# Requires: NEWSAPI_KEY in .env
# ---------------------------------------------------------------------------


async def fetch_newsapi(query: str, *, page_size: int = 20, language: str = "en") -> dict[str, Any]:
    """
    Fetch news articles from NewsAPI (v2 everything endpoint).
    Set NEWSAPI_KEY in .env. Returns articles list and total count.
    """
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise ValueError("NEWSAPI_KEY is not set in environment")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "pageSize": min(page_size, 100),
        "language": language,
        "sortBy": "relevancy",
        "apiKey": api_key,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# GDELT — Global Database of Events, Language, and Tone
# DOC 2.0 full-text search; no key required for basic usage
# ---------------------------------------------------------------------------


async def fetch_gdelt(query: str, *, timespan: str = "3m", max_records: int = 25) -> dict[str, Any]:
    """
    Fetch news/events from GDELT DOC 2.0 full-text search API.
    timespan: e.g. "3m" (3 months) or "1y" (1 year). Returns article list and metadata.
    """
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": query,
        "mode": "artlist",
        "maxrecords": max_records,
        "format": "json",
        "timespan": timespan,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Wikipedia — MediaWiki REST API / Action API
# No API key. Set User-Agent as per Wikimedia guidelines.
# ---------------------------------------------------------------------------


async def fetch_wikipedia(query: str, *, limit: int = 10, lang: str = "en") -> dict[str, Any]:
    """
    Search Wikipedia via MediaWiki Action API (opensearch).
    lang: wiki language code (e.g. "en", "hi"). Returns search results with titles and snippets.
    """
    base = f"https://{lang}.wikipedia.org"
    url = f"{base}/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": limit,
        "format": "json",
        "origin": "*",
    }
    headers = {
        "User-Agent": "FakeNewsBackend/1.0 (fact-checking; https://github.com/your-repo)",
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()
