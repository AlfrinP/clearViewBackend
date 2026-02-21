"""Health check route."""

from fastapi import APIRouter

from app.env import MONGODB_CONNECTION_STRING, SERPER_API_KEY
from app.core.schemas import HealthResponse
from pymongo import MongoClient

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
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
