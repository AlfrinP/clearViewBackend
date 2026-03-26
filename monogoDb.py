from pymongo import AsyncMongoClient
from env import MONGO_URI
from env import MONGO_DB_NAME
from env import MONGODB_COLLECTION
import pymongo


client = AsyncMongoClient(
    MONGO_URI,
    server_api=pymongo.server_api.ServerApi(
        version="1", strict=True, deprecation_errors=True
    ),
)
db = client.get_database(MONGO_DB_NAME)
collection = db.get_collection(MONGODB_COLLECTION)


async def ensure_mongo_connection() -> None:
    try:
        await client.admin.command("ping")
    except Exception as e:
        raise RuntimeError(
            "MongoDB connection check failed. Verify MONGO_URI and network access."
        ) from e
