from typing import Any

from pydantic import BaseModel, Field


class VerifyNewsRequest(BaseModel):
    claim: str = Field(min_length=1, description="The claim to verify")


class VerifyNewsResultDTO(BaseModel):
    final_verdict: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    justification: str | None = None
    sources_used: list[str] = Field(default_factory=list)


class VerifyNewsResponse(BaseModel):
    claim: str
    evaluation: dict[str, Any] = Field(default_factory=dict)
    result: VerifyNewsResultDTO = Field(default_factory=VerifyNewsResultDTO)

