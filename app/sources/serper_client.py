"""Serper API client for Google Search."""
import os
from typing import Any

import httpx

SERPER_BASE_URL = "https://google.serper.dev/search"


async def serper_search(
    query: str,
    *,
    num: int = 10,
    site: str | None = None,
) -> dict[str, Any]:
    """
    Search Google via Serper API.
    If site is provided, restricts to that domain (e.g. who.int).
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        raise ValueError("SERPER_API_KEY is not set in environment")

    search_query = f"site:{site} {query}" if site else query

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            SERPER_BASE_URL,
            json={"q": search_query, "num": num},
            headers={"X-Api-Key": api_key},
        )
        resp.raise_for_status()
        return resp.json()
