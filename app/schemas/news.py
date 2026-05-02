from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VerifyNewsRequest(BaseModel):
    claim: str = Field(
        min_length=1,
        description="The factual claim or news statement to verify.",
        examples=["NASA confirmed liquid water on the surface of Mars in 2025."],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "claim": "NASA confirmed liquid water on the surface of Mars in 2025.",
            }
        }
    )


class ExternalSource(BaseModel):
    """Metadata for a single external (web search) evidence item."""

    title: str | None = Field(
        default=None,
        description="Title of the external source / article.",
        examples=["NASA Mars Exploration Program: 2025 Update"],
    )
    url: str | None = Field(
        default=None,
        description="Canonical URL of the external source.",
        examples=["https://mars.nasa.gov/news/2025-update"],
    )
    description: str | None = Field(
        default=None,
        description=(
            "Short snippet / extracted content from the source that was provided "
            "to the LLM as evidence."
        ),
        examples=[
            "NASA scientists released a 2025 report summarising findings on "
            "subsurface water signatures observed by the Perseverance rover..."
        ],
    )
    score: float | None = Field(
        default=None,
        description=(
            "Relevance score returned by the search provider (higher = more "
            "relevant). May be null if the provider does not supply one."
        ),
        examples=[0.87],
    )
    published_date: str | None = Field(
        default=None,
        description="Publication date as reported by the source, if available.",
        examples=["2025-08-14"],
    )


class VerifyNewsEvaluationDTO(BaseModel):
    """Internal-evidence evaluation produced before optional external search."""

    verdict: str | None = Field(
        default=None,
        description="One of: supported | refuted | insufficient.",
        examples=["insufficient"],
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Model confidence in the internal-evidence verdict (0-1).",
        examples=[0.42],
    )
    needs_external_search: bool | None = Field(
        default=None,
        description=(
            "Whether the orchestrator decided to fall back to an external web "
            "search after evaluating the internal evidence."
        ),
        examples=[True],
    )
    evidence_strength: str | None = Field(
        default=None,
        description="One of: weak | moderate | strong.",
        examples=["weak"],
    )
    reason: str | None = Field(
        default=None,
        description="Detailed, evidence-grounded explanation of the verdict.",
    )


class VerifyNewsResultDTO(BaseModel):
    """Final synthesized verdict combining internal + external evidence."""

    final_verdict: str | None = Field(
        default=None,
        description="One of: True | False | Misleading | Not enough information.",
        examples=["Misleading"],
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Final model confidence (0-1) in the synthesized verdict.",
        examples=[0.66],
    )
    justification: str | None = Field(
        default=None,
        description=(
            "Detailed reasoning for the final verdict. Cites the specific "
            "internal and/or external evidence the verdict is based on."
        ),
    )
    sources_used: list[str] = Field(
        default_factory=list,
        description=(
            "Which evidence channels actually contributed to the verdict. "
            "Allowed values: 'internal', 'external'. Empty if neither contributed."
        ),
        examples=[["internal", "external"]],
    )


class VerifyNewsResponse(BaseModel):
    """Response payload for the /verify-news endpoint."""

    claim: str = Field(
        description="The original claim that was submitted for verification.",
    )
    evaluation: VerifyNewsEvaluationDTO = Field(
        default_factory=VerifyNewsEvaluationDTO,
        description=(
            "Result of the first-pass evaluation against internal evidence "
            "only (before any external search)."
        ),
    )
    result: VerifyNewsResultDTO = Field(
        default_factory=VerifyNewsResultDTO,
        description="Final synthesized verdict using all available evidence.",
    )
    external_sources: list[ExternalSource] = Field(
        default_factory=list,
        description=(
            "Metadata for every external (web search) source that was "
            "retrieved and provided to the LLM as evidence. Empty when the "
            "internal evidence was sufficient and no external search was run."
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "claim": "NASA confirmed liquid water on the surface of Mars in 2025.",
                "evaluation": {
                    "verdict": "insufficient",
                    "confidence": 0.4,
                    "needs_external_search": True,
                    "evidence_strength": "weak",
                    "reason": "Internal documents do not directly address the 2025 NASA announcement.",
                },
                "result": {
                    "final_verdict": "Misleading",
                    "confidence": 0.66,
                    "justification": (
                        "External source [1] states NASA reported subsurface water "
                        "signatures, not confirmed surface liquid water. The claim "
                        "overstates the announcement..."
                    ),
                    "sources_used": ["external"],
                },
                "external_sources": [
                    {
                        "title": "NASA Mars Exploration Program: 2025 Update",
                        "url": "https://mars.nasa.gov/news/2025-update",
                        "description": (
                            "NASA scientists released a 2025 report summarising "
                            "findings on subsurface water signatures observed by "
                            "the Perseverance rover..."
                        ),
                        "score": 0.87,
                        "published_date": "2025-08-14",
                    }
                ],
            }
        }
    )


# Backwards-compat: some callers may still import the old loose type.
VerifyNewsEvaluation = VerifyNewsEvaluationDTO

__all__ = [
    "ExternalSource",
    "VerifyNewsEvaluationDTO",
    "VerifyNewsRequest",
    "VerifyNewsResponse",
    "VerifyNewsResultDTO",
]


# Type re-export for any callers that previously typed evaluation as a dict.
EvaluationDictType = dict[str, Any]
