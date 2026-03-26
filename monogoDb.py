import pymongo
from fastapi import Request
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection

from env import MONGO_DB_NAME, MONGO_URI, MONGODB_COLLECTION


def create_mongo_client() -> AsyncMongoClient:
    return AsyncMongoClient(
        MONGO_URI,
        server_api=pymongo.server_api.ServerApi(
            version="1",
            strict=True,
            deprecation_errors=True,
        ),
    )


def get_mongo_collection(client: AsyncMongoClient) -> AsyncCollection:
    db = client.get_database(MONGO_DB_NAME)
    return db.get_collection(MONGODB_COLLECTION)


async def ensure_mongo_connection(client: AsyncMongoClient) -> None:
    try:
        await client.admin.command("ping")
    except Exception as e:
        raise RuntimeError(
            "MongoDB connection check failed. Verify MONGO_URI and network access."
        ) from e


async def mongo_collection_dependency(request: Request) -> AsyncCollection:
    return request.app.state.mongo_collection
