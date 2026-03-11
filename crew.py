import json
import logging
import re
from typing import Any

from env import GROQ_API_KEY, MOCK_PIPELINE, RAG_SIMILARITY_THRESHOLD

from crewai import Crew, Process

from agents.decision_agent import decision_agent
from agents.evaluation_agent import evaluation_agent
from agents.input_agent import input_agent
from agents.rag_agent import rag_agent
from agents.web_search_agent import web_search_agent
from tasks.analyze_sentiment import create_web_search_task
from tasks.extract_information import create_extract_information_task
from tasks.produce_final_result import create_produce_final_result_task
from tasks.retrieve_evidence import create_retrieve_evidence_task
from tasks.verify_facts import create_verify_facts_task

logger = logging.getLogger(__name__)


def _task_output_to_text(task_output: Any) -> str:
    if task_output is None:
        return ""
    if hasattr(task_output, "raw") and task_output.raw:
        return str(task_output.raw)
    if hasattr(task_output, "output") and task_output.output:
        return str(task_output.output)
    return str(task_output)


def _safe_json(text: str) -> dict:
    text = text.strip()
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


def _normalize_web_sources(raw_sources: Any) -> list[dict]:
    if not isinstance(raw_sources, list):
        return []

    normalized: list[dict] = []
    for source in raw_sources:
        if not isinstance(source, dict):
            continue
        normalized.append(
            {
                "title": str(source.get("title", "")).strip(),
                "content": str(
                    source.get(
                        "content",
                        source.get("snippet", source.get("summary", "")),
                    )
                ).strip(),
                "url": str(source.get("url", "")).strip(),
            }
        )
    return normalized


def _default_decision_payload(reasoning: str) -> dict:
    return {
        "classification": "Uncertain",
        "confidence": 0.0,
        "reasoning": reasoning,
        "rag_evidence": [],
        "web_sources": [],
    }


def _partial_decision_payload(reasoning: str, web_sources: list[dict]) -> dict:
    return {
        "classification": "Uncertain",
        "confidence": 0.2 if web_sources else 0.0,
        "reasoning": reasoning,
        "rag_evidence": [],
        "web_sources": web_sources,
    }


def _mock_result(news_text: str) -> dict:
    fake_markers = [
        "cures covid",
        "miracle cure",
        "secret government",
        "100% guaranteed",
    ]
    sufficient_markers = [
        "reuters reports",
        "who states",
        "cdc confirms",
        "peer reviewed study",
    ]
    lowered = news_text.lower()
    is_likely_fake = any(marker in lowered for marker in fake_markers)
    rag_sufficient = any(marker in lowered for marker in sufficient_markers)
    classification = "Fake" if is_likely_fake else "Uncertain"
    confidence = 0.82 if is_likely_fake else 0.55
    web_sources = (
        []
        if rag_sufficient
        else [
            {
                "title": "Mock Source",
                "url": "https://example.com/mock-source",
                "content": (
                    "Mock web evidence used because RAG similarity was " "insufficient."
                ),
            }
        ]
    )
    return {
        "classification": classification,
        "confidence": confidence,
        "reasoning": (
            "Mock pipeline result. "
            + (
                "RAG evidence treated as sufficient."
                if rag_sufficient
                else "RAG evidence treated as insufficient; web fallback applied."
            )
        ),
        "rag_evidence": [
            {
                "claim": news_text[:120],
                "passage": "Mock local evidence passage.",
                "source": "mock://local-rag",
                "similarity_score": 0.81 if rag_sufficient else 0.42,
            }
        ],
        "web_sources": web_sources,
    }


