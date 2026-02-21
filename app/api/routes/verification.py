"""Verification API routes."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.auth.jwt import User, get_current_active_user
from app.core.schemas import VerificationRequest, VerificationResponse
from app.rule_engine.decision_engine import decision_engine

router = APIRouter(prefix="/api/v1", tags=["verification"])


@router.post("/verify", response_model=VerificationResponse)
async def verify_claim(
    req: VerificationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> VerificationResponse:
    """Verify a claim using hybrid policy + web RAG."""
    try:
        return await decision_engine(req.claim)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
