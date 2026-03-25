evaluation_prompt = """You are a fact verification system.

Claim:
{claim}

Internal Evidence:
{documents}

Tasks:
1. Determine if the evidence SUPPORTS, REFUTES, or is INSUFFICIENT.
2. Decide if more external information is needed.

Return ONLY valid JSON:

{
  "verdict": "supported | refuted | insufficient",
  "confidence": 0 to 1,
  "needs_external_search": true or false,
  "evidence_strength": "weak | moderate | strong",
  "reason": "short explanation"
}
"""


final_verdict_prompt = """
Claim:
{claim}

Internal Evidence:
{internal_docs}

External Evidence:
{external_docs}

Task:
Classify the claim as:
- True
- False
- Misleading
- Not enough information

Return JSON:
{
  "final_verdict": "...",
  "confidence": 0-1,
  "justification": "clear reasoning",
  "sources_used": ["internal", "external"]
}

"""
