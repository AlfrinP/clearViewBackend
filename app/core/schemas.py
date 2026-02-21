"""Pydantic schemas for API request/response."""
from pydantic import BaseModel, Field


class SourceRef(BaseModel):
    """Reference to a source used in verification."""
    title: str | None = None
    url: str | None = None
    snippet: str | None = None
    domain: str | None = None
    trust_score: float | None = None


class VerificationRequest(BaseModel):
    """Request body for verification endpoint."""
    claim: str = Field(..., description="The claim to verify")


class VerificationResponse(BaseModel):
    """Structured verification result."""
    claim: str
    verdict: str = Field(..., description="TRUE | FALSE | PARTIALLY_TRUE | UNVERIFIABLE")
    confidence: float = Field(..., ge=0, le=1)
    policy_sources: list[SourceRef] = Field(default_factory=list)
    external_sources: list[SourceRef] = Field(default_factory=list)
    reasoning: str
    conflicts_found: bool = False


class IngestRequest(BaseModel):
    """Request body for ingestion endpoint."""
    file_path: str = Field(..., description="Path to PDF/DOCX file relative to project root")


class IngestResponse(BaseModel):
    """Response from ingestion endpoint."""
    status: str = Field(..., description="success | error")
    documents_ingested: int = 0
    message: str = ""


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    mongodb: str = "unknown"
    serper_key_set: bool = False
