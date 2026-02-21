"""Fusion agent - combine policy and web evidence, detect conflicts."""
from app.agents.policy_agent import _parse_verification_response
from app.models.llm import llm

FUSION_PROMPT = """You are a verification judge. Compare government policy evidence with external verified sources.

Claim to verify: {claim}

Government Policy Evidence:
{policy_context}

External Verified Sources (WHO, UN, Reuters):
{web_context}

Task:
1. Compare both sources
2. Detect any contradictions between policy and web sources
3. Produce final verdict: TRUE, FALSE, PARTIALLY_TRUE, or UNVERIFIABLE
4. Confidence: 0-1
5. Reasoning: explain your conclusion and cite sources. Note if conflicts_found.

Format your response exactly as:
VERDICT: <verdict>
CONFIDENCE: <number>
CONFLICTS_FOUND: <true or false>
REASONING: <your reasoning>"""


async def fusion_verify(
    claim: str,
    policy_context: list[dict],
    web_context: list[dict],
) -> dict:
    """Verify claim using both policy and web context."""
    policy_str = "\n\n".join(
        f"[Policy] {c.get('snippet', '')}"
        for c in policy_context
    )
    web_str = "\n\n".join(
        f"[{c.get('title')} - {c.get('url')}] {c.get('snippet', '')}"
        for c in web_context
    )
    prompt = FUSION_PROMPT.format(
        claim=claim,
        policy_context=policy_str or "No policy documents.",
        web_context=web_str or "No web sources.",
    )
    response = await llm.ainvoke(prompt)
    text = (response.content or "").strip()
    result = _parse_verification_response(text)

    # Parse conflicts_found
    conflicts_found = False
    for line in text.split("\n"):
        if line.upper().startswith("CONFLICTS_FOUND:"):
            val = line.split(":", 1)[1].strip().lower()
            conflicts_found = val in ("true", "yes", "1")
            break
    result["conflicts_found"] = conflicts_found
    return result
