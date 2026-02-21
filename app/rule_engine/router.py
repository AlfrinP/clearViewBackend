"""LLM-based router for claim classification."""
from app.models.llm import llm

ROUTER_PROMPT = """Classify the user claim into ONE category:

1. GOV_POLICY → laws, schemes, regulations, government decisions, official policy
2. GENERAL_FACT → news, science, public claims, world events
3. BOTH → needs both government policy and external verified sources

Claim: {claim}

Return only the category: GOV_POLICY, GENERAL_FACT, or BOTH. Nothing else."""


def route_query(claim: str) -> str:
    """Classify claim and return GOV_POLICY, GENERAL_FACT, or BOTH."""
    prompt = ROUTER_PROMPT.format(claim=claim)
    response = llm.invoke(prompt)
    text = (response.content or "").strip().upper()
    if "GOV_POLICY" in text:
        return "GOV_POLICY"
    if "GENERAL_FACT" in text:
        return "GENERAL_FACT"
    if "BOTH" in text:
        return "BOTH"
    return "BOTH"  # default to both if unclear