def run_fake_news_pipeline(news_text: str) -> dict:
    logger.info("Starting fake-news pipeline.")
    if MOCK_PIPELINE:
        logger.info("MOCK_PIPELINE enabled. Returning mock result.")
        return _mock_result(news_text)

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is required unless MOCK_PIPELINE=true.")

    logger.info("Creating initial tasks: extract -> retrieve -> verify")
    extract_task = create_extract_information_task(input_agent, news_text)
    retrieve_task = create_retrieve_evidence_task(
        rag_agent,
        news_text,
        extract_task,
    )
    verify_task = create_verify_facts_task(evaluation_agent, retrieve_task)

    logger.info(
        "Launching initial crew with agents: %s",
        [input_agent.role, rag_agent.role, evaluation_agent.role],
    )
    initial_crew = Crew(
        agents=[input_agent, rag_agent, evaluation_agent],
        tasks=[extract_task, retrieve_task, verify_task],
        process=Process.sequential,
        verbose=False,
    )
    initial_result = initial_crew.kickoff()
    logger.info("Initial crew completed.")

    initial_outputs = getattr(initial_result, "tasks_output", [])
    retrieve_json = _safe_json(
        _task_output_to_text(initial_outputs[1] if len(initial_outputs) > 1 else None)
    )
    verify_json = _safe_json(
        _task_output_to_text(initial_outputs[2] if len(initial_outputs) > 2 else None)
    )

    similarity_score = float(
        verify_json.get(
            "similarity_score", retrieve_json.get("max_similarity_score", 0.0)
        )
        or 0.0
    )
    rag_sufficient = verify_json.get("rag_sufficient")
    if rag_sufficient is None:
        rag_sufficient = similarity_score >= RAG_SIMILARITY_THRESHOLD
    logger.info(
        "Evidence routing decision: rag_sufficient=%s similarity_score=%.3f threshold=%.3f",
        rag_sufficient,
        similarity_score,
        RAG_SIMILARITY_THRESHOLD,
    )

    if rag_sufficient:
        logger.info("Skipping web search. Running decision agent with RAG evidence only.")
        decision_task = create_produce_final_result_task(decision_agent, [verify_task])
        decision_crew = Crew(
            agents=[decision_agent],
            tasks=[decision_task],
            process=Process.sequential,
            verbose=False,
        )
        decision_result = decision_crew.kickoff()
        logger.info("Decision-only crew completed.")
        final_output = getattr(decision_result, "tasks_output", [])
        logger.debug("Decision output raw=%r", final_output)
        decision_json = _safe_json(
            _task_output_to_text(final_output[0] if final_output else decision_result)
        )
        if not decision_json:
            logger.warning(
                "Decision agent output was unparsable. Returning default decision payload."
            )
            decision_json = _default_decision_payload(
                "Final decision agent returned unparsable output."
            )
        decision_json.setdefault("rag_evidence", retrieve_json.get("rag_evidence", []))
        decision_json.setdefault("web_sources", [])
        return decision_json

    logger.info("RAG evidence insufficient. Running web search fallback path.")
    web_task = create_web_search_task(web_search_agent, news_text, verify_task)
    decision_task = create_produce_final_result_task(
        decision_agent, [verify_task, web_task]
    )
    logger.info(
        "Launching fallback crew with agents: %s",
        [web_search_agent.role, decision_agent.role],
    )
    fallback_crew = Crew(
        agents=[web_search_agent, decision_agent],
        tasks=[web_task, decision_task],
        process=Process.sequential,
        verbose=False,
    )
    fallback_result = fallback_crew.kickoff()
    logger.info("Fallback crew completed.")
    fallback_outputs = getattr(fallback_result, "tasks_output", [])
    web_json = _safe_json(
        _task_output_to_text(fallback_outputs[0] if len(fallback_outputs) > 0 else None)
    )
    decision_json = _safe_json(
        _task_output_to_text(
            fallback_outputs[1] if len(fallback_outputs) > 1 else fallback_result
        )
    )
    if not decision_json:
        logger.warning(
            "Decision output after web search was unparsable. Using default payload."
        )
        raw_web_output = _task_output_to_text(
            fallback_outputs[0] if len(fallback_outputs) > 0 else None
        )
        raw_decision_output = _task_output_to_text(
            fallback_outputs[1] if len(fallback_outputs) > 1 else fallback_result
        )
        logger.error(
            "Unparsable fallback outputs. raw_web_output=%r raw_decision_output=%r",
            raw_web_output[:2000],
            raw_decision_output[:2000],
        )
        fallback_web_sources = _normalize_web_sources(web_json.get("web_sources", []))
        decision_json = _partial_decision_payload(
            (
                "Final decision agent returned unparsable output after web "
                "search. Returning partial result with retrieved web sources."
            ),
            fallback_web_sources,
        )
    decision_json.setdefault("rag_evidence", retrieve_json.get("rag_evidence", []))
    web_sources = _normalize_web_sources(web_json.get("web_sources", []))
    decision_json.setdefault("web_sources", web_sources)
    logger.info("Pipeline finished. web_sources_count=%d", len(web_sources))
    return decision_json
