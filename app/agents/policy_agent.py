"""Policy-only verification agent."""
from app.models.llm import llm

POLICY_PROMPT = """You are a fake news detection assistant focused on government policy, laws, and regulations.

Claim to verify: {claim}

Evidence from government policy documents:
{context}

Task: Verify the claim using ONLY the evidence above. Provide:
1. Verdict: TRUE, FALSE, PARTIALLY_TRUE, or UNVERIFIABLE
2. Confidence: a number between 0 and 1
3. Reasoning: brief explanation citing the evidence

Format your response exactly as:
VERDICT: <verdict>
CONFIDENCE: <number>
REASONING: <your reasoning>"""


async def policy_verify(claim: str, policy_context: list[dict]) -> dict:
    """Verify claim using policy context only."""
    context_str = "\n\n".join(
        f"[{c.get('title', 'Source')}] {c.get('snippet', '')}"
        for c in policy_context
    )
    prompt = POLICY_PROMPT.format(claim=claim, context=context_str or "No policy documents found.")
    response = await llm.ainvoke(prompt)
    text = (response.content or "").strip()
    return _parse_verification_response(text)


def _parse_verification_response(text: str) -> dict:
    """Parse LLM response into verdict, confidence, reasoning."""
    verdict = "UNVERIFIABLE"
    confidence = 0.5
    reasoning = text

    for line in text.split("\n"):
        line = line.strip()
        if line.upper().startswith("VERDICT:"):
            v = line.split(":", 1)[1].strip().upper()
            if v in ("TRUE", "FALSE", "PARTIALLY_TRUE", "UNVERIFIABLE"):
                verdict = v
        elif line.upper().startswith("CONFIDENCE:"):
            try:
                c = float(line.split(":", 1)[1].strip())
                confidence = max(0, min(1, c))
            except ValueError:
                pass
        elif line.upper().startswith("REASONING:"):
            reasoning = line.split(":", 1)[1].strip()

    return {"verdict": verdict, "confidence": confidence, "reasoning": reasoning}
