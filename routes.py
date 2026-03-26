from __future__ import annotations

from fastapi import APIRouter, HTTPException

from dao.verification_dao import verify_claim
from dtos import VerifyNewsRequest, VerifyNewsResponse, VerifyNewsResultDTO

router = APIRouter()


@router.post("/verify-news", response_model=VerifyNewsResponse)
def verify_news(payload: VerifyNewsRequest) -> VerifyNewsResponse:
    try:
        final_state = verify_claim(payload.claim)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    evaluation = final_state.get("evaluation") or {}
    result = final_state.get("result") or {}

    return VerifyNewsResponse(
        claim=payload.claim,
        evaluation=evaluation,
        result=VerifyNewsResultDTO(**result) if isinstance(result, dict) else VerifyNewsResultDTO(),
    )
