from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.db.mongo import (
    create_mongo_client,
    ensure_mongo_connection,
    get_mongo_collection,
)
from app.integrations.appwrite_storage import (
    create_appwrite_storage,
    ensure_appwrite_connection,
)
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_client = create_mongo_client()
    mongo_collection = get_mongo_collection(mongo_client)
    appwrite_storage = create_appwrite_storage()

    await ensure_mongo_connection(mongo_client)
    ensure_appwrite_connection(appwrite_storage)

    app.state.mongo_client = mongo_client
    app.state.mongo_collection = mongo_collection
    app.state.appwrite_storage = appwrite_storage
    yield
    await mongo_client.close()


app = FastAPI(
    title="ClearView Backend",
    version="2.0",
    lifespan=lifespan,
    description=(
        "ClearView is an evidence-grounded news / claim verification service.\n\n"
        "It evaluates a claim first against an internal vector store of "
        "trusted documents and, when that evidence is insufficient or weak, "
        "falls back to an external web search. Final verdicts are returned "
        "together with the supporting evidence — including full metadata for "
        "every external source that was used (title, URL, description, "
        "relevance score, and publication date)."
    ),
    openapi_tags=[
        {
            "name": "clearview-api",
            "description": (
                "Claim verification, file uploads, and evidence-store "
                "management endpoints."
            ),
        }
    ],
)
app.include_router(router)
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
