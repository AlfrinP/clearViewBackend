import json
import re

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from models import llm
from rag.vectorDb import vector_store
from webScraping import get_web_content

app = FastAPI()


class VerifyNewsRequest(BaseModel):
    news: str = Field(..., min_length=1, description="News article or claim text.")


def _safe_json(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


def _retrieve_rag_evidence(news: str) -> list[dict]:
    rag_evidence = []
    try:
        docs_scores = vector_store.similarity_search_with_relevance_scores(news, k=2)
        for doc, score in docs_scores:
            rag_evidence.append(
                {
                    "claim": news[:180],
                    "passage": doc.page_content[:300],
                    "source": str(doc.metadata.get("source", doc.metadata)),
                    "similarity_score": float(max(0.0, min(1.0, score))),
                }
            )
    except Exception:
        docs = vector_store.similarity_search(news, k=2)
        for doc in docs:
            rag_evidence.append(
                {
                    "claim": news[:180],
                    "passage": doc.page_content[:300],
                    "source": str(doc.metadata.get("source", doc.metadata)),
                    "similarity_score": 0.0,
                }
            )
    return rag_evidence


def _retrieve_web_evidence(news: str) -> list[dict]:
    web_raw = get_web_content(news)
    return [
        {
            "title": "Web verification summary",
            "content": str(web_raw)[:500],
            "url": "",
        }
    ]


def _build_verdict(news: str, rag_evidence: list[dict], web_sources: list[dict]) -> dict:
    prompt = (
        "You are a fake-news verification assistant.\n"
        "Classify the claim as Real, Fake, or Uncertain using the provided evidence.\n"
        "Return strict JSON only with keys: classification, confidence, reasoning.\n"
        "Keep reasoning under 80 words and confidence between 0 and 1.\n\n"
        f"Claim:\n{news}\n\n"
        f"RAG Evidence:\n{json.dumps(rag_evidence, ensure_ascii=False)}\n\n"
        f"Web Evidence:\n{json.dumps(web_sources, ensure_ascii=False)}"
    )
    raw = llm.invoke(prompt).content
    parsed = _safe_json(raw)
    if not parsed:
        return {
            "classification": "Uncertain",
            "confidence": 0.0,
            "reasoning": "Could not parse model verdict.",
        }
    return {
        "classification": parsed.get("classification", "Uncertain"),
        "confidence": float(parsed.get("confidence", 0.0) or 0.0),
        "reasoning": parsed.get("reasoning", ""),
    }


@app.post("/verify-news")
async def verify_news(payload: VerifyNewsRequest):
    news = payload.news.strip()
    if not news:
        raise HTTPException(status_code=400, detail="news must not be empty")

    rag_evidence = _retrieve_rag_evidence(news)
    web_sources = _retrieve_web_evidence(news)
    verdict = _build_verdict(news, rag_evidence, web_sources)

    return {
        "classification": verdict["classification"],
        "confidence": verdict["confidence"],
        "reasoning": verdict["reasoning"],
        "rag_evidence": rag_evidence,
        "web_sources": web_sources,
    }