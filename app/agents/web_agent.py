"""Web-only verification agent."""
from app.agents.policy_agent import _parse_verification_response
from app.models.llm import llm

WEB_PROMPT = """You are a fact-checking assistant. Verify the claim using ONLY the evidence from verified sources (WHO, UN, Reuters).

Claim to verify: {claim}

Evidence from verified web sources:
{context}

Task: Verify the claim using ONLY the evidence above. Provide:
1. Verdict: TRUE, FALSE, PARTIALLY_TRUE, or UNVERIFIABLE
2. Confidence: a number between 0 and 1
3. Reasoning: brief explanation citing the sources

Format your response exactly as:
VERDICT: <verdict>
CONFIDENCE: <number>
REASONING: <your reasoning>"""


async def web_verify(claim: str, web_context: list[dict]) -> dict:
    """Verify claim using web context only."""
    context_str = "\n\n".join(
        f"[{c.get('title', 'Source')} - {c.get('url', '')}] {c.get('snippet', '')}"
        for c in web_context
    )
    prompt = WEB_PROMPT.format(claim=claim, context=context_str or "No web sources found.")
    response = await llm.ainvoke(prompt)
    text = (response.content or "").strip()
    return _parse_verification_response(text)
