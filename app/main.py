from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.db.mongo import create_mongo_client, ensure_mongo_connection, get_mongo_collection
from app.integrations.appwrite_storage import (
    create_appwrite_storage,
    ensure_appwrite_connection,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_client = create_mongo_client()
    mongo_collection = get_mongo_collection(mongo_client)
    appwrite_storage = create_appwrite_storage()

    await ensure_mongo_connection(mongo_client)
    await ensure_appwrite_connection(appwrite_storage)

    app.state.mongo_client = mongo_client
    app.state.mongo_collection = mongo_collection
    app.state.appwrite_storage = appwrite_storage
    yield
    await mongo_client.close()


app = FastAPI(title="ClearView Backend", version="2.0", lifespan=lifespan)
app.include_router(router)

