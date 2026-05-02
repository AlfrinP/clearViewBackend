from __future__ import annotations

from typing import Any, TypedDict

from pydantic import BaseModel, Field

from app.ai import prompts
from app.ai.model_client import llm
from app.ai.tools import retrieve_context, web_search


class GraphState(TypedDict, total=False):
    claim: str
    internal_docs: str
    external_docs: str
    external_sources: list[dict[str, Any]]
    evaluation: dict
    result: dict


class Evaluation(BaseModel):
    verdict: str = Field(description="supported | refuted | insufficient")
    confidence: float = Field(description="0 to 1")
    needs_external_search: bool
    evidence_strength: str = Field(description="weak | moderate | strong")
    reason: str = Field(description="short explanation")


class FinalVerdict(BaseModel):
    final_verdict: str = Field(
        description="True | False | Misleading | Not enough information"
    )
    confidence: float = Field(description="0 to 1")
    justification: str = Field(description="clear reasoning")
    sources_used: list[str] = Field(
        description="sources used, e.g. ['internal', 'external']"
    )


def should_search_more(state: GraphState) -> str:
    result = state.get("evaluation", {})
    if result.get("verdict") == "insufficient":
        return "external"
    if result.get("confidence", 1.0) < 0.65:
        return "external"
    if result.get("evidence_strength") == "weak":
        return "external"
    return "final"


def internal_retrieval(state: GraphState) -> dict:
    docs = retrieve_context.invoke({"query": state["claim"]})
    if isinstance(docs, tuple):
        docs = docs[0]
    return {"internal_docs": docs}


def evaluate(state: GraphState) -> dict:
    structured_llm = llm.with_structured_output(Evaluation)
    response = structured_llm.invoke(
        prompts.evaluation_prompt.format(
            claim=state["claim"], documents=state.get("internal_docs", "")
        )
    )
    return {"evaluation": response.model_dump()}


def _normalize_external_results(raw: Any) -> list[dict[str, Any]]:
    """Normalize Tavily / web-search output into a list of source dicts.

    Tavily returns a dict shaped like:
        {"query": ..., "answer": ..., "results": [{title, url, content, score, ...}, ...]}
    but we defensively handle strings, lists and missing keys.
    """
    if raw is None:
        return []

    if isinstance(raw, dict):
        results = raw.get("results") or raw.get("data") or []
    elif isinstance(raw, list):
        results = raw
    else:
        return []

    normalized: list[dict[str, Any]] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "description": item.get("content") or item.get("snippet"),
                "score": item.get("score"),
                "published_date": item.get("published_date"),
            }
        )
    return normalized


def _format_external_for_llm(sources: list[dict[str, Any]]) -> str:
    """Render structured external sources into a clean string for the prompt."""
    if not sources:
        return ""
    lines: list[str] = []
    for idx, src in enumerate(sources, start=1):
        title = src.get("title") or "Untitled"
        url = src.get("url") or "n/a"
        description = src.get("description") or ""
        lines.append(
            f"[{idx}] Title: {title}\n    URL: {url}\n    Content: {description}"
        )
    return "\n\n".join(lines)


def external_retrieval(state: GraphState) -> dict:
    raw = web_search.invoke({"query": state["claim"]})
    sources = _normalize_external_results(raw)
    return {
        "external_docs": _format_external_for_llm(sources),
        "external_sources": sources,
    }


def final_answer(state: GraphState) -> dict:
    structured_llm = llm.with_structured_output(FinalVerdict)
    response = structured_llm.invoke(
        prompts.final_verdict_prompt.format(
            claim=state["claim"],
            internal_docs=state.get("internal_docs", ""),
            external_docs=state.get("external_docs", ""),
        )
    )
    return {"result": response.model_dump()}
