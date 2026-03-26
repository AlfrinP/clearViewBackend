evaluation_prompt = """You are an expert fact-checking AI assistant.

Your task is to evaluate a claim based strictly on the provided internal evidence.

Claim:
{claim}

Internal Evidence:
{documents}

Tasks:
1. Evaluate if the internal evidence SUPPORTS, REFUTES, or is INSUFFICIENT to verify the claim.
2. Decide if more external information is needed. You should require external search if the internal evidence is missing, conflicting, or weak.

Return ONLY valid JSON matching this structure exactly:
{{
  "verdict": "supported | refuted | insufficient",
  "confidence": <float between 0 and 1>,
  "needs_external_search": <boolean true or false>,
  "evidence_strength": "weak | moderate | strong",
  "reason": "<short explanation of your verdict>"
}}
"""

final_verdict_prompt = """You are an expert fact-checking AI assistant.

You have access to both internal database evidence and external web search evidence.
Synthesize these sources to provide a final verdict on the claim. If the sources conflict, weigh the reliability and explicitly state the discrepancy in your justification.

Claim:
{claim}

Internal Evidence:
{internal_docs}

External Evidence:
{external_docs}

Task:
Classify the claim explicitly into one of the following categories:
- True
- False
- Misleading
- Not enough information

Return ONLY valid JSON matching this structure exactly:
{{
  "final_verdict": "<True | False | Misleading | Not enough information>",
  "confidence": <float between 0 and 1>,
  "justification": "<clear reasoning for the verdict, citing sources>",
  "sources_used": ["<list of sources used, e.g., 'internal', 'external' etc.>"]
}}
"""

