"""External Web RAG - Serper API restricted to trusted domains."""
import os

from app.core.config import ALLOWED_EXTERNAL_DOMAINS, SOURCE_WEIGHTS
from app.sources.serper_client import serper_search


async def fetch_web_evidence(query: str, *, max_results: int = 15) -> list[dict]:
    """
    Fetch evidence from Serper, restricted to who.int, un.org, reuters.com.
    Returns list of {title, snippet, url, domain, trust_score} sorted by trust.
    """
    if not os.getenv("SERPER_API_KEY"):
        return []

    all_results: list[dict] = []

    for domain in ALLOWED_EXTERNAL_DOMAINS:
        try:
            data = await serper_search(query, num=5, site=domain)
            organic = data.get("organic", [])
            for r in organic:
                link = r.get("link", "")
                if domain in link:
                    all_results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("snippet", ""),
                        "url": link,
                        "domain": domain,
                        "trust_score": SOURCE_WEIGHTS.get(domain, 0.5),
                    })
        except Exception:
            continue

    # Sort by trust_score descending
    all_results.sort(key=lambda x: x["trust_score"], reverse=True)
    return all_results[:max_results]
