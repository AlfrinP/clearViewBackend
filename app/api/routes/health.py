"""Health check route."""
from typing import Annotated

from fastapi import APIRouter, Depends
from pymongo import MongoClient

from app.auth.jwt import User, get_current_active_user
from app.core.schemas import HealthResponse
from app.env import MONGODB_CONNECTION_STRING, SERPER_API_KEY

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> HealthResponse:
    """Health check - MongoDB and env vars."""
    mongodb_status = "unknown"
    if MONGODB_CONNECTION_STRING:
        try:
            client = MongoClient(
                MONGODB_CONNECTION_STRING, serverSelectionTimeoutMS=3000
            )
            client.admin.command("ping")
            mongodb_status = "connected"
        except Exception:
            mongodb_status = "disconnected"
    return HealthResponse(
        status="ok",
        mongodb=mongodb_status,
        serper_key_set=bool(SERPER_API_KEY),
    )
