from __future__ import annotations

from typing import Any

from verification_graph import verification_graph


def verify_claim(claim: str) -> dict[str, Any]:
    initial_state: dict[str, Any] = {
        "claim": claim,
        "internal_docs": "",
        "external_docs": "",
        "evaluation": {},
        "result": {},
    }
    return verification_graph.invoke(initial_state)
