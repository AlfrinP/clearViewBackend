from typing import Any

from app.ai.graph import verification_graph


def verify_claim(claim: str) -> dict[str, Any]:
    initial_state: dict[str, Any] = {
        "claim": claim,
        "internal_docs": "",
        "external_docs": "",
        "external_sources": [],
        "evaluation": {},
        "result": {},
    }
    return verification_graph.invoke(initial_state)

