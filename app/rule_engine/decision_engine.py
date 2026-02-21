"""Decision engine - orchestrate routing and verification."""
from app.core.schemas import SourceRef, VerificationResponse
from app.rule_engine.router import route_query
from app.sources.policy_rag import retrieve_policy_context
from app.sources.web_rag import fetch_web_evidence

from app.agents.policy_agent import policy_verify
from app.agents.web_agent import web_verify
from app.agents.fusion_agent import fusion_verify


def _to_source_refs(items: list[dict]) -> list[SourceRef]:
    return [
        SourceRef(
            title=it.get("title"),
            url=it.get("url"),
            snippet=it.get("snippet"),
            domain=it.get("domain"),
            trust_score=it.get("trust_score"),
        )
        for it in items
    ]


async def decision_engine(claim: str) -> VerificationResponse:
    """Route claim and run appropriate verification path."""
    category = route_query(claim)

    if category == "GOV_POLICY":
        policy_ctx = retrieve_policy_context(claim)
        result = await policy_verify(claim, policy_ctx)
        return VerificationResponse(
            claim=claim,
            verdict=result["verdict"],
            confidence=result["confidence"],
            policy_sources=_to_source_refs(policy_ctx),
            external_sources=[],
            reasoning=result["reasoning"],
            conflicts_found=False,
        )

    if category == "GENERAL_FACT":
        web_ctx = await fetch_web_evidence(claim)
        result = await web_verify(claim, web_ctx)
        return VerificationResponse(
            claim=claim,
            verdict=result["verdict"],
            confidence=result["confidence"],
            policy_sources=[],
            external_sources=_to_source_refs(web_ctx),
            reasoning=result["reasoning"],
            conflicts_found=False,
        )

    # BOTH
    policy_ctx = retrieve_policy_context(claim)
    web_ctx = await fetch_web_evidence(claim)
    result = await fusion_verify(claim, policy_ctx, web_ctx)
    return VerificationResponse(
        claim=claim,
        verdict=result["verdict"],
        confidence=result["confidence"],
        policy_sources=_to_source_refs(policy_ctx),
        external_sources=_to_source_refs(web_ctx),
        reasoning=result["reasoning"],
        conflicts_found=result.get("conflicts_found", False),
    )
