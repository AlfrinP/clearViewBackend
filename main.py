from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI

from appwriteClient import ensure_appwrite_connection
from monogoDb import ensure_mongo_connection
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_mongo_connection()
    await ensure_appwrite_connection()
    print("App started")
    yield
    print("App shutting down")


app = FastAPI(title="ClearView Backend", version="2.0", lifespan=lifespan)
app.include_router(router)
