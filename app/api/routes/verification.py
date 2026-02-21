"""Verification API routes."""
from fastapi import APIRouter, HTTPException, Request

from app.core.schemas import VerificationRequest, VerificationResponse
from app.rule_engine.decision_engine import decision_engine

router = APIRouter(prefix="/api/v1", tags=["verification"])


@router.post("/verify", response_model=VerificationResponse)
async def verify_claim(req: VerificationRequest) -> VerificationResponse:
    """Verify a claim using hybrid policy + web RAG."""
    try:
        return await decision_engine(req.claim)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
